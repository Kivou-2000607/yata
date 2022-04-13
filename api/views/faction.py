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
        livechain = faction.chain_set.filter(tId=0).first()
        if livechain is None:
            # chain not there (needs API call data)
            if payload["current"] < 10:
                pass

            livechain = faction.chain_set.create(
                    tId=0,
                    live=True,
                    chain=payload["current"],
                    start=payload["start"],
                    end=tsnow()
                )
            livechain.report = True
            livechain.computing = True
            livechain.cooldown = False
            livechain.status = 1
            livechain.addToEnd = 10
            livechain.assignCrontab()
            livechain.save()

            payload["yata"] = {"error": f"Start computing live report for faction {factionId}"}
            return JsonResponse({"chain": payload, "timestamp": tsnow()}, status=200)

        elif not livechain.report:
            # if chain already there but not started
            livechain.report = True
            livechain.live = True
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
