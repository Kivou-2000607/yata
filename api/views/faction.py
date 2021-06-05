"""
Copyright 2020 kivou.2000607@gmail.com

This file is part of yata.

    yata is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    yata is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with yata. If not, see <https://www.gnu.org/licenses/>.
"""
# django
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# cache and rate limit
from django.views.decorators.cache import cache_page
from ratelimit.decorators import ratelimit
from ratelimit.core import get_usage, is_ratelimited

# standards
import json
import numpy
from scipy import stats

# yata
from yata.handy import apiCall
from yata.handy import tsnow
from yata.handy import timestampToDate
from faction.models import Faction
from faction.models import Wall
from player.models import Player


@cache_page(60)
def livechain(request):
    try:
        # check if API key is valid with api call
        key = request.GET.get("key", False)
        if not key:
            return JsonResponse({"error": {"code": 2, "error": "No keys provided"}}, status=400)

        call = apiCall('faction', '', 'chain,basic', key=key)
        if "apiError" in call:
            return JsonResponse({"error": {"code": 4, "error": call["apiErrorString"]}}, status=400)

        # create basic payload
        payload = call["chain"]
        payload["faction_id"] = call["ID"]
        payload["faction_name"] = call["name"]

        #  check if can get faction
        factionId = call.get("ID", 0)
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            payload["yata"] = {"error": f"Can't find faction {factionId} in YATA database"}
            return JsonResponse({"chain": payload, "timestamp": tsnow()}, status=200)

        # get live report
        livechain = faction.chain_set.filter(tId=0, report=True).first()
        if livechain is None:
            # create tab
            livechain.report = True
            livechain.computing = True
            livechain.cooldown = False
            livechain.status = 1
            livechain.addToEnd = 10
            livechain.assignCrontab()
            livechain.save()

            payload["yata"] = {"error": f"Start computing live report for faction {factionId}"}
            return JsonResponse({"chain": payload, "timestamp": tsnow()}, status=200)

        graphs = json.loads(livechain.graphs)
        graphSplit = graphs.get("hits", "").split(',')
        graphSplitCrit = graphs.get("crit", "").split(',')
        graphSplitStat = graphs.get("members", "").split(',')
        if len(graphSplit) > 1 and len(graphSplitCrit) > 1:
            # compute average time for one bar
            bins = (int(graphSplit[-1].split(':')[0]) - int(graphSplit[0].split(':')[0])) / float(60 * (len(graphSplit) - 1))
            graph = {'hits': [], 'members': [], 'stats': {'bin_size': bins * 60, 'critical_hits_ratio': int(bins) / 5}}
            cummulativeHits = 0
            x = numpy.zeros(len(graphSplit))
            y = numpy.zeros(len(graphSplit))
            for i, (line, lineCrit) in enumerate(zip(graphSplit, graphSplitCrit)):
                splt = line.split(':')
                spltCrit = lineCrit.split(':')
                cummulativeHits += int(splt[1])
                graph['hits'].append([int(splt[0]), int(splt[1]), cummulativeHits, int(spltCrit[0]), int(spltCrit[1]), int(spltCrit[2])])
                x[i] = int(splt[0])
                y[i] = cummulativeHits

            #  y = ax + b (y: hits, x: timestamp)
            a, b, _, _, _ = stats.linregress(x[-2:], y[-2:])
            a = max(a, 0.00001)
            try:
                ETA = int((livechain.getNextBonus() - b) / a)
            except BaseException as e:
                ETA = "unable to compute EAT ({})".format(e)
            graph['stats']['current_eta'] = ETA
            graph['stats']['current_hit_rate'] = a
            graph['stats']['current_intercept'] = b

            a, b, _, _, _ = stats.linregress(x, y)
            try:
                ETA = int((livechain.getNextBonus() - b) / a)
            except BaseException as e:
                ETA = "unable to compute EAT ({})".format(e)
            graph['stats']['global_hit_rate'] = a
            graph['stats']['global_intercept'] = b

            if len(graphSplitStat) > 1:
                for line in graphSplitStat:
                    splt = line.split(':')
                    graph['members'].append([float(splt[0]), int(splt[1])])

            payload["yata"] = graph
            payload["yata"]["last"] = livechain.last
            payload["yata"]["update"] = livechain.update

        else:
            payload["yata"] = {"error": f"No enough data"}

        return JsonResponse({"chain": payload, "timestamp": tsnow()}, status=200)

    except BaseException as e:
        return JsonResponse({"error": {"code": 1, "error": str(e)}}, status=500)


@cache_page(60*10)
def getCrimes(request):
    try:
        # check if API key is valid with api call
        key = request.GET.get("key", False)
        if not key:
            return JsonResponse({"error": {"code": 2, "error": "No keys provided"}}, status=400)

        call = apiCall('user', '', '', key=key)
        if "apiError" in call:
            return JsonResponse({"error": {"code": 4, "error": call["apiErrorString"]}}, status=400)

        #  check if can get faction
        factionId = call.get("faction", {}).get("faction_id")
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            return JsonResponse({"error": {"code": 2, "error": f"Can't find faction {factionId} in YATA database"}}, status=400)

        # update crimes
        faction.updateCrimes()

        # get members
        members = {}
        for member in faction.member_set.all():
            if member.nnb:
                members[str(member.tId)] = {"NNB": member.nnb, "equivalent_arsons": member.arson, "ce_rank": member.crimesRank}
            else:
                members[str(member.tId)] = {"NNB": None, "equivalent_arsons": None, "ce_rank": member.crimesRank}

        return JsonResponse({"members": members, "timestamp": tsnow()}, status=200)

    except BaseException as e:
        return JsonResponse({"error": {"code": 1, "error": str(e)}}, status=500)


