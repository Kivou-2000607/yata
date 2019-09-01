"""
Copyright 2019 kivou.2000607@gmail.com

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

from django.shortcuts import render
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from scipy import stats
import numpy
import json
import random
import os

from player.models import Player

from yata.handy import apiCall
from yata.handy import cleanhtml
from yata.handy import timestampToDate
from yata.handy import returnError

from chain.functions import updateMembers
from chain.functions import factionTree
from chain.functions import BONUS_HITS

from chain.models import Faction
from chain.models import Preference
from chain.models import Crontab
from chain.models import Wall


# render view
def index(request):
    try:
        if request.session.get('player'):
            print('[view.chain.index] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            key = player.key

            # get user info
            user = apiCall('user', '', 'profile', key)
            if 'apiError' in user:
                context = {'player': player, 'apiError': user["apiError"] + " We can't check your faction so you don't have access to this section."}
                player.chainInfo = "N/A"
                player.factionId = 0
                player.factionNa = "-"
                player.factionAA = False
                # player.lastUpdateTS = int(timezone.now().timestamp())
                player.save()
                return render(request, 'chain.html', context)

            factionId = int(user.get("faction")["faction_id"])
            preferences = Preference.objects.first()
            allowedFactions = json.loads(preferences.allowedFactions) if preferences is not None else []
            print("[view.chain.index] allowedFactions: {}".format(allowedFactions))
            # if str(factionId) in allowedFactions:
            if True:
                player.chainInfo = user.get("faction")["faction_name"]
                player.factionNa = user.get("faction")["faction_name"]
                player.factionId = factionId
                if 'chains' in apiCall('faction', factionId, 'chains', key):
                    player.chainInfo += " [AA]"
                    player.factionAA = True
                else:
                    player.factionAA = False
                # player.lastUpdateTS = int(timezone.now().timestamp())
                player.save()
                print('[view.chain.index] player in faction {}'.format(player.chainInfo))
            else:
                print('[view.chain.index] player in non registered faction {}'.format(user.get("faction")["faction_name"]))
                context = {"player": player, "errorMessage": "Faction not registered. PM Kivou [2000607] for details."}
                return render(request, 'chain.html', context)

            # get /create faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                faction = Faction.objects.create(tId=factionId, name=user.get("faction")["faction_name"])
                print('[view.chain.index] faction {} created'.format(factionId))
            else:
                faction.name = user.get("faction")["faction_name"]
                faction.save()
                print('[view.chain.index] faction {} found'.format(factionId))

            if player.factionAA:
                print('[view.chain.index] save AA key'.format(factionId))
                faction.addKey(player.tId, player.key)
                faction.save()
                if not len(faction.crontab_set.all()):
                    openCrontab = Crontab.objects.filter(open=True).all()
                    minBusy = min([c.nFactions() for c in openCrontab])
                    for crontab in openCrontab:
                        if crontab.nFactions() == minBusy:
                            crontab.faction.add(faction)
                            crontab.save()
                            break
                    print('[view.chain.index] attributed to {} '.format(crontab))

            else:
                print('[view.chain.index] remove AA key'.format(factionId))
                faction.delKey(player.tId)
                faction.save()

            chains = faction.chain_set.filter(status=True).order_by('-end')
            context = {'player': player, 'faction': faction, 'chaincat': True, 'chains': chains, 'view': {'list': True}}
            return render(request, 'chain.html', context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


def live(request):
    try:
        if request.session.get('player'):
            print('[view.chain.index] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            player.save()

            factionId = player.factionId
            key = player.key
            page = 'chain/content-reload.html' if request.method == 'POST' else 'chain.html'

            cts = int(timezone.now().timestamp())

            # get live chain and next bonus
            req = apiCall('faction', factionId, 'chain,timestamp', key)
            if 'apiError' in req:
                player.chainInfo = "N/A"
                player.factionId = 0
                player.factionAA = False
                # player.lastUpdateTS = int(timezone.now().timestamp())
                player.save()
                selectError = 'apiErrorSub' if request.method == 'POST' else 'apiError'
                context = {'player': player, 'currentTimestamp': cts, selectError: req["apiError"] + " We can't check your faction so you don't have access to this section."}
                return render(request, page, context)

            liveChain = req.get("chain")
            liveChain["timestamp"] = req.get("timestamp", 0)
            activeChain = bool(int(liveChain['current']) > 9)
            print("[view.chain.index] live chain: {}".format(activeChain))
            # liveChain["nextBonus"] = 10
            # for i in BONUS_HITS:
            #     liveChain["nextBonus"] = i
            #     if i >= int(liveChain["current"]):
            #         break

            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, 'currentTimestamp': cts, selectError: "Faction not found. It might come from a API issue. Click on chain report again please."}
                return render(request, page, context)

            if activeChain:
                print('[view.chain.index] chain active')
                chain = faction.chain_set.filter(tId=0).first()
                if chain is None:
                    print('[view.chain.index] live chain 0 created')
                    chain = faction.chain_set.create(tId=0, start=1, status=False)
                else:
                    print('[view.chain.index] live chain 0 found')

                report = chain.report_set.filter(chain=chain).first()
                print('[view.chain.index] live report is {}'.format(report))
                if report is None:
                    chain.graph = ''
                    chain.save()
                    counts = None
                    bonus = None
                    print('[view.chain.index] live counts is {}'.format(counts))
                    print('[view.chain.index] live bonus is {}'.format(bonus))
                else:
                    counts = report.count_set.extra(select={'fieldsum': 'wins + bonus'}, order_by=('-fieldsum', '-respect'))
                    bonus = report.bonus_set.all()
                    print('[view.chain.index] live counts of length {}'.format(len(counts)))
                    print('[view.chain.index] live bonus of length {}'.format(len(bonus)))

                # create graph
                graphSplit = chain.graph.split(',')
                if len(graphSplit) > 1:
                    print('[view.chain.index] data found for graph of length {}'.format(len(graphSplit)))
                    # compute average time for one bar
                    bins = (int(graphSplit[-1].split(':')[0]) - int(graphSplit[0].split(':')[0])) / float(60 * (len(graphSplit) - 1))
                    graph = {'data': [], 'info': {'binsTime': bins, 'criticalHits': int(bins) / 5}}
                    cummulativeHits = 0
                    x = numpy.zeros(len(graphSplit))
                    y = numpy.zeros(len(graphSplit))
                    for i, line in enumerate(graphSplit):
                        splt = line.split(':')
                        cummulativeHits += int(splt[1])
                        graph['data'].append([timestampToDate(int(splt[0])), int(splt[1]), cummulativeHits, int(splt[0])])
                        x[i] = int(splt[0])
                        y[i] = cummulativeHits
                    speedRate = cummulativeHits * 300 / float((int(graphSplit[-1].split(':')[0]) - int(graphSplit[0].split(':')[0])))  # hits every 5 minutes
                    graph['info']['speedRate'] = speedRate

                    #  y = ax + b (y: hits, x: timestamp)
                    a, b, _, _, _ = stats.linregress(x[-20:], y[-20:])
                    print("[view.chain.index] linreg a={} b={}".format(a, b))
                    a = max(a, 0.00001)
                    try:
                        ETA = timestampToDate(int((liveChain["max"] - b) / a))
                    except BaseException as e:
                        print("[view.chain.live] ERROR, unable to compute ETA liveChain[max] = {}, a = {}, b = {}".format(liveChain["max"], a, b))
                        print(f"[view.chain.live] {e}")
                        ETA = "unable to compute EAT"
                    graph['info']['ETALast'] = ETA
                    graph['info']['regLast'] = [a, b]

                    a, b, _, _, _ = stats.linregress(x, y)
                    try:
                        ETA = timestampToDate(int((liveChain["max"] - b) / a))
                    except BaseException as e:
                        print("[view.chain.live] ERROR, unable to compute ETA liveChain[max] = {}, a = {}, b = {}".format(liveChain["max"], a, b))
                        print(f"[view.chain.live] {e}")
                        ETA = "unable to compute EAT"
                    graph['info']['ETA'] = ETA
                    graph['info']['reg'] = [a, b]

                else:
                    print('[view.chain.live] no data found for graph')
                    graph = {'data': [], 'info': {'binsTime': 5, 'criticalHits': 1}}

                # context
                context = {'player': player, 'chaincat': True, 'faction': faction, 'chain': chain, 'liveChain': liveChain, 'bonus': bonus, 'counts': counts, 'currentTimestamp': cts, 'view': {'report': True, 'liveReport': True}, 'graph': graph}

            # no active chain
            else:
                chain = faction.chain_set.filter(tId=0).first()
                if chain is not None:
                    chain.delete()
                    print('[view.chain.index] chain 0 deleted')
                context = {'player': player, 'chaincat': True, 'currentTimestamp': cts, 'faction': faction, 'liveChain': liveChain, 'view': {'liveReport': True}}  # set chain to True to display category links

            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


# render view
def list(request):
    try:
        if request.session.get('player'):
            print('[view.chain.list] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            player.save()

            key = player.key
            factionId = player.factionId
            page = 'chain/content-reload.html' if request.method == 'POST' else 'chain.html'

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Click on chain report again please."}
                return render(request, page, context)

            # update chains if AA
            error = False
            if player.factionAA:
                chains = apiCall('faction', faction.tId, 'chains', key, sub='chains')
                if 'apiError' in chains:
                    error = chains

                else:
                    print('[view.chain.list] update chain list')
                    for k, v in chains.items():
                        chain = faction.chain_set.filter(tId=k).first()
                        if v['chain'] >= faction.hitsThreshold:
                            if chain is None:
                                # print('[view.chain.list] chain {} created'.format(k))
                                faction.chain_set.create(tId=k, nHits=v['chain'], respect=v['respect'],
                                                         start=v['start'],
                                                         end=v['end'])
                            else:
                                # print('[view.chain.list] chain {} updated'.format(k))
                                chain.start = v['start']
                                chain.end = v['end']
                                chain.nHits = v['chain']
                                # chain.reportNHits = 0
                                chain.respect = v['respect']
                                chain.save()

                        else:
                            if chain is not None:
                                # print('[view.chain.list] chain {} deleted'.format(k))
                                chain.delete()

            # get chains
            chains = faction.chain_set.filter(status=True).order_by('-end')

            context = {'player': player, 'faction': faction, 'chaincat': True, 'chains': chains, 'view': {'list': True}}
            if error:
                selectError = 'apiErrorSub' if request.method == 'POST' else 'apiError'
                context.update({selectError: error["apiError"] + " List of chain not updated."})
            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


# render view
def report(request, chainId):
    try:
        if request.session.get('player'):
            print('[view.chain.list] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            player.save()

            factionId = player.factionId
            page = 'chain/content-reload.html' if request.method == 'POST' else 'chain.html'

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Click on chain report again please."}
                return render(request, page, context)

            chains = faction.chain_set.filter(status=True).order_by('-end')

            # get chain
            chain = faction.chain_set.filter(tId=chainId).first()
            if chain is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, 'faction': faction, selectError: "Chain not found. It might come from a API issue. Click on chain report again please."}
                return render(request, page, context)

            print('[view.chain.report] chain {} found'.format(chainId))

            # get report
            report = chain.report_set.filter(chain=chain).first()
            if report is None:
                print('[view.chain.report] report of {} not found'.format(chain))
                context = dict({"player": player, 'faction': faction, 'chaincat': True, 'chain': chain, 'chains': chains, 'view': {'report': True, 'list': True}})
                return render(request, page, context)

            print('[view.chain.report] report of {} found'.format(chain))

            # create graph
            graphSplit = chain.graph.split(',')
            if len(graphSplit) > 1:
                print('[view.chain.report] data found for graph of length {}'.format(len(graphSplit)))
                # compute average time for one bar
                bins = (int(graphSplit[-1].split(':')[0]) - int(graphSplit[0].split(':')[0])) / float(60 * (len(graphSplit) - 1))
                graph = {'data': [], 'info': {'binsTime': bins, 'criticalHits': int(bins) / 5}}
                cummulativeHits = 0
                for line in graphSplit:
                    splt = line.split(':')
                    cummulativeHits += int(splt[1])
                    graph['data'].append([timestampToDate(int(splt[0])), int(splt[1]), cummulativeHits])
                    speedRate = cummulativeHits * 300 / float((int(graphSplit[-1].split(':')[0]) - int(graphSplit[0].split(':')[0])))  # hits every 5 minutes
                    graph['info']['speedRate'] = speedRate
            else:
                print('[view.chain.report] no data found for graph')
                graph = {'data': [], 'info': {'binsTime': 5, 'criticalHits': 1, 'speedRate': 0}}

            # context
            counts = report.count_set.extra(select={'fieldsum': 'wins + bonus'}, order_by=('-fieldsum', '-respect'))
            context = dict({"player": player,
                            'chaincat': True,
                            'faction': faction,
                            'chain': chain,  # for general info
                            'chains': chains,  # for chain list after report
                            'counts': counts,  # for report
                            'bonus': report.bonus_set.all(),  # for report
                            'graph': graph,  # for report
                            'view': {'list': True, 'report': True}})  # views

            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


# render view
def jointReport(request):
    try:
        if request.session.get('player'):
            print('[view.chain.list] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            player.save()

            key = player.key
            factionId = player.factionId
            page = 'chain/content-reload.html' if request.method == 'POST' else 'chain.html'

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Click on chain report again please."}
                return render(request, page, context)

            # get chains
            chains = faction.chain_set.filter(jointReport=True).order_by('start')
            print('[VIEW jointReport] {} chains for the joint report'.format(len(chains)))
            if len(chains) < 1:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {selectError: 'No chains found for the joint report. Add reports throught the chain list.',
                           'faction': faction,
                           'chains': faction.chain_set.filter(status=True).order_by('-end'),
                           'player': player, 'chaincat': True, 'view': {'list': True}}
                return render(request, page, context)

            # loop over chains
            counts = dict({})
            bonuses = dict({})
            total = {'nHits': 0, 'respect': 0.0}
            for chain in chains:
                print('[VIEW jointReport] chain {} found'.format(chain.tId))
                total['nHits'] += chain.nHits
                total['respect'] += float(chain.respect)
                # get report
                report = chain.report_set.filter(chain=chain).first()
                if report is None:
                    return render(request, 'yata/error.html', {'errorMessage': 'Report of chain {} not found in the database.'.format(chain.tId)})
                print('[VIEW jointReport] report of {} found'.format(chain))
                # loop over counts
                chainCounts = report.count_set.all()
                chainBonuses = report.bonus_set.all()
                for bonus in chainBonuses:
                    if bonus.tId in bonuses:
                        bonuses[bonus.tId][1].append(bonus.hit)
                        bonuses[bonus.tId][2] += bonus.respect
                    else:
                        bonuses[bonus.tId] = [bonus.name, [bonus.hit], bonus.respect, 0]

                for count in chainCounts:

                    if count.attackerId in counts:
                        counts[count.attackerId]['hits'] += count.hits
                        counts[count.attackerId]['wins'] += count.wins
                        counts[count.attackerId]['bonus'] += count.bonus
                        counts[count.attackerId]['respect'] += count.respect
                        counts[count.attackerId]['fairFight'] += count.fairFight
                        counts[count.attackerId]['war'] += count.war
                        counts[count.attackerId]['warhits'] += count.warhits
                        counts[count.attackerId]['retaliation'] += count.retaliation
                        counts[count.attackerId]['groupAttack'] += count.groupAttack
                        counts[count.attackerId]['overseas'] += count.overseas
                        counts[count.attackerId]['watcher'] += count.watcher / float(len(chains))
                        counts[count.attackerId]['beenThere'] = count.beenThere or counts[count.attackerId]['beenThere']  # been present to at least one chain
                    else:
                        counts[count.attackerId] = {'name': count.name,
                                                    'hits': count.hits,
                                                    'wins': count.wins,
                                                    'bonus': count.bonus,
                                                    'respect': count.respect,
                                                    'fairFight': count.fairFight,
                                                    'war': count.war,
                                                    'warhits': count.warhits,
                                                    'retaliation': count.retaliation,
                                                    'groupAttack': count.groupAttack,
                                                    'overseas': count.overseas,
                                                    'watcher': count.watcher / float(len(chains)),
                                                    'daysInFaction': count.daysInFaction,
                                                    'beenThere': count.beenThere,
                                                    'attackerId': count.attackerId}
                print('[VIEW jointReport] {} counts for {}'.format(len(counts), chain))

            # order the Bonuses
            # bonuses ["name", [[bonus1, bonus2, bonus3, ...], respect, nwins]]
            smallHit = 999999999
            for k, v in counts.items():
                if k in bonuses:
                    if v["daysInFaction"] >= 0:
                        bonuses[k][3] = v["wins"]
                        smallHit = min(int(v["wins"]), smallHit)
                    else:
                        del bonuses[k]

            for k, v in counts.items():
                if k not in bonuses and int(v["wins"]) >= smallHit and v["daysInFaction"] >= 0:
                    bonuses[k] = [v["name"], [], 0, v["wins"]]

                # else:
                #     if int(v["wins"]) >= int(smallestNwins):
                #         bonuses.append([[v["name"]], [[], 1, v["wins"]]])

            # aggregate counts
            arrayCounts = [v for k, v in sorted(counts.items(), key=lambda x: (-x[1]["wins"] - x[1]["bonus"], -x[1]["respect"]))]
            arrayBonuses = [[i, name, ", ".join([str(h) for h in sorted(hits)]), respect, wins] for i, (name, hits, respect, wins) in sorted(bonuses.items(), key=lambda x: x[1][1], reverse=True)]

            # add last time connected
            error = False
            update = updateMembers(faction, key=key)
            if 'apiError' in update:
                error = update

            for i, bonus in enumerate(arrayBonuses):
                try:
                    arrayBonuses[i].append(faction.member_set.filter(tId=bonus[0]).first().lastAction)
                except BaseException:
                    arrayBonuses[i].append(False)

            # context
            context = dict({'chainsReport': chains,  # chains of joint report
                            'total': total,  # for general info
                            'counts': arrayCounts,  # counts for report
                            'bonuses': arrayBonuses,  # bonuses for report
                            'chains': faction.chain_set.filter(status=True).order_by('-end'),  # for chain list after report
                            'player': player,
                            'faction': faction,
                            'chaincat': True,  # to display categories
                            'view': {'jointReport': True}})  # view

            if error:
                selectError = 'apiErrorSub' if request.method == 'POST' else 'apiError'
                context.update({selectError: error["apiError"] + " List of members not updated."})
            return render(request, page, context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


# render view
def members(request):
    try:
        if request.session.get('player'):
            print('[view.chain.members] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            player.save()

            key = player.key
            factionId = player.factionId
            page = 'chain/content-reload.html' if request.method == 'POST' else 'chain.html'

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Click on chain report again please."}
                return render(request, page, context)

            # update chains if AA
            members = updateMembers(faction, key=key)
            error = False
            if 'apiError' in members:
                error = members

            # get members
            members = faction.member_set.all()

            context = {'player': player, 'chaincat': True, 'faction': faction, 'members': members, 'view': {'members': True}}
            if error:
                selectError = 'apiErrorSub' if request.method == 'POST' else 'apiError'
                context.update({selectError: error["apiError"] + " Members not updated."})
            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


# action view
def createReport(request, chainId):
    try:
        if request.session.get('player') and request.method == 'POST':
            print('[view.chain.createReport] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()

            factionId = player.factionId
            context = {"player": player}

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})

            # get chain
            chain = faction.chain_set.filter(tId=chainId).first()
            if chain is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Chain {} not found in the database.'.format(chainId)})
            print('[view.chain.createReport] chain {} found'.format(chainId))

            print('[view.chain.createReport] number of hits: {}'.format(chain.nHits))
            chain.createReport = True
            chain.save()
            context = {"player": player, "chain": chain}
            return render(request, 'chain/list-buttons.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


# action view
def renderIndividualReport(request, chainId, memberId):
    try:
        if request.session.get('player') and request.method == 'POST':
            # get session info
            print('[view.chain.renderIndividualReport] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            factionId = player.factionId

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
            print('[view.chain.renderIndividualReport] faction {} found'.format(factionId))

            # get chain
            chain = faction.chain_set.filter(tId=chainId).first()
            if chain is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Chain {} not found in the database.'.format(chainId)})
            print('[view.chain.renderIndividualReport] chain {} found'.format(chainId))

            # get report
            report = chain.report_set.filter(chain=chain).first()
            if report is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Report of chain {} not found in the database.'.format(chainId)})
            print('[view.chain.renderIndividualReport] report of {} found'.format(chain))

            # create graph
            count = report.count_set.filter(attackerId=memberId).first()
            graphSplit = count.graph.split(',')
            if len(graphSplit) > 1:
                print('[view.chain.renderIndividualReport] data found for graph of length {}'.format(len(graphSplit)))
                # compute average time for one bar
                bins = (int(graphSplit[-1].split(':')[0]) - int(graphSplit[0].split(':')[0])) / float(60 * (len(graphSplit) - 1))
                graph = {'data': [], 'info': {'binsTime': bins, 'criticalHits': int(bins) / 5}}
                cummulativeHits = 0
                for line in graphSplit:
                    splt = line.split(':')
                    cummulativeHits += int(splt[1])
                    graph['data'].append([timestampToDate(int(splt[0])), int(splt[1]), cummulativeHits])
                    speedRate = cummulativeHits * 300 / float((int(graphSplit[-1].split(':')[0]) - int(graphSplit[0].split(':')[0])))  # hits every 5 minutes
                    graph['info']['speedRate'] = speedRate
            else:
                print('[view.chain.report] no data found for graph')
                graph = {'data': [], 'info': {'binsTime': 5, 'criticalHits': 1, 'speedRate': 0}}

            # context
            context = dict({'graph': graph,  # for report
                            'memberId': memberId})  # for selecting to good div

            print('[view.chain.renderIndividualReport] render')
            return render(request, 'chain/ireport.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


# action view
def deleteReport(request, chainId):
    try:
        if request.session.get('player') and request.method == 'POST':
            print('[view.chain.deleteReport] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            factionId = player.factionId
            context = {"player": player}

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})

            # get chain
            chain = faction.chain_set.filter(tId=chainId).first()
            if chain is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Chain {} not found in the database.'.format(chainId)})
            print('[view.chain.deleteReport] chain {} found'.format(chainId))

            # delete old report and remove from joint report
            chain.report_set.all().delete()
            chain.jointReport = False
            chain.createReport = False
            chain.hasReport = False
            chain.save()

            context = {"player": player, "chain": chain}
            return render(request, 'chain/list-buttons.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


# action view
def toggleReport(request, chainId):
    try:
        if request.session.get('player') and request.method == 'POST':
            print('[view.chain.deleteReport] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            factionId = player.factionId
            context = {"player": player}

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
            print('[VIEW toggleReport] faction {} found'.format(factionId))

            # get chain
            chain = faction.chain_set.filter(tId=chainId).first()
            if chain is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Chain {} not found in the database.'.format(chainId)})
            print('[VIEW toggleReport] chain {} found'.format(chainId))

            # toggle
            chain.toggle_report()
            chain.save()

            print('[VIEW toggleReport] render')
            context.update({"chain": chain})
            return render(request, 'chain/list-buttons.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


def aa(request):
    try:
        if request.session.get('player'):
            print('[view.chain.aa] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            player.save()

            if player.factionAA:
                faction = Faction.objects.filter(tId=player.factionId).first()
                print('[view.chain.aa] player with AA. Faction {}'.format(faction))
                faction.addKey(player.tId, player.key)
                faction.save()
                if not len(faction.crontab_set.all()):
                    openCrontab = Crontab.objects.filter(open=True).all()
                    minBusy = min([c.nFactions() for c in openCrontab])
                    for crontab in openCrontab:
                        if crontab.nFactions() == minBusy:
                            crontab.faction.add(faction)
                            crontab.save()
                            break
                    print('[view.chain.aa] attributed to {} '.format(crontab))

                crontabs = dict({})
                # update members before to avoid coming here before having members
                updateMembers(faction, key=player.key)
                keys = [(faction.member_set.filter(tId=id).first(), k) for (id, k) in faction.getAllPairs()]
                for crontab in faction.crontab_set.all():
                    print('[view.chain.aa]     --> {}'.format(crontab))
                    crontabs[crontab.tabNumber] = {"crontab": crontab, "factions": []}
                    for f in crontab.faction.all():
                        crontabs[crontab.tabNumber]["factions"].append(f)
                context = {'player': player, 'chaincat': True, 'crontabs': crontabs, "bonus": BONUS_HITS, "faction": faction, 'keys': keys, 'view': {'aa': True}}
                page = 'chain/content-reload.html' if request.method == 'POST' else 'chain.html'
                return render(request, page, context)

            else:
                return returnError(type=403, msg="You need AA rights.")

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


# action view
def toggleKey(request, id):
    try:
        if request.session.get('player') and request.method == 'POST':
            print('[view.chain.toggleKey] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            factionId = player.factionId

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
            print('[view.chain.toggleKey] faction {} found'.format(factionId))

            id, key = faction.toggleKey(player.tId)

            context = {"player": player, "p": player, "k": key}
            return render(request, 'chain/aa-keys.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


# action view
def chainThreshold(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            print('[view.chain.toggleKey] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            factionId = player.factionId

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
            print('[view.chain.toggleKey] faction {} found'.format(factionId))

            previousThreshold = faction.hitsThreshold
            faction.hitsThreshold = int(request.POST.get("threshold", 100))
            faction.save()

            context = {"player": player, "faction": faction, "bonus": BONUS_HITS, "onChange": True, "previousThreshold": previousThreshold}
            return render(request, 'chain/aa-threshold.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


# action view
def togglePoster(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            print('[view.chain.togglePoster] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            factionId = player.factionId

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
            print('[view.chain.togglePoster] faction {} found'.format(factionId))

            faction.poster = not faction.poster
            faction.save()

            messageDeleted = False
            if not faction.poster:
                url = "{}/trees/{}.png".format(settings.STATIC_ROOT, faction.tId)
                if os.path.exists(url):
                    print('[view.chain.togglePoster] Delete faction {} poster at {}'.format(factionId, url))
                    os.remove(url)
                    messageDeleted = True
                else:
                    print('[view.chain.togglePoster] Try to delete faction {} poster at {} but file does not exist'.format(factionId, url))

            context = {'faction': faction}
            if messageDeleted:
                context.update({'messageDeleted': messageDeleted})
            return render(request, 'chain/aa-poster.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


def tree(request):
    try:
        if request.session.get('player'):
            print('[view.chain.tree] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            player.save()

            if player.factionAA:
                faction = Faction.objects.filter(tId=player.factionId).first()
                print('[view.chain.tree] player with AA. Faction {}'.format(faction))

                if not faction.poster:
                    context = {'player': player, 'chaincat': True, 'faction': faction, 'errorMessageSub': "Poster disabled. Go to AA options to enable it."}
                    page = 'chain/content-reload.html' if request.method == 'POST' else 'chain.html'
                    return render(request, page, context)

                if request.method == "POST":
                    print(request.POST)
                    t = request.POST.get("t", False)
                    p = int(request.POST.get("p", False))
                    v = int(request.POST.get("v", False))
                    if t:
                        print('[view.chain.tree] {}[{}] = {}'.format(t, p, v))
                        posterOpt = json.loads(faction.posterOpt)
                        if posterOpt.get(t, False):
                            posterOpt[t][p] = v
                        else:
                            if t == "fontColor":
                                option = [0, 0, 0, 255]
                                option[p] = v
                            elif t == "fontFamily":
                                option = [0]
                                option[p] = v
                            elif t == "iconType":
                                option = [0]
                                option[p] = v
                            elif t == "background":
                                option = [0, 0, 0, 0]
                                option[p] = v

                            posterOpt[t] = option

                        faction.posterOpt = json.dumps(posterOpt)
                        faction.save()

                factionTree(faction)

                fntId = {i: [f.split("__")[0].replace("-", " "), int(f.split("__")[1].split(".")[0])] for i, f in enumerate(sorted(os.listdir(settings.STATIC_ROOT + '/perso/font/')))}
                posterOpt = json.loads(faction.posterOpt)
                context = {'player': player, 'chaincat': True, 'faction': faction, "posterOpt": posterOpt, 'random': random.randint(0, 65535), 'fonts': fntId, 'view': {'tree': True}}
                page = 'chain/content-reload.html' if request.method == 'POST' else 'chain.html'
                return render(request, page, context)

            else:
                return returnError(type=403, msg="You need AA rights.")

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


def armory(request):
    from bazaar.items import ITEM_TYPE

    try:
        if request.session.get('player'):
            print('[view.armory] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            player.save()
            faction = Faction.objects.filter(tId=player.factionId).first()

            if player.factionAA:
                print('[view.armory] player with AA. Faction {}'.format(faction))
                armoryRaw = apiCall('faction', player.factionId, 'armorynewsfull', player.key, sub="armorynews")
                if 'apiError' in armoryRaw:
                    context = {'player': player, 'chaincat': True, 'faction': faction, "apiErrorSub": armoryRaw["apiError"]}
                    page = 'chain/content-reload.html' if request.method == 'POST' else 'chain.html'
                    return render(request, page, context)

                if faction.armoryRecord:
                    for k, v in json.loads(faction.armoryString).items():
                        if k not in armoryRaw:
                            armoryRaw[k] = v
                    faction.armoryString = json.dumps(armoryRaw)
                else:
                    faction.armoryString = "{}"

                faction.save()

            else:
                armoryRaw = json.loads(faction.armoryString)

            now = int(timezone.now().timestamp())
            timestamps = {"start": now, "end": 0, "fstart": now, "fend": 0, "size": 0}
            toDel = []
            for k, v in armoryRaw.items():
                if type(v) is not dict:
                    toDel.append(k)
                else:
                    ts = int(v.get("timestamp", 0))
                    timestamps["start"] = min(timestamps["start"], ts)
                    timestamps["end"] = max(timestamps["end"], ts)
                    if ts < int(request.POST.get("start", 0)) or ts > int(request.POST.get("end", now)):
                        toDel.append(k)

            for k in toDel:
                del armoryRaw[k]

            timestamps["fstart"] = request.POST.get("start", timestamps.get("start"))
            timestamps["fend"] = request.POST.get("end", timestamps.get("end"))
            timestamps["size"] = len(armoryRaw)

            armory = dict({})
            timestamps["nObjects"] = 0
            for k, v in armoryRaw.items():
                ns = cleanhtml(v.get("news", "")).split(" ")
                if 'used' in ns:
                    member = ns[0]
                    if ns[6] in ["points"]:
                        item = ns[6].title()
                        n = 25
                    else:
                        item = " ".join(ns[6:-1]).split(":")[0].strip()
                        # item = " ".join(ns[6:-1]).strip()
                        n = 1

                    timestamps["nObjects"] += n
                    if item in armory:
                        if member in armory[item]:
                            armory[item][member][0] += n
                        else:
                            armory[item][member] = [n, 0]
                    else:
                        # new item and new member [taken, given]
                        armory[item] = {member: [n, 0]}

                elif 'deposited' in ns:
                    member = ns[0]
                    n = int(ns[2].replace(",", ""))
                    timestamps["nObjects"] += n
                    if ns[-1] in ["points"]:
                        item = ns[-1].title()
                    else:
                        item = " ".join(ns[4:]).split(":")[0].strip()
                        # item = " ".join(ns[4:]).strip()
                    if item in armory:
                        if member in armory[item]:
                            armory[item][member][1] += n
                        else:
                            armory[item][member] = [0, n]
                    else:
                        # new item and new member [taken, given]
                        armory[item] = {member: [0, n]}

                # elif 'gave' in ns:
                    # print(ns)

                elif 'filled' in ns:
                    member = ns[0]
                    item = "Blood Bag"
                    timestamps["nObjects"] += 1
                    if item in armory:
                        if member in armory[item]:
                            armory[item][member][1] += 1
                        else:
                            armory[item][member] = [0, 1]
                    else:
                        # new item and new member [taken, given]
                        armory[item] = {member: [0, 1]}

            armoryType = {t: dict({}) for t in ITEM_TYPE}
            armoryType["Points"] = dict({})

            for k, v in armory.items():
                for t, i in ITEM_TYPE.items():
                    # if k.split(" : ")[0] in i:
                    if k in i:
                        armoryType[t][k] = v
                        break
                if k in ["Points"]:
                    armoryType["Points"][k] = v

            context = {'player': player, 'chaincat': True, 'faction': faction, "timestamps": timestamps, "armory": armoryType, 'view': {'armory': True}}
            page = 'chain/content-reload.html' if request.method == 'POST' else 'chain.html'
            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


# action view
def toggleArmoryRecord(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            print('[view.chain.toggleArmoryRecord] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            factionId = player.factionId

            if player.factionAA:
                faction = Faction.objects.filter(tId=factionId).first()
                if faction is None:
                    return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
                print('[view.chain.toggleArmoryRecord] faction {} found'.format(factionId))

                faction.armoryRecord = not faction.armoryRecord
                faction.save()

                context = {"player": player, "faction": faction}
                return render(request, 'chain/armory-record.html', context)

            else:
                return returnError(type=403, msg="You need AA rights.")

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


# action view
def resetArmoryRecord(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            print('[view.chain.toggleArmoryRecord] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            factionId = player.factionId

            if player.factionAA:
                faction = Faction.objects.filter(tId=factionId).first()
                if faction is None:
                    return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
                print('[view.chain.toggleArmoryRecord] faction {} found'.format(factionId))

                faction.armoryString = "{}"
                faction.save()

                context = {"player": player, "faction": faction}
                return render(request, 'chain/armory-record.html', context)

            else:
                return returnError(type=403, msg="You need AA rights.")

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


def walls(request):
    try:
        if request.session.get('player'):
            print('[view.chain.wall] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            factionId = player.factionId

            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
            print('[view.chain.wall] faction {} found'.format(factionId))

            walls = Wall.objects.filter(factions=faction).all()

            summary = dict({})
            for wall in walls:
                # print(wall)
                aFac = f"{wall.attackerFactionName} [{wall.attackerFactionId}]"
                dFac = f"{wall.defenderFactionName} [{wall.defenderFactionId}]"

                if aFac not in summary:
                    summary[aFac] = dict({'Total': [0, 0, 0],  # Total [Points / Joins / Clears]
                                          'Players': dict({})})
                if dFac not in summary:
                    summary[dFac] = dict({'Total': [0, 0, 0],  # Total [Points / Joins / Clears]
                                          'Players': dict({})})

                attackers = json.loads(wall.attackers)
                for k, v in attackers.items():
                    if k not in summary[aFac]['Players']:
                        summary[aFac]['Players'][k] = {"D": [0, 0, 0],  # [Points / Joins / Clears]
                                                       "A": [0, 0, 0],  # [Points / Joins / Clears]
                                                       "P": [v["XID"], v["Name"], v["Level"]]}
                    summary[aFac]['Players'][k]["A"][0] += v["Points"]
                    summary[aFac]['Players'][k]["A"][1] += v["Joins"]
                    summary[aFac]['Players'][k]["A"][2] += v["Clears"]
                    summary[aFac]['Total'][0] += v["Points"]
                    summary[aFac]['Total'][1] += v["Joins"]
                    summary[aFac]['Total'][2] += v["Clears"]

                defenders = json.loads(wall.defenders)
                for k, v in defenders.items():
                    if k not in summary[dFac]['Players']:
                        summary[dFac]['Players'][k] = {"D": [0, 0, 0],  # [Points / Joins / Clears]
                                                       "A": [0, 0, 0],  # [Points / Joins / Clears]
                                                       "P": [v["XID"], v["Name"], v["Level"]]}
                    summary[dFac]['Players'][k]["A"][0] += v["Points"]
                    summary[dFac]['Players'][k]["A"][1] += v["Joins"]
                    summary[dFac]['Players'][k]["A"][2] += v["Clears"]
                    summary[dFac]['Total'][0] += v["Points"]
                    summary[dFac]['Total'][1] += v["Joins"]
                    summary[dFac]['Total'][2] += v["Clears"]

            # print("summary")
            # for k, v in summary.items():
            #     print(k, v)

            context = {'player': player, 'chaincat': True, 'faction': faction, "walls": walls, 'summary': summary, 'view': {'walls': True}}
            page = 'chain/content-reload.html' if request.method == 'POST' else 'chain.html'
            return render(request, page, context)

        else:
            message = "You might want to log in."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


# action view
def deleteWall(request, wallId):
    try:
        if request.session.get('player') and request.method == 'POST':
            print('[view.chain.deleteWall] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            factionId = player.factionId

            if player.factionAA:
                faction = Faction.objects.filter(tId=factionId).first()
                if faction is None:
                    return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
                print('[view.chain.deleteWall] faction {} found'.format(factionId))

                wall = Wall.objects.filter(tId=wallId).first()
                wall.factions.remove(faction)
                if not len(wall.factions.all()):
                    print('[view.chain.deleteWall] delete wall {}'.format(wall.tId))
                    wall.delete()

                return render(request, 'chain/walls-line.html')
            else:
                return returnError(type=403, msg="You need AA rights.")

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


@csrf_exempt
def importWall(request):
    if request.method == 'POST':
        try:
            req = json.loads(request.body)

            # get author
            authorId = req.get("author", 0)
            author = Player.objects.filter(tId=authorId).first()

            #  check if author is in YATA
            if author is None:
                t = 0
                m = "You're not register in YATA"
                print(m)
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")
            print("Author in yata: checked")
            print(author)

            # check if API key is valid with api call
            HTTP_KEY = request.META.get("HTTP_KEY")
            call = apiCall('user', '', '', key=HTTP_KEY)
            print(call)
            if "apiError" in call:
                t = -1
                m = call["apiError"]
                print(m)
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")

            # check if API key sent == API key in YATA
            if HTTP_KEY != author.key:
                t = 0
                m = "Your API key seems to be out of date in YATA, please log again"
                print(m)
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")
            print("API keys match: checked")

            #  check if AA of a faction
            if not author.factionAA:
                t = 0
                m = "You don't have AA perm"
                print(m)
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")
            print("AA perm: checked")

            #  check if can get faction
            faction = Faction.objects.filter(tId=author.factionId).first()
            if faction is None:
                t = 0
                m = f"Can't find faction {author.factionId} in YATA database"
                print(m)
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")
            print("Faction exists: checked")

            attackers = dict({})
            defenders = dict({})
            i = 0
            for p in req.get("participants"):
                i += 1
                if p.get("Name")[0] == '=':
                    p["Name"] = p["Name"][2:-1]
                if p.get("Position") in ["Attacker"]:
                    attackers[p.get('XID')] = p
                else:
                    defenders[p.get('XID')] = p
            print(f"Wall Participants: {i}")

            if i > 500:
                t = 0
                m = f"{i} is too much participants for a wall"
                print(m)
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")
            print("# Participant: checked")

            wallDic = {'tId': int(req.get('id')),
                       # 'tss': int(req.get('ts_start')),
                       # 'tse': int(req.get('ts_end')),
                       'tss': int(req.get('ts_start')),
                       'tse': int(req.get('ts_end')),
                       'attackers': json.dumps(attackers),
                       'defenders': json.dumps(defenders),
                       'attackerFactionId': int(req.get('att_fac')),
                       'defenderFactionId': int(req.get('def_fac')),
                       'attackerFactionName': req.get('att_fac_name'),
                       'defenderFactionName': req.get('def_fac_name'),
                       'territory': req.get('terr')}
            print("Wall headers: processed")

            if faction.tId not in [wallDic.get('attackerFactionId'), wallDic.get('defenderFactionId')]:
                t = 0
                m = f"{faction} is not involved in this war"
                print(m)
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")
            print("Faction in wall: checked")

            messageList = []
            wall = Wall.objects.filter(tId=wallDic.get('tId')).first()
            if wall is None:
                messageList.append(f"Wall {wallDic.get('tId')} created")
                creation = True
                wall = Wall.objects.create(**wallDic)
            else:
                messageList.append(f"Wall {wallDic.get('tId')} modified")
                wall.update(wallDic)

            if faction in wall.factions.all():
                messageList.append(f"wall already added to {faction}")
            else:
                messageList.append(f"adding wall to {faction}")
                wall.factions.add(faction)

            t = 1
            m = ", ".join(messageList)
            print(m)
            return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")

        except BaseException as e:
            t = 0
            m = f"Server error... YATA's been poorly coded: {e}"
            return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")

    else:
        return returnError(type=403, msg="You need to post. Don\'t try to be a smart ass.")