@csrf_exempt
def updateRanking(request):
    try:

        # check if API key is valid with api call
        key = request.GET.get("key", False)
        if not key:
            return JsonResponse({"error": {"code": 2, "error": "No keys provided"}}, status=400)

        # check if body contains sub_ranking
        payload = json.loads(request.body)
        sub_ranking = payload.get("sub_ranking")
        if sub_ranking is None:
            return JsonResponse({"error": {"code": 2, "error": "No sub ranking provided"}}, status=400)

        # insure its a list of ints
        if not isinstance(sub_ranking, list) and not all([str(_).isdigit() for _ in sub_ranking]):
            return JsonResponse({"error": {"code": 2, "error": "Sub ranking not well formated"}}, status=400)
        sub_ranking = [int(_) for _ in sub_ranking]

        # get faction ID
        call = apiCall('user', '', '', key=key)
        if "apiError" in call:
            return JsonResponse({"error": {"code": 4, "error": call["apiErrorString"]}}, status=400)

        #  check if can get faction
        factionId = call.get("faction", {}).get("faction_id")
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            return JsonResponse({"error": {"code": 2, "error": f"Can't find faction {factionId} in YATA database"}}, status=400)

        # update crimes
        faction.updateRanking([sub_ranking])

        return HttpResponse(status=200)

    except BaseException as e:
        return JsonResponse({"error": {"code": 1, "error": str(e)}}, status=500)


@csrf_exempt
def importWall(request):
    try:
        if request.method != 'POST':
            return JsonResponse({"error": {"code": 2, "error": "POST request needed"}}, status=400)

        req = json.loads(request.body)

        # get author
        authorId = req.get("author", 0)
        author = Player.objects.filter(tId=authorId).first()

        #  check if author is in YATA
        if author is None:
            return JsonResponse({"error": {"code": 2, "error": f"You're not register in YATA"}}, status=400)

        # check if API key is valid with api call
        HTTP_KEY = request.META.get("HTTP_KEY")
        call = apiCall('user', '', '', key=HTTP_KEY)
        if "apiError" in call:
            return JsonResponse({"error": {"code": 4, "error": call["apiErrorString"]}}, status=400)

        # check if API key sent == API key in YATA
        if HTTP_KEY != author.getKey():
            return JsonResponse({"error": {"code": 2, "error": "Your API key seems to be out of date in YATA, please log again"}}, status=400)


        #  check if AA of a faction
        if not author.factionAA:
            return JsonResponse({"error": {"code": 2, "error": "You don't have AA perm"}}, status=400)

        #  check if can get faction
        faction = Faction.objects.filter(tId=author.factionId).first()
        if faction is None:
            return JsonResponse({"error": {"code": 2, "error": f"Can't find faction {author.factionId} in YATA database"}}, status=400)

        attackers = dict({})
        defenders = dict({})
        i = 0
        for p in req.get("participants"):
            i += 1
            p = {k.split(" ")[0].strip(): v for k, v in p.items()}
            if p.get("Name")[0] == '=':
                p["Name"] = p["Name"][2:-1]
            if p.get("Position") in ["Attacker"]:
                attackers[p.get('XID')] = p
            else:
                defenders[p.get('XID')] = p

        if i > 500:
            return JsonResponse({"error": {"code": 2, "error": f"{i} is too many participants for a wall"}}, status=400)

        r = int(req.get('result', 0))
        if r == -1:
            result = "Timeout"
        elif r == 1:
            result = "Win"
        else:
            result = "Truce"

        wallDic = {'tId': int(req.get('id')),
                   'tss': int(req.get('ts_start')),
                   'tse': int(req.get('ts_end')),
                   'attackers': json.dumps(attackers),
                   'defenders': json.dumps(defenders),
                   'attackerFactionId': int(req.get('att_fac')),
                   'defenderFactionId': int(req.get('def_fac')),
                   'attackerFactionName': req.get('att_fac_name'),
                   'defenderFactionName': req.get('def_fac_name'),
                   'territory': req.get('terr'),
                   'result': result}

        if faction.tId not in [wallDic.get('attackerFactionId'), wallDic.get('defenderFactionId')]:
            return JsonResponse({"error": {"code": 2, "error": f"Faction {faction} is not involved in this war"}}, status=400)

        messageList = []
        wall = Wall.objects.filter(tId=wallDic.get('tId')).first()
        if wall is None:
            messageList.append("Wall {} created".format(wallDic.get('tId')))
            creation = True
            wall = Wall.objects.create(**wallDic)
        else:
            messageList.append("Wall {} modified".format(wallDic.get('tId')))
            wall.update(wallDic)

        if faction in wall.factions.all():
            messageList.append("wall already added to {}".format(faction))
        else:
            messageList.append("adding wall to {}".format(faction))
            wall.factions.add(faction)

        return JsonResponse({"message": ", ".join(messageList)}, status=200)

    except BaseException as e:
        return JsonResponse({"error": {"code": 1, "error": str(e)}}, status=500)
