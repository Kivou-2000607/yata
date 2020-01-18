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
from django.shortcuts import redirect
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.forms.models import model_to_dict

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
from chain.functions import updateFactionTree
from chain.functions import factionTree
from chain.functions import BONUS_HITS

from chain.models import Faction
from chain.models import Crontab
from chain.models import Wall
from chain.models import Territory
from chain.models import Racket
from chain.models import FactionData


# render view
def index(request):
    try:
        if request.session.get('player'):
            print('[view.chain.index] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            player.active = True
            key = player.getKey()

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
                faction.addKey(player.tId, player.getKey())
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
            return redirect('/chain/territories/')
            # return returnError(type=403, msg="You might want to log in.")

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
            key = player.getKey()
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
                graphSplitCrit = chain.graphCrit.split(',')
                graphSplitStat = chain.graphStat.split(',')
                if len(graphSplit) > 1:
                    print('[view.chain.index] data found for graph of length {}'.format(len(graphSplit)))
                    # compute average time for one bar
                    bins = (int(graphSplit[-1].split(':')[0]) - int(graphSplit[0].split(':')[0])) / float(60 * (len(graphSplit) - 1))
                    graph = {'data': [], 'dataCrit': [], 'dataStat': [], 'info': {'binsTime': bins, 'criticalHits': int(bins) / 5}}
                    cummulativeHits = 0
                    x = numpy.zeros(len(graphSplit))
                    y = numpy.zeros(len(graphSplit))
                    for i, (line, lineCrit) in enumerate(zip(graphSplit, graphSplitCrit)):
                        splt = line.split(':')
                        spltCrit = lineCrit.split(':')
                        cummulativeHits += int(splt[1])
                        graph['data'].append([timestampToDate(int(splt[0])), int(splt[1]), cummulativeHits, int(splt[0])])
                        graph['dataCrit'].append([timestampToDate(int(splt[0])), int(spltCrit[0]), int(spltCrit[1]), int(spltCrit[2])])
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
                        ETA = "unable to compute EAT"
                    graph['info']['ETALast'] = ETA
                    graph['info']['regLast'] = [a, b]

                    a, b, _, _, _ = stats.linregress(x, y)
                    try:
                        ETA = timestampToDate(int((liveChain["max"] - b) / a))
                    except BaseException as e:
                        print("[view.chain.live] ERROR, unable to compute ETA liveChain[max] = {}, a = {}, b = {}".format(liveChain["max"], a, b))
                        ETA = "unable to compute EAT"
                    graph['info']['ETA'] = ETA
                    graph['info']['reg'] = [a, b]

                    if len(graphSplitStat) > 1:
                        for line in graphSplitStat:
                            splt = line.split(':')
                            graph['dataStat'].append([float(splt[0]), int(splt[1])])

                else:
                    print('[view.chain.live] no data found for graph')
                    graph = {'data': [], 'dataCrit': [], 'dataStat': [], 'info': {'binsTime': 5, 'criticalHits': 1}}

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


# action view
def toggleLiveReport(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            print('[view.chain.toggleLiveReport] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            factionId = player.factionId

            if player.factionAA:
                # get faction
                faction = Faction.objects.filter(tId=factionId).first()
                if faction is None:
                    return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
                    print('[view.chain.toggleLiveReport] faction {} found'.format(factionId))

                # toggle live creation
                message = "The report will be deleted."
                if faction.numberOfKeys:
                    faction.createLive = not faction.createLive
                else:
                    faction.createLive = False
                    message = "You need at least one AA key enabled."

                faction.save()

                print('[view.chain.toggleLiveReport] render')
                context = {"player": player, "faction": faction, "message": message, "liveChain": {"current": 10}}
                return render(request, 'chain/live-toggle.html', context)

            else:
                return returnError(type=403, msg="You need AA rights.")

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

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

            key = player.getKey()
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
            graphSplitCrit = chain.graphCrit.split(',')
            graphSplitStat = chain.graphStat.split(',')
            if len(graphSplit) > 1 and len(graphSplitCrit) > 1:
                print('[view.chain.report] data found for graph of length {}'.format(len(graphSplit)))
                # compute average time for one bar
                bins = (int(graphSplit[-1].split(':')[0]) - int(graphSplit[0].split(':')[0])) / float(60 * (len(graphSplit) - 1))
                graph = {'data': [], 'dataCrit': [], 'dataStat': [], 'info': {'binsTime': bins, 'criticalHits': int(bins) / 5}}
                cummulativeHits = 0
                for line, lineCrit in zip(graphSplit, graphSplitCrit):
                    splt = line.split(':')
                    spltCrit = lineCrit.split(':')
                    cummulativeHits += int(splt[1])
                    graph['data'].append([timestampToDate(int(splt[0])), int(splt[1]), cummulativeHits])
                    graph['dataCrit'].append([timestampToDate(int(splt[0])), int(spltCrit[0]), int(spltCrit[1]), int(spltCrit[2])])
                    speedRate = cummulativeHits * 300 / float((int(graphSplit[-1].split(':')[0]) - int(graphSplit[0].split(':')[0])))  # hits every 5 minutes
                    graph['info']['speedRate'] = speedRate

                if len(graphSplitStat) > 1:
                    for line in graphSplitStat:
                        splt = line.split(':')
                        graph['dataStat'].append([float(splt[0]), int(splt[1])])

            else:
                print('[view.chain.report] no data found for graph')
                graph = {'data': [], 'dataCrit': [], 'dataStat': [], 'info': {'binsTime': 5, 'criticalHits': 1, 'speedRate': 0}}

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

            key = player.getKey()
            factionId = player.factionId
            page = 'chain/content-reload.html' if request.method == 'POST' else 'chain.html'

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Click on chain report again please."}
                return render(request, page, context)

            # update members for:
            # add last time connected in bonus table
            # more recent dif than from count
            error = False
            update = updateMembers(faction, key=key, force=False)
            if 'apiError' in update:
                error = update

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
                        # compute last dif if possible
                        if 'apiError' in update:
                            dif = count.daysInFaction
                        else:
                            m = update.filter(tId=count.attackerId).first()
                            dif = -1 if m is None else m.daysInFaction

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
                                                    'daysInFaction': dif,
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

            for i, bonus in enumerate(arrayBonuses):
                try:
                    arrayBonuses[i].append(faction.member_set.filter(tId=bonus[0]).first().lastAction)
                except BaseException:
                    arrayBonuses[i].append(False)

            # hack for joint report total time
            totalTime = 0
            for c in chains:
                totalTime += (c.end - c.start)
            chain = {"start": 0, "end": totalTime, "nAttacks": False}
            # context
            context = dict({'chainsReport': chains,  # chains of joint report
                            'total': total,  # for general info
                            'counts': arrayCounts,  # counts for report
                            'bonuses': arrayBonuses,  # bonuses for report
                            'chains': faction.chain_set.filter(status=True).order_by('-end'),  # for chain list after report
                            'player': player,
                            'chain': chain,
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

            key = player.getKey()
            factionId = player.factionId
            page = 'chain/content-reload.html' if request.method == 'POST' else 'chain.html'

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Click on chain report again please."}
                return render(request, page, context)

            # update chains if AA
            members = updateMembers(faction, key=key, force=False)
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
def toggleMemberShare(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            print('[view.chain.toggleMemberShare] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()

            factionId = player.factionId

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'chain/members-line-energy.html', {'errorMessage': 'Faction {} not found'.format(factionId)})

            # get member
            member = faction.member_set.filter(tId=player.tId).first()
            if member is None:
                return render(request, 'chain/members-line-energy.html', {'errorMessage': 'Member {} not found'.format(player.tId)})

            # toggle share energy
            if request.POST.get("type") == "energy":
                member.shareE = 0 if member.shareE else 1
                error = member.updateEnergy(key=player.getKey())
                # handle api error
                if error:
                    member.shareE = 0
                    member.energy = 0
                    return render(request, 'chain/members-line-energy.html', {'errorMessage': error.get('apiErrorString', 'error')})
                else:
                    context = {"player": player, "member": member}
                    return render(request, 'chain/members-line-energy.html', context)

            elif request.POST.get("type") == "nerve":
                member.shareN = 0 if member.shareN else 1
                error = member.updateNNB(key=player.getKey())
                # handle api error
                if error:
                    member.shareN = 0
                    member.nnb = 0
                    return render(request, 'chain/members-line-nnb.html', {'errorMessage': error.get('apiErrorString', 'error')})
                else:
                    context = {"player": player, "member": member}
                    return render(request, 'chain/members-line-nnb.html', context)

                # member.save()
            else:
                return render(request, 'chain/members-line-energy.html', {'errorMessage': '?'})

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


# action view
def updateMember(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            print('[view.chain.updateMember] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            factionId = player.factionId

            if player is None:
                return render(request, 'chain/members-line.html', {'member': False, 'errorMessage': 'Who are you?'})

            # get faction (of the user, not the member)
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'chain/members-line.html', {'errorMessage': 'Faction {} not found'.format(factionId)})

            # update members status for the faction (skip < 30s)
            membersAPI = faction.updateMemberStatus()

            # get member id
            memberId = request.POST.get("memberId", 0)

            # get member
            member = faction.member_set.filter(tId=memberId).first()
            if member is None:
                return render(request, 'chain/members-line.html', {'errorMessage': 'Member {} not found in faction {}'.format(memberId, factionId)})

            # update status
            member.updateStatus(**membersAPI.get(memberId, dict({})).get("status"))

            # update energy
            tmpP = Player.objects.filter(tId=memberId).first()
            if tmpP is None:
                member.shareE = -1
                member.shareN = -1
                member.save()
            elif member.shareE > 0 and member.shareN > 0:
                req = apiCall("user", "", "perks,bars,crimes", key=tmpP.getKey())
                member.updateEnergy(key=tmpP.getKey(), req=req)
                member.updateNNB(key=tmpP.getKey(), req=req)
            elif member.shareE > 0:
                member.updateEnergy(key=tmpP.getKey())
            elif member.shareN > 0:
                member.updateNNB(key=tmpP.getKey())

            context = {"player": player, "member": member}
            return render(request, 'chain/members-line.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

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

            # reset number of createReport
            faction.createReport = bool(faction.numberOfReportsToCreate())
            faction.save()
            print('[view.chain.createReport] set faction create report to {}'.format(faction.createReport))

            context = {"player": player, "chain": chain}
            return render(request, 'chain/list-buttons.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


# action view
def renderIndividualReport(request):
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

            chainId = request.POST.get("chainId", 0)
            memberId = request.POST.get("memberId", 0)
            print(chainId)
            if chainId in ["joint"]:
                # get all chains from joint report
                chains = faction.chain_set.filter(jointReport=True).order_by('start')
                counts = []
                for chain in chains:
                    report = chain.report_set.first()
                    count = report.count_set.filter(attackerId=memberId).first()
                    counts.append(count)
                context = dict({'counts': counts, 'memberId': memberId})
                return render(request, 'chain/ireport.html', context)
            else:
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
                if count is not None:
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

                    return render(request, 'chain/ireport.html', context)

                else:
                    print('[view.chain.renderIndividualReport] Error: no count...')
                    # context
                    context = dict({'graph': None,  # for report
                                    'memberId': memberId})  # for selecting to good div
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

            # reset number of createReport
            faction.createReport = bool(faction.numberOfReportsToCreate())
            faction.save()
            print('[view.chain.deleteReport] set faction create report to {}'.format(faction.createReport))

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


def respectSimulator(request):
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
                faction.addKey(player.tId, player.getKey())
                faction.save()

                # upgrade tree
                if request.POST.get('reset', False):
                    factionTree, simuTree = updateFactionTree(faction, key=player.getKey(), force=True, reset=True)
                else:
                    factionTree, simuTree = updateFactionTree(faction, key=player.getKey(), force=True)
                upgradeTree = json.loads(FactionData.objects.first().upgradeTree)

                upgradeTreeReshaped = dict({})
                totalRespect = {"faction": 0, "tree": 0, "simu": 0}

                for branchId, branch in upgradeTree.items():
                    bname = branch["1"]['branch']
                    uname = branch["1"]['name'].rstrip()

                    # create tooltip
                    details = []
                    for k, v in branch.items():
                        details.append([v["name"], v["ability"], v["challenge"], v["challengeprogress"][1]])

                    # remove useless entries
                    del branch["1"]["branch"]
                    del branch["1"]["name"]
                    del branch["1"]["ability"]
                    del branch["1"]["challenge"]

                    # add faction entries
                    branch["1"]["faction_order"] = 0
                    branch["1"]["faction_level"] = 0
                    branch["1"]["faction_cost"] = 0
                    branch["1"]["faction_multiplier"] = 0
                    branch["1"]["simu_order"] = 0
                    branch["1"]["simu_level"] = 0
                    branch["1"]["simu_cost"] = 0
                    branch["1"]["simu_multiplier"] = 0

                    # respects = [0]
                    respects = [0] + [v["base_cost"] for k, v in branch.items()]

                    # modify name css id
                    if len(branch) > 1:
                        uname = " ".join(uname.split(" ")[:-1]).rstrip()

                    if bname in upgradeTreeReshaped:
                        upgradeTreeReshaped[bname][uname] = branch["1"]
                    else:
                        upgradeTreeReshaped[bname] = {uname: branch["1"]}

                    upgradeTreeReshaped[bname][uname]["respect"] = respects
                    upgradeTreeReshaped[bname][uname]["levels"] = len(respects) - 1
                    upgradeTreeReshaped[bname][uname]["branchId"] = branchId
                    upgradeTreeReshaped[bname][uname]["details"] = details

                # compute base cost of each branch
                # for each branch
                # faction -> 0: base respect 1: respect 2: position
                # simulat -> 3: base respect 4: respect 5: position
                branchesCost = dict({"Core": [0, 0, 0, 0, 0, 0], "Criminality": [0, 0, 0, 0, 0, 0], "Fortitude": [0, 0, 0, 0, 0, 0], "Voracity": [0, 0, 0, 0, 0, 0], "Toleration": [0, 0, 0, 0, 0, 0], "Excursion": [0, 0, 0, 0, 0, 0], "Steadfast": [0, 0, 0, 0, 0, 0], "Aggression": [0, 0, 0, 0, 0, 0], "Suppression": [0, 0, 0, 0, 0, 0]})

                # create faction tree
                for branchId, branch in factionTree.items():
                    bname = branch['branch']
                    uname = branch['name'].rstrip()

                    # change name for levels branches
                    if upgradeTreeReshaped[bname].get(uname) is None:
                        uname = " ".join(uname.split(" ")[:-1]).rstrip()

                    order = branch["branchorder"]
                    multiplier = 2**(int(order) - 1) if order > 0 else 0
                    lvl = branch["level"]
                    res = upgradeTreeReshaped[bname][uname]["respect"]
                    upgradeTreeReshaped[bname][uname]["faction_order"] = order
                    upgradeTreeReshaped[bname][uname]["faction_multiplier"] = multiplier
                    upgradeTreeReshaped[bname][uname]["faction_level"] = lvl
                    upgradeTreeReshaped[bname][uname]["faction_cost"] = multiplier * numpy.sum(res[:lvl + 1])
                    upgradeTreeReshaped[bname][uname]["challengedone"] = branch["challengedone"]
                    upgradeTreeReshaped[bname][uname]["unsets_completed"] = branch.get("unsets_completed", "")
                    totalRespect["faction"] += upgradeTreeReshaped[bname][uname]["faction_cost"]

                    branchesCost[bname][0] += numpy.sum(res[:lvl + 1])
                    branchesCost[bname][1] += multiplier * numpy.sum(res[:lvl + 1])
                    branchesCost[bname][2] = order

                # update simu tree on the fly and branchesCost [3, 5]
                if request.POST.get('branchId') is not None:
                    modId = request.POST.get('branchId')
                    modModification = request.POST.get('modification')
                    modValue = request.POST.get('value')

                    # check consistency of the graph (necessary levels for the sub branches)
                    if modModification in ["level"]:
                        # modify the value in the simulation tree
                        if modId in simuTree:
                            simuTree[modId][modModification] = int(modValue)

                        # change branch level if the modification of the subbranch requires it
                        # lvl: level reuired
                        # {sb: [[b1, lvl1], [b2, lvl2]]}
                        r = {
                            # Toleration
                            27: [[29, 1]],  # side effect
                            28: [[29, 13]],  # overdosing

                            # Criminality
                            13: [[14, 2]],  # nerve
                            15: [[14, 2]],  # jail time
                            17: [[14, 2], [15, 10]],  # bust skill
                            16: [[14, 2], [15, 10], [17, 10]],  # bust nerve

                            # Excrusion
                            34: [[33, 2]],  # travel cost
                            31: [[33, 3]],  # hunting
                            35: [[33, 8]],  # rehab
                            32: [[33, 9]],  # oversea banking

                            # Supression
                            45: [[46, 3]],  # maximum life
                            48: [[47, 7]],  # escape

                            # Agression
                            44: [[43, 10]],  # accuracy
                            40: [[42, 3]],  # hospitalization
                            41: [[42, 15]],  # damage

                            # Fortitude
                            18: [[20, 2]],  # medical cooldown
                            19: [[20, 13]],  # reviving
                            21: [[20, 4]],  # life regeneration
                            22: [[20, 4], [21, 5]],  # medical effectiveness

                            # Voracity
                            23: [[25, 2]],  # candy effect
                            24: [[25, 15]],  # energy drink effect
                            26: [[25, 9]],  # alcohol effect

                            # Core
                            10: [[11, 2]],  # chaining
                            12: [[11, 2]],  # territory
                            }

                        if int(modId) in r and int(modValue):
                            for b, lvl in [(b[0], b[1]) for b in r[int(modId)]]:
                                print("couocu", b, lvl, simuTree[str(b)]['level'])
                                simuTree[str(b)]['level'] = max(lvl, simuTree[str(b)]['level'])

                        # change subbranch level to zero if the modification of the branch requires it
                        # sb: sub branch
                        # b: b branch
                        # {b: [[sb1, lvl1], [sb2, lvl2]]}
                        r = {
                            # Toleration
                            29: [[27, 1], [28, 13]],  # addiction

                            # Criminality
                            17: [[16, 10]],  # bust skill
                            15: [[17, 10], [16, 10]],  # jail time
                            14: [[15, 2], [13, 2], [17, 2], [16, 2]],  # crimes

                            # Excrusion
                            33: [[34, 2], [31, 3], [35, 8], [32, 9]],  # travel capacity

                            # Supression
                            46: [[45, 3]],  # defense
                            47: [[48, 7]],  # dexterity

                            # Agression
                            43: [[44, 10]],  # speed
                            42: [[40, 3], [41, 15]],  # strength

                            # Fortitude
                            20: [[18, 2], [21, 4], [22, 4], [19, 13]],   # hospitalization time
                            21: [[22, 5]],   # life regeneration

                            # Voracity
                            25: [[23, 2], [24, 15], [26, 9]],  # booster cooldown

                            # Core
                            11: [[10, 2], [12, 2]],  # capacity
                            }

                        if int(modId) in r:
                            for sb, lvl in [(sb[0], sb[1]) for sb in r[int(modId)]]:
                                simuTree[str(sb)]['level'] = 0 if int(modValue) < lvl else simuTree[str(sb)]['level']

                        # special case for steadfast
                        r = {
                            37: [36, 38, 39],  # speed training
                            36: [37, 38, 39],  # strength training
                            38: [39, 36, 37],  # defense training
                            39: [38, 36, 37],  # dexterity training
                            }

                        if int(modId) in r:
                            # max the close branch to 10
                            if int(modValue) > 10:
                                i = str(r[int(modId)][0])
                                simuTree[i]['level'] = min(10, simuTree[i]['level'])

                            # max the two other branches to 15
                            if int(modValue) > 15:
                                i = str(r[int(modId)][1])
                                simuTree[i]['level'] = min(15, simuTree[i]['level'])
                                i = str(r[int(modId)][2])
                                simuTree[i]['level'] = min(15, simuTree[i]['level'])

                        # special case for core
                        r = {
                            1: [],  # weapon armory
                            2: [1],  # armor armory
                            3: [1, 2],  # tempory armory
                            4: [1, 2],  # medical armory
                            5: [1, 2, 3],  # booster armory
                            6: [1, 2, 4],  # drug armory
                            7: [1, 2, 3, 4, 5, 6],  # point storage
                            8: [1, 2, 3, 4, 5, 6, 7],  # laboratory
                            }

                        if int(modId) in r:
                            if int(modValue):
                                for i in r[int(modId)]:
                                    simuTree[str(i)]['level'] = 1
                            else:
                                for k in [k for k, v in r.items() if int(modId) in v]:
                                    simuTree[str(k)]['level'] = 0

                        # optimize branch order
                        for k, v in simuTree.items():
                            bname = v["branch"]
                            uname = v["name"].rstrip()
                            if upgradeTreeReshaped[bname].get(uname) is None:
                                uname = " ".join(uname.split(" ")[:-1]).rstrip()
                            lvl = int(v["level"])
                            res = upgradeTreeReshaped[bname][uname]["respect"]
                            branchesCost[v["branch"]][3] += numpy.sum(res[:lvl + 1])

                        # update branch costs
                        for i, (k, v) in enumerate([(k, v) for (k, v) in sorted(branchesCost.items(), key=lambda x: -x[1][3]) if k not in ["Core"]]):
                            branchesCost[k][5] = i + 1 if branchesCost[k][3] else 0

                        # update branch order
                        for k, v in [(k, v) for (k, v) in simuTree.items() if v["branch"] not in ["Core"]]:
                            order = int(branchesCost[v["branch"]][5])
                            simuTree[k]["branchorder"] = order
                            simuTree[k]["branchmultiplier"] = 2**(int(order) - 1) if order > 0 else 0

                    # if modify branch order change all same branch order
                    if modModification in ['branchorder']:
                        # branch we modify the order modifying
                        a = [(k, v) for k, v in simuTree.items() if v['branch'] == simuTree[modId]['branch']]

                        if int(modValue):
                            # branch that has this order and we'll swap with above
                            b = [(k, v) for k, v in simuTree.items() if v['branchorder'] == int(modValue) and v['branch'] != simuTree[modId]['branch'] and v['branch'] not in ['Core']]
                            for k, v in b:
                                simuTree[k]['branchorder'] = simuTree[modId]['branchorder']

                        for k, v in a:
                            simuTree[k]['branchorder'] = int(modValue)
                            if not int(modValue):
                                simuTree[k]['level'] = 0

                    faction.simuTree = json.dumps(simuTree)
                    faction.save()

                # reset simu branch cost
                for k in branchesCost:
                    branchesCost[k][3] = 0
                    branchesCost[k][4] = 0
                    branchesCost[k][5] = 0

                # create simulation tree
                for branchId, branch in simuTree.items():
                    bname = branch['branch']
                    uname = branch['name'].rstrip()

                    # change name for levels branches
                    if upgradeTreeReshaped[bname].get(uname) is None:
                        uname = " ".join(uname.split(" ")[:-1]).rstrip()

                    order = int(branch["branchorder"])
                    multiplier = 2**(int(order) - 1) if order > 0 else 0
                    lvl = branch["level"]
                    res = upgradeTreeReshaped[bname][uname]["respect"]
                    upgradeTreeReshaped[bname][uname]["simu_order"] = order
                    upgradeTreeReshaped[bname][uname]["simu_multiplier"] = multiplier
                    upgradeTreeReshaped[bname][uname]["simu_level"] = lvl
                    upgradeTreeReshaped[bname][uname]["simu_cost"] = multiplier * numpy.sum(res[:lvl + 1])
                    totalRespect["simu"] += upgradeTreeReshaped[bname][uname]["simu_cost"]

                    branchesCost[bname][3] += numpy.sum(res[:lvl + 1])
                    branchesCost[bname][4] += multiplier * numpy.sum(res[:lvl + 1])
                    branchesCost[bname][5] = order

                # for k1, v1 in upgradeTreeReshaped.items():
                #     print(k1)
                #     for k2, v2 in v1.items():
                #         print(k2, v2)

                # upgrade key
                context = {'player': player,
                           'chaincat': True,
                           "faction": faction,
                           "upgradeTree": upgradeTreeReshaped,
                           "branchesCost": branchesCost,
                           "totalRespect": totalRespect,
                           'view': {'simu': True}}
                if request.method == 'POST':
                    page = 'chain/content-reload.html' if request.POST.get('change') is None else 'chain/respect-simulator-table.html'
                else:
                    page = 'chain.html'
                return render(request, page, context)

            else:
                return returnError(type=403, msg="You need AA rights.")

        else:
            return returnError(type=403, msg="You might want to log in.")

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
                faction.addKey(player.tId, player.getKey())
                faction.save()

                # gives the faction a crontab if not
                if not len(faction.crontab_set.all()):
                    openCrontab = Crontab.objects.filter(open=True).all()
                    minBusy = min([c.nFactions() for c in openCrontab])
                    for crontab in openCrontab:
                        if crontab.nFactions() == minBusy:
                            crontab.faction.add(faction)
                            crontab.save()
                            break
                    print('[view.chain.aa] attributed to {} '.format(crontab))

                # update members before to avoid coming here before having members
                updateMembers(faction, key=player.getKey(), force=False)

                # fill crontabs and keys
                crontabs = dict({})
                keys = [(faction.member_set.filter(tId=id).first(), k) for (id, k) in faction.getAllPairs() if faction.member_set.filter(tId=id).first() is not None]
                keysIgnored = [(id, k) for (id, k) in faction.getAllPairs() if faction.member_set.filter(tId=id).first() is None]

                for crontab in faction.crontab_set.all():
                    print('[view.chain.aa]     --> {}'.format(crontab))
                    crontabs[crontab.tabNumber] = {"crontab": crontab, "factions": []}
                    for f in crontab.faction.all():
                        crontabs[crontab.tabNumber]["factions"].append(f)

                # upgrade key
                context = {'player': player, 'chaincat': True, 'crontabs': crontabs, "bonus": BONUS_HITS, "faction": faction, 'keys': keys, 'keysIgnored': keysIgnored, 'view': {'aa': True}}
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

            messageDeleted = False
            if not faction.poster:
                faction.posterHold = False
                url = "{}/trees/{}.png".format(settings.STATIC_ROOT, faction.tId)
                if os.path.exists(url):
                    print('[view.chain.togglePoster] Delete faction {} poster at {}'.format(factionId, url))
                    os.remove(url)
                    messageDeleted = True
                else:
                    print('[view.chain.togglePoster] Try to delete faction {} poster at {} but file does not exist'.format(factionId, url))

            faction.save()

            context = {'faction': faction}
            if messageDeleted:
                context.update({'messageDeleted': messageDeleted})
            return render(request, 'chain/aa-poster.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


# action view
def togglePosterHold(request):
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

            if faction.poster:
                faction.posterHold = not faction.posterHold
            faction.save()

            context = {'faction': faction}
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

                    # hexa color code
                    if p == 4:
                        hex = request.POST.get("v").replace("#", "")[:8]
                        if len(hex) == 4:
                            tmp = hex
                            hex = ""
                            for i in range(4):
                                hex += tmp[i] + tmp[i]

                        elif len(hex) == 8:
                            pass

                        else:
                            hex = "FFFFFFFF"

                        try:
                            int(hex, 16)
                        except BaseException:
                            hex = "FFFFFFFF"

                        v = [int(hex[:2], 16), int(hex[2:4], 16), int(hex[4:6], 16), int(hex[6:8], 16)]

                    # decimal for one color
                    else:
                        v = int(request.POST.get("v", False))

                    if t:
                        print('[view.chain.tree] {}[{}] = {}'.format(t, p, v))
                        posterOpt = json.loads(faction.posterOpt)
                        if posterOpt.get(t, False):
                            if p == 4:
                                posterOpt[t] = v
                            else:
                                posterOpt[t][p] = v
                        else:
                            if t == "fontColor":
                                if p == 4:
                                    option = v
                                else:
                                    option = [0, 0, 0, 255]
                                    option[p] = v
                            elif t == "fontFamily":
                                option = [0]
                                option[p] = v
                            elif t == "iconType":
                                option = [0]
                                option[p] = v
                            elif t == "background":
                                if p == 4:
                                    option = v
                                else:
                                    option = [0, 0, 0, 0]
                                    option[p] = v

                            posterOpt[t] = option

                        faction.posterOpt = json.dumps(posterOpt)
                        faction.save()

                if not faction.posterHold:
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
    from bazaar.models import BazaarData

    try:
        ITEM_TYPE = json.loads(BazaarData.objects.first().itemType)
        if request.session.get('player'):
            print('[view.armory] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            player.save()
            faction = Faction.objects.filter(tId=player.factionId).first()

            if player.factionAA:
                print('[view.armory] player with AA. Faction {}'.format(faction))
                req = apiCall('faction', player.factionId, 'armorynewsfull,fundsnewsfull', player.getKey())
                if 'apiError' in req:
                    context = {'player': player, 'chaincat': True, 'faction': faction, "apiErrorSub": req["apiError"]}
                    page = 'chain/content-reload.html' if request.method == 'POST' else 'chain.html'
                    return render(request, page, context)

                armoryRaw = req["armorynews"]
                fundsRaw = req["fundsnews"]

                if faction.armoryRecord:
                    # armory
                    for k, v in json.loads(faction.armoryString).items():
                        if k not in armoryRaw:
                            armoryRaw[k] = v
                    faction.armoryString = json.dumps(armoryRaw)

                    # funds
                    for k, v in json.loads(faction.fundsString).items():
                        if k not in fundsRaw:
                            fundsRaw[k] = v
                    faction.fundsString = json.dumps(fundsRaw)
                else:
                    faction.armoryString = "{}"
                    faction.fundsString = "{}"
                    faction.networthString = "{}"

                faction.save()

            else:
                armoryRaw = json.loads(faction.armoryString)
                fundsRaw = json.loads(faction.fundsString)

            now = int(timezone.now().timestamp())
            timestamps = {"start": now, "end": 0, "fstart": now, "fend": 0, "size": 0}

            # delete armory out of timestamp
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

            # delete funds out of timestamp
            toDel = []
            for k, v in fundsRaw.items():
                if type(v) is not dict:
                    toDel.append(k)
                else:
                    ts = int(v.get("timestamp", 0))
                    timestamps["start"] = min(timestamps["start"], ts)
                    timestamps["end"] = max(timestamps["end"], ts)
                    if ts < int(request.POST.get("start", 0)) or ts > int(request.POST.get("end", now)):
                        toDel.append(k)
            for k in toDel:
                del fundsRaw[k]

            timestamps["fstart"] = request.POST.get("start", timestamps.get("start"))
            timestamps["fend"] = request.POST.get("end", timestamps.get("end"))
            timestamps["size"] = len(armoryRaw) + len(fundsRaw)

            armory = dict({})
            timestamps["nObjects"] = 0
            for k, v in armoryRaw.items():
                ns = cleanhtml(v.get("news", "")).split(" ")
                btype = "?"
                if 'used' in ns:
                    member = ns[0]
                    if ns[6] in ["points"]:
                        item = ns[6].title()
                        n = 25
                    else:
                        splt = " ".join(ns[6:-1]).split(":")
                        if len(splt) > 1:
                            btype = splt[-1].strip()
                        item = splt[0].strip()
                        # item = " ".join(ns[6:-1]).strip()
                        n = 1

                    timestamps["nObjects"] += n
                    if item in armory:
                        if member in armory[item]:
                            armory[item][member][0] += n
                            btypes = [t for t in armory[item][member][3].split(", ") if t not in ["?"]]
                            if btype not in btypes:
                                btypes.append(btype)
                                armory[item][member][3] = ", ".join(btypes)
                        else:
                            armory[item][member] = [n, 0, 0, btype]
                    else:
                        # new item and new member [taken, given, filled]
                        # print(btype)
                        armory[item] = {member: [n, 0, 0, btype]}

                elif 'deposited' in ns:
                    member = ns[0]
                    # print(ns)
                    n = int(ns[2].replace(",", "").replace("$", ""))
                    timestamps["nObjects"] += n
                    if ns[-1] in ["points"]:
                        item = ns[-1].title()
                    else:
                        splt = " ".join(ns[4:]).split(":")
                        if len(splt) > 1:
                            btype = splt[-1].strip()
                        item = splt[0].strip()
                        # item = " ".join(ns[4:]).strip()
                    if item in armory:
                        if member in armory[item]:
                            armory[item][member][1] += n
                            btypes = [t for t in armory[item][member][3].split(", ") if t not in ["?"]]
                            if btype not in btypes:
                                btypes.append(btype)
                                armory[item][member][3] = ", ".join(btypes)
                        else:
                            armory[item][member] = [0, n, 0, btype]
                    else:
                        # new item and new member [taken, given]
                        armory[item] = {member: [0, n, 0, btype]}

                # elif 'gave' in ns:
                #     print(ns)

                elif 'filled' in ns:
                    # print(ns)
                    member = ns[0]
                    item = "Blood Bag"
                    timestamps["nObjects"] += 1
                    if item in armory:
                        if member in armory[item]:
                            armory[item][member][2] += 1
                        else:
                            armory[item][member] = [0, 0, 1, btype]
                    else:
                        # new item and new member [taken, given, filled]
                        armory[item] = {member: [0, 0, 1, btype]}

            for k, v in fundsRaw.items():
                ns = cleanhtml(v.get("news", "")).split(" ")
                item = "Funds"
                member = ns[0]
                if item not in armory:
                    # was given, deposited, dummy, dummy
                    armory[item] = {member: [0, 0, 0, ""]}
                if member not in armory[item]:
                    armory[item][member] = [0, 0, 0, ""]

                if ns[1] == "was":
                    armory[item][member][0] += int(ns[3].replace("$", "").replace(",", "").replace(".", ""))
                elif ns[1] == "deposited":
                    armory[item][member][1] += int(ns[2].replace("$", "").replace(",", "").replace(".", ""))

            armoryType = {t: dict({}) for t in ITEM_TYPE}
            armoryType["Points"] = dict({})
            armoryType["Funds"] = dict({})

            for k, v in armory.items():
                for t, i in ITEM_TYPE.items():
                    # if k.split(" : ")[0] in i:
                    if k in i:
                        armoryType[t][k] = v
                        break
                if k in ["Points"]:
                    armoryType["Points"][k] = v

                if k in ["Funds"]:
                    armoryType["Funds"][k] = v

            networthGraph = json.loads(faction.networthString)
            tmp = [0, 0]
            for i, (k, v) in enumerate(sorted(networthGraph.items(), key=lambda x: x[0], reverse=False)):
                diff = v[0] - v[1]
                networthGraph[k].append(diff - tmp[0])
                networthGraph[k].append(v[2] - tmp[1])
                tmp = [diff, v[2]]

            context = {'player': player, 'networthGraph': sorted(networthGraph.items(), key=lambda x: x[0], reverse=True)[:-1], 'chaincat': True, 'faction': faction, "timestamps": timestamps, "armory": armoryType, 'view': {'armory': True}}
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
                # account for this wall only of faction id in wall.breakdown
                breakdown = json.loads(wall.breakdown)
                if str(faction.tId) in breakdown:
                    pass
                else:
                    continue

                aFac = "{} [{}]".format(wall.attackerFactionName, wall.attackerFactionId)
                dFac = "{} [{}]".format(wall.defenderFactionName, wall.defenderFactionId)

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


# action view
def toggleWall(request, wallId):
    try:
        if request.session.get('player') and request.method == 'POST':
            print('[view.chain.toggleWall] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            factionId = player.factionId

            if player.factionAA:
                faction = Faction.objects.filter(tId=factionId).first()
                if faction is None:
                    return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
                print('[view.chain.toggleWall] faction {} found'.format(factionId))

                wall = Wall.objects.filter(tId=wallId).first()
                breakdown = json.loads(wall.breakdown)

                if str(faction.tId) in breakdown:
                    # the wall was on we turn it off
                    breakdown = [id for id in breakdown if id != str(faction.tId)]
                    wall.breakSingleFaction = False
                else:
                    # the wall was off we turn it on
                    breakdown.append(str(faction.tId))
                    wall.breakSingleFaction = True

                wall.breakdown = json.dumps(breakdown)
                wall.save()

                context = {"player": player, "wall": wall}
                return render(request, 'chain/walls-line.html', context)
            else:
                return returnError(type=403, msg="You need AA rights.")

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


# API
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
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")
            print("Author in yata: checked")

            # check if API key is valid with api call
            HTTP_KEY = request.META.get("HTTP_KEY")
            call = apiCall('user', '', '', key=HTTP_KEY)
            if "apiError" in call:
                t = -1
                m = call
                print({"message": m, "type": t})
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")

            # check if API key sent == API key in YATA
            if HTTP_KEY != author.getKey():
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
                m = "Can't find faction {} in YATA database".format(author.factionId)
                print(m)
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")
            print("Faction exists: checked")

            attackers = dict({})
            defenders = dict({})
            i = 0
            for p in req.get("participants"):
                i += 1
                print("import wall, participants before: ", p)
                p = {k.split(" ")[0].strip(): v for k, v in p.items()}
                if p.get("Name")[0] == '=':
                    p["Name"] = p["Name"][2:-1]
                print("import wall, participants after: ", p)
                if p.get("Position") in ["Attacker"]:
                    attackers[p.get('XID')] = p
                else:
                    defenders[p.get('XID')] = p
            print("Wall Participants: {}".format(i))

            if i > 500:
                t = 0
                m = "{} is too much participants for a wall".format(i)
                print(m)
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")
            print("# Participant: checked")

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
            print("Wall headers: processed")

            if faction.tId not in [wallDic.get('attackerFactionId'), wallDic.get('defenderFactionId')]:
                t = 0
                m = "{} is not involved in this war".format(faction)
                print(m)
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")
            print("Faction in wall: checked")

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

            chain = faction.chain_set.filter(tId=wall.tId).first()
            if chain is None:
                chain = faction.chain_set.create(tId=wall.tId, start=wall.tss, end=wall.tse, wall=True)
                print("create chain:", chain)
            else:
                print("chain already exists:", chain)

            t = 1
            m = ", ".join(messageList)
            return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")

        except BaseException as e:
            t = 0
            m = "Server error... YATA's been poorly coded: {}".format(e)
            return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")

    else:
        return returnError(type=403, msg="You need to post. Don\'t try to be a smart ass.")


def territories(request):
    try:
        if request.session.get('player'):
            print('[view.chain.territories] get player id from session')
            tId = request.session["player"].get("tId")
        else:
            print('[view.chain.territories] anon session')
            tId = -1

        player = Player.objects.filter(tId=tId).first()
        factionId = player.factionId

        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
        print('[view.chain.territories] faction {} found'.format(factionId))

        # get faction territories
        print('[view.chain.territories] get faction territories')
        territories = Territory.objects.filter(faction=factionId)
        n = len(territories)
        x0 = 0.0
        y0 = 0.0
        summary = {"n": n, "daily_respect": 0.0}
        if n:
            for territory in territories:
                r = json.loads(territory.racket)
                if len(r):
                    territory.racket = "{name}: {reward}".format(**r)
                else:
                    territory.racket = ""
                x0 += territory.coordinate_x
                y0 += territory.coordinate_y
                territory.factionName = faction.name
                summary["daily_respect"] += territory.daily_respect
                summary["factionName"] = territory.factionName
                summary["faction"] = territory.faction

            x0 /= n
            y0 /= n
            summary["coordinate_x"] = x0
            summary["coordinate_y"] = y0

        print('[view.chain.territories] get all territories')
        allTerritories = Territory.objects.all()

        print('[view.chain.territories] get rackets')
        rackets = Racket.objects.all()
        for racket in rackets:
            t = allTerritories.filter(tId=racket.tId).first()
            x = t.coordinate_x
            y = t.coordinate_y
            r = t.daily_respect
            racket.coordinate_x = x
            racket.coordinate_y = y
            racket.daily_respect = r
            racket.distance = ((x - x0)**2 + (y - y0)**2)**0.5
            if racket.faction:
                tmp = Faction.objects.filter(tId=racket.faction).first()
                if tmp is not None:
                    racket.factionName = tmp.name
                else:
                    racket.factionName = "Faction"
            else:
                racket.factionName = "-"

        territoryTS = FactionData.objects.first().territoryTS
        context = {'player': player, 'chaincat': True, 'faction': faction, 'rackets': rackets, 'territoryTS': territoryTS, 'territories': territories, 'summary': summary, 'view': {'territories': True}}
        page = 'chain/content-reload.html' if request.method == 'POST' else 'chain.html'
        return render(request, page, context)

    except Exception:
        return returnError()


# action view
def territoriesFullGraph(request):
    try:
        if request.method == 'POST':
            if request.session.get('player'):
                print('[view.chain.territories] get player id from session')
                tId = request.session["player"].get("tId")
            else:
                print('[view.chain.territoriesFullGraph] anon session')
                tId = -1

            player = Player.objects.filter(tId=tId).first()
            factionId = player.factionId

            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
            print('[view.chain.territories] faction {} found'.format(factionId))

            # get faction territories
            territories = Territory.objects.filter(faction=factionId)
            n = len(territories)
            x0 = 2568.97
            y0 = 2479.89
            summary = {"n": n, "daily_respect": 0.0}
            if n:
                for territory in territories:
                    r = json.loads(territory.racket)
                    if len(r):
                        territory.racket = "{name}: {reward}".format(**r)
                    else:
                        territory.racket = ""
                    x0 += territory.coordinate_x
                    y0 += territory.coordinate_y
                    territory.factionName = faction.name
                    summary["daily_respect"] += territory.daily_respect
                    summary["factionName"] = territory.factionName
                    summary["faction"] = territory.faction

                x0 /= n
                y0 /= n
                summary["coordinate_x"] = x0
                summary["coordinate_y"] = y0

            allTerritories = Territory.objects.all()
            for territory in allTerritories:
                tmp = Faction.objects.filter(tId=territory.faction).first()
                if tmp is not None:
                    territory.factionName = tmp.name
                else:
                    territory.factionName = "Faction"

            rackets = Racket.objects.all()
            for racket in rackets:
                t = allTerritories.filter(tId=racket.tId).first()
                x = t.coordinate_x
                y = t.coordinate_y
                r = t.daily_respect
                racket.coordinate_x = x
                racket.coordinate_y = y
                racket.daily_respect = r
                racket.distance = ((x - x0)**2 + (y - y0)**2)**0.5
                if racket.faction:
                    tmp = Faction.objects.filter(tId=racket.faction).first()
                    if tmp is not None:
                        racket.factionName = tmp.name
                    else:
                        racket.factionName = "Faction"

            context = {'faction': faction, 'rackets': rackets, 'territories': territories, 'summary': summary, 'allTerritories': allTerritories}
            return render(request, 'chain/territories-graph-full.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


def bigBrother(request):
    try:
        if request.session.get('player'):
            print('[view.chain.bigBrother] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            factionId = player.factionId

            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
            print('[view.chain.bigBrother] faction {} found'.format(factionId))

            bridge = {
                "criminaloffences": "Offences",
                "busts": "Busts",
                "jails": "Jail sentences",
                "drugsused": "Drugs taken",
                "drugoverdoses": "Overdoses",
                "gymstrength": "Energy on strength",
                "gymspeed": "Energy on speed",
                "gymdefense": "Energy on defense",
                "gymdexterity": "Energy on dexterity",
                "traveltime": "Hours of flight",
                "hunting": "Hunts",
                "rehabs": "Rehabs",
                "caymaninterest": "Interest in Cayman",
                "medicalcooldownused": "Medical cooldown",
                "revives": "Revives",
                "medicalitemrecovery": "Life recovered",
                "hosptimereceived": "Hospital received",
                "candyused": "Candy used",
                "alcoholused": "Alcohol used",
                "energydrinkused": "Energy drinks used",
                "hosptimegiven": "Hospital given",
                "attacksdamagehits": "Damaging hits",
                "attacksdamage": "Damage dealt",
                "attacksdamaging": "Damage received",
                "attacksrunaway": "Runaways",
                "allgyms": "Energy training",
                # "": "",
                }

            error = False
            message = False
            if request.POST.get('add', False) and player.factionAA:
                addType = request.POST.get('add')
                ts = int(timezone.now().timestamp())
                ts = ts - ts % 3600

                # check if already added this hour
                if faction.stat_set.filter(timestamp=ts).filter(name=addType).first() is not None:
                    error = "{} already added this hour. Try later.".format(bridge[addType])
                    req = False
                else:
                    req = apiCall("faction", "", "timestamp,contributors&stat={}".format(addType), key=player.getKey())

                # check api error
                if req and 'apiError' in req:
                    error = req["apiError"] + " can't add challenge."

                # check if wrong type (due to cache)
                elif req and addType not in req["contributors"]:
                    delay = 32 - (int(timezone.now().timestamp()) - int(req["timestamp"]))
                    error = "You have to wait at least 30 seconds between different entries because of API cache (wait {}s).".format(delay)

                # should be good -> add entry
                elif req:
                    newStat = dict({})
                    newStat["timestamp"] = ts
                    # newStat["type"] = addType
                    newStat["name"] = addType
                    contributors = dict({})
                    members = faction.member_set.all()
                    for k, v in [(k, v["contributed"]) for k, v in req["contributors"][addType].items() if v["in_faction"]]:
                        m = members.filter(tId=int(k)).first()
                        memberName = m.name if m is not None else "Player"
                        contributors[k] = [memberName, v]
                    newStat["contributors"] = json.dumps(contributors)
                    faction.stat_set.create(**newStat)
                    message = "{} added at {}".format(bridge[addType], timestampToDate(ts))

            # get all stats
            allStats = faction.stat_set.all().order_by('timestamp')

            # add on the fly 4 gyms
            # loop over unique ts
            gymsKeys = ["gymstrength", "gymspeed", "gymdefense", "gymdexterity"]
            for uniqueTS in set([s.timestamp for s in allStats]):
                gyms = []
                for tsStat in allStats.filter(timestamp=uniqueTS):
                    if tsStat.name in gymsKeys:
                        gyms.append(tsStat)

                if len(gyms) == 4:
                    if allStats.filter(name="allgyms", timestamp=uniqueTS).first() is None:
                        print("create all gym")
                        newStat = {"timestamp": gyms[0].timestamp, "name": "allgyms"}
                        contributors = dict({})
                        for gym in gyms:
                            for k, v in json.loads(gym.contributors).items():
                                if k in contributors:
                                    contributors[k][1] += v[1]
                                else:
                                    contributors[k] = v
                        newStat["contributors"] = json.dumps(contributors)
                        faction.stat_set.create(**newStat)
                        allStats = faction.stat_set.all().order_by('timestamp')

            statsList = dict({})
            contributors = False
            comparison = False
            for stat in allStats:
                # create entry if first iteration on this type
                if stat.name not in statsList:
                    statsList[stat.name] = []

                # enter contributors
                realName = bridge.get(stat.name, stat.name)
                statsList[stat.name].append([realName, stat.timestamp])

            if request.POST.get('name', False):
                name = request.POST.get('name')
                tsA = int(request.POST.get('tsA'))
                tsB = int(request.POST.get('tsB'))
                comparison = [name, tsA, tsB, str(name)]

                # select first timestamp
                stat = allStats.filter(name=name, timestamp=tsA).first()
                contributors = dict({})
                # in case they remove stat and select it before refraising
                if stat is not None:
                    comparison[3] = bridge.get(stat.name, stat.name)
                    for k, v in json.loads(stat.contributors).items():
                        contributors[bridge.get(k, k)] = [v[0], v[1], 0]

                    # select second timestamp
                    if tsB > 0:
                        stat = allStats.filter(name=name, timestamp=tsB).first()
                        for k, v in json.loads(stat.contributors).items():
                            memberName = bridge.get(k, k)
                            # update 3rd column if already in timestamp A
                            if k in contributors:
                                contributors[memberName][2] = v[1]
                            # add if new
                            else:
                                contributors[memberName] = [v[0], 0, v[1]]
                            c = contributors[memberName]
                            if not c[2] - c[1]:
                                del contributors[memberName]

            context = {'player': player, 'chaincat': True, 'faction': faction, 'statsList': statsList, 'contributors': contributors, 'comparison': comparison, 'bridge': bridge, 'view': {'bigBrother': True}}
            if error:
                context["apiErrorSub"] = error
            if message:
                context["validMessageSub"] = message
            if request.method == 'POST':
                page = 'chain/content-reload.html' if request.POST.get('name') is None else 'chain/big-brother-table.html'
            else:
                page = 'chain.html'
            return render(request, page, context)

        else:
            message = "You might want to log in."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


# action view
def removeUpgrade(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            print('[view.chain.removeUpgrade] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            factionId = player.factionId

            if player.factionAA:
                faction = Faction.objects.filter(tId=factionId).first()
                if faction is None:
                    return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
                print('[view.chain.removeUpgrade] faction {} found'.format(factionId))

                s = faction.stat_set.filter(name=request.POST.get('name')).filter(timestamp=request.POST.get('ts')).first()
                try:
                    s.delete()
                    m = "Okay"
                    t = 1
                except BaseException as e:
                    m = str(e)
                    t = -1

                print(m)
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")
            else:
                return returnError(type=403, msg="You need AA rights.")

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()

@csrf_exempt
def importUpgrades(request):
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
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")
            print("Author in yata: checked")

            # check if API key is valid with api call
            HTTP_KEY = request.META.get("HTTP_KEY")
            call = apiCall('user', '', '', key=HTTP_KEY)
            if "apiError" in call:
                t = -1
                m = call
                print({"message": m, "type": t})
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")

            # check if API key sent == API key in YATA
            if HTTP_KEY != author.getKey():
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
                m = "Can't find faction {} in YATA database".format(author.factionId)
                print(m)
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")
            print("Faction exists: checked")

            #  check if can read type and name
            if not req.get('type', False) or not req.get('name', False):
                t = 0
                m = "Can't read the upgrade type or name... weird".format(author.factionId)
                print(m)
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")
            print("Read upgrade type and name: checked")

            contributors = req.get("contributors", dict({}))
            del req["author"]
            req["contributors"] = dict({})
            for c in [c for c in contributors if not c.get("exmember", True)]:
                del c["exmember"]
                req["contributors"][c["userid"]] = [c["playername"], c["total"]]

            ts = int(timezone.now().timestamp())
            ts = ts - ts % 3600
            req["timestamp"] = ts
            req["contributors"] = json.dumps(req["contributors"])
            if faction.stat_set.filter(timestamp=ts).filter(type=req.get('type')).first() is not None:
                t = 0
                m = "Stat already imported this hour."
            else:
                t = 1
                m = "{} as been imported".format(req.get('name', False))
                faction.stat_set.create(**req)

            return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")

        except BaseException as e:
            t = 0
            m = "Server error... YATA's been poorly coded: {}".format(e)
            return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")

    else:
        return returnError(type=403, msg="You need to post. Don\'t try to be a smart ass.")


def importFakeWall(request):
    try:
        if request.method == 'GET' and len(request.GET) and request.GET.get("ts", False):
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            factionId = player.factionId
            faction = Faction.objects.filter(tId=factionId).first()

            chain = faction.chain_set.filter(tId=1).first()
            if chain is not None:
                chain.delete()
            chain = faction.chain_set.create(tId=1, start=int(request.GET.get("ts", False)), end=int(timezone.now().timestamp()), wall=True)

            return redirect('/chain/')
        else:
            return returnError(type=403, msg="You need to set a GET date. Don\'t try to be a smart ass.")
    except Exception:
        return returnError()


# render view
def contracts(request):
    try:
        if request.session.get('player'):
            print('[view.chain.list] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            player.save()

            key = player.getKey()
            factionId = player.factionId
            page = 'chain/content-reload.html' if request.method == 'POST' else 'chain.html'

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Click on chain report again please."}
                return render(request, page, context)

            # delete contract
            if request.POST.get("delete", False):
                contract = faction.revivecontract_set.filter(pk=request.POST["contractId"])
                contract.delete()
                # dummy render
                return render(request, page)

            # create contract
            elif 'tsStart' in request.POST and 'tsEnd' in request.POST:
                tsStart = int(request.POST['tsStart'])
                tsEnd = int(request.POST['tsEnd'])
                if tsStart < tsEnd:
                    faction.revivecontract_set.create(start=tsStart, end=tsEnd, computing=True, owner=True)

            # modify end date
            elif request.POST.get('tsEnd', False):
                tsEnd = int(request.POST['tsEnd'])
                contractId = int(request.POST['contractId'])
                contract = faction.revivecontract_set.filter(pk=contractId).first()
                if contract.start < tsEnd:
                    if contract.end > tsEnd:
                        # delete revive > end
                        nrevives = 0
                        for r in contract.revive_set.all():
                            if r.timestamp > contract.end:
                                r.delete()
                            else:
                                nrevives += 1
                        contract.revivesContract = nrevives
                    else:
                        contract.computing = True

                    contract.end = tsEnd
                    contract.save()
                    context = {'player': player, 'faction': faction, 'contract': contract}

            # get contracts
            contracts = faction.revivecontract_set.all().order_by('-end')

            context = {'player': player, 'faction': faction, 'chaincat': True, 'contracts': contracts, 'view': {'contracts': True}}

            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


def contract(request, contractId):
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

            # get contracts
            contracts = faction.revivecontract_set.all()

            # get contract
            contract = contracts.filter(pk=contractId).first()

            if contract is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, 'faction': faction, selectError: "Contract not found."}
                return render(request, page, context)
            print('[view.chain.report] contract {} found'.format(contractId))

            factionsRevivers = json.loads(contract.factionsRevivers)
            factionsTargets = json.loads(contract.factionsTargets)

            # if click on shared
            if request.POST.get("type") == "revivers":
                if int(request.POST["factionId"]) in factionsRevivers:
                    factionsRevivers.remove(int(request.POST["factionId"]))
                else:
                    factionsRevivers.append(int(request.POST["factionId"]))
                contract.factionsRevivers = json.dumps(factionsRevivers)
            elif request.POST.get("type") == "targets":
                if int(request.POST["factionId"]) in factionsTargets:
                    factionsTargets.remove(int(request.POST["factionId"]))
                else:
                    factionsTargets.append(int(request.POST["factionId"]))
                contract.factionsTargets = json.dumps(factionsTargets)

            revives = dict({})
            revivesMade = 0
            revivesReceived = 0
            contract.last = 0
            contract.first = 0
            for r in contract.revive_set.all():
                revives[r.tId] = model_to_dict(r)
                if r.target_faction in factionsTargets:
                    revives[r.tId]["show"] = True
                    revivesReceived += 1
                    contract.last = max(contract.last, r.timestamp) if contract.last else r.timestamp
                    contract.first = min(contract.first, r.timestamp) if contract.first else r.timestamp
                elif r.reviver_faction in factionsRevivers:
                    revives[r.tId]["show"] = True
                    revivesMade += 1
                    contract.last = max(contract.last, r.timestamp) if contract.last else r.timestamp
                    contract.first = min(contract.first, r.timestamp) if contract.first else r.timestamp
                else:
                    revives[r.tId]["show"] = False

            contract.revivesMade = revivesMade
            contract.revivesReceived = revivesReceived
            contract.revivesContract = len(revives)
            contract.save()

            breakdown = dict({"target_factions": dict({}), "reviver_factions": dict({}), "revivers": dict({}), "targets": dict({})})
            # point of view of the revivers
            if contract.owner:
                for k, v in revives.items():
                    # add traget faction
                    if v["target_faction"] in breakdown["target_factions"]:
                        breakdown["target_factions"][v["target_faction"]]["revives"] += 1
                    else:
                        shared = True if v["target_faction"] in factionsTargets else False
                        breakdown["target_factions"][v["target_faction"]] = {"revives": 1, "name": v["target_factionname"], "show": shared}

                    # add reviver faction
                    if v["reviver_faction"] in breakdown["reviver_factions"]:
                        breakdown["reviver_factions"][v["reviver_faction"]]["revives"] += 1
                    else:
                        shared = True if v["reviver_faction"] in factionsRevivers else False
                        breakdown["reviver_factions"][v["reviver_faction"]] = {"revives": 1, "name": v["reviver_factionname"], "show": shared}

                    # add reviver
                    if v["reviver_faction"] in factionsRevivers:
                        if v["reviver_id"] in breakdown["revivers"]:
                            breakdown["revivers"][v["reviver_id"]]["revives"] += 1
                        else:
                            breakdown["revivers"][v["reviver_id"]] = {"revives": 1, "name": v["reviver_name"], "faction": v["reviver_faction"], "factionname": v["reviver_factionname"]}

                    # add target
                    if v["target_faction"] in factionsTargets:
                        if v["target_id"] in breakdown["targets"]:
                            breakdown["targets"][v["target_id"]]["revives"] += 1
                        else:
                            breakdown["targets"][v["target_id"]] = {"revives": 1, "name": v["target_name"], "faction": v["target_faction"], "factionname": v["target_factionname"]}

            # convert factions to dictionnary for the template
            # do not save
            contract.factionsRevivers = json.loads(contract.factionsRevivers)
            contract.factionsTargets = json.loads(contract.factionsTargets)

            # context
            context = dict({"player": player,
                            'chaincat': True,
                            'faction': faction,
                            'contracts': contracts,
                            'contract': contract,
                            'revives': revives,
                            'breakdown': breakdown,
                            'view': {'contract': True}})  # views

            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


def attacks(request):
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

            # create new breakdown
            if 'tsStart' in request.POST:
                tss = int(request.POST.get("tsStart", 0))
                tse = int(request.POST.get("tsEnd", 0))
                if int(request.POST.get("live", False)):
                    print("new live breakdown")
                    faction.attacksbreakdown_set.all().delete()
                    faction.attacksbreakdown_set.create(tss=tss, tse=0, live=True, computing=True)
                elif tse:
                    if tss < tse:
                        print("new normal breakdown")
                        faction.attacksbreakdown_set.all().delete()
                        faction.attacksbreakdown_set.create(tss=tss, tse=tse, live=False, computing=True)


            # if click on delete
            if int(request.POST.get("delete", 0)):
                faction.attacksbreakdown_set.all().delete()

            # get breakdown
            attacksBreakdown = faction.attacksbreakdown_set.first()
            if attacksBreakdown is None:
                context = dict({"player": player,
                                'chaincat': True,
                                'faction': faction,
                                'attacksBreakdown': False,
                                'view': {'attacks': True}})  # views
                return render(request, page, context)

            # if modify end date
            if 'modifyEnd' in request.POST:
                tse = int(request.POST.get("tsEnd", 0))
                if attacksBreakdown.tss < tse:
                    attacksBreakdown.tse = tse
                    attacksBreakdown.live = False
                    attacksBreakdown.computing = True
                    attacksBreakdown.attack_set.filter(timestamp_ended__gt=tse).delete()
                    attacksBreakdown.save()

            attackerFactions = json.loads(attacksBreakdown.attackerFactions)
            defenderFactions = json.loads(attacksBreakdown.defenderFactions)

            # if click on toggle
            if request.POST.get("type") == "attackers":
                print(int(request.POST["factionId"]))
                if int(request.POST["factionId"]) in attackerFactions:
                    attackerFactions.remove(int(request.POST["factionId"]))
                else:
                    attackerFactions.append(int(request.POST["factionId"]))
                attacksBreakdown.attackerFactions = json.dumps(attackerFactions)
            elif request.POST.get("type") == "defenders":
                if int(request.POST["factionId"]) in defenderFactions:
                    defenderFactions.remove(int(request.POST["factionId"]))
                else:
                    defenderFactions.append(int(request.POST["factionId"]))
                attacksBreakdown.defenderFactions = json.dumps(defenderFactions)
            attacksBreakdown.save()

            attacks = dict({})
            attacksMade = 0
            attacksReceived = 0
            for r in attacksBreakdown.attack_set.all():
                attacks[r.tId] = model_to_dict(r)
                if not r.attacker_id:
                    attacks[r.tId]["attacker_name"] = "Stealth"
                    attacks[r.tId]["attacker_factionname"] = "Stealth"
                    attacks[r.tId]["attacker_id"] = 1
                    attacks[r.tId]["attacker_faction"] = 1

                if attacks[r.tId]["defender_faction"] in defenderFactions:
                    attacks[r.tId]["show"] = True
                    attacksReceived += 1
                elif attacks[r.tId]["attacker_faction"] in attackerFactions:
                    attacks[r.tId]["show"] = True
                    attacksMade += 1
                else:
                    attacks[r.tId]["show"] = False

            attacksBreakdown.attacks = attacksMade
            attacksBreakdown.defends = attacksReceived

            breakdown = dict({"defender_factions": dict({}), "attacker_factions": dict({}), "attackers": dict({}), "defenders": dict({}), "players": dict({})})
            for k, v in attacks.items():
                winAtt = 0 if v["result"] in ["Lost"] else 1
                winDef = 1 if v["result"] in ["Lost"] else 0

                # add defender faction
                if v["defender_faction"] in breakdown["defender_factions"]:
                    breakdown["defender_factions"][v["defender_faction"]]["attacked"] += 1
                    breakdown["defender_factions"][v["defender_faction"]]["defends"] += winDef
                else:
                    show = True if v["defender_faction"] in defenderFactions else False
                    breakdown["defender_factions"][v["defender_faction"]] = {"attacks": 0, "wins": 0, "attacked": 1, "defends": winDef, "name": v["defender_factionname"], "show": show}

                # add attacker faction
                if v["attacker_faction"] in breakdown["attacker_factions"]:
                    breakdown["attacker_factions"][v["attacker_faction"]]["attacks"] += 1
                    breakdown["attacker_factions"][v["attacker_faction"]]["wins"] += winAtt
                else:
                    show = True if v["attacker_faction"] in attackerFactions else False
                    breakdown["attacker_factions"][v["attacker_faction"]] = {"attacks": 1, "wins": winAtt, "attacked": 0, "defends": 0, "name": v["attacker_factionname"], "show": show}

                # add attacker
                if v["attacker_faction"] in attackerFactions:
                    if v["attacker_id"] in breakdown["players"]:
                        breakdown["players"][v["attacker_id"]]["attacks"] += 1
                        breakdown["players"][v["attacker_id"]]["wins"] += winAtt
                    else:
                        breakdown["players"][v["attacker_id"]] = {"attacks": 1, "wins": winAtt, "attacked": 0, "defends": 0, "name": v["attacker_name"], "faction": v["attacker_faction"], "factionname": v["attacker_factionname"]}

                # add defender
                if v["defender_faction"] in defenderFactions:
                    if v["defender_id"] in breakdown["players"]:
                        breakdown["players"][v["defender_id"]]["attacked"] += 1
                        breakdown["players"][v["defender_id"]]["defends"] += winDef
                    else:
                        breakdown["players"][v["defender_id"]] = {"attacks": 0, "wins": 0, "attacked": 1, "defends": winDef, "name": v["defender_name"], "faction": v["defender_faction"], "factionname": v["defender_factionname"]}

            # # convert factions to dictionnary for the template
            # # do not save
            attackerFactions = json.loads(attacksBreakdown.attackerFactions)
            defenderFactions = json.loads(attacksBreakdown.defenderFactions)

            # context
            context = dict({"player": player,
                            'chaincat': True,
                            'faction': faction,
                            'attacksBreakdown': attacksBreakdown,
                            'attacks': attacks,

                            # 'contracts': contracts,
                            # 'contract': contract,
                            'breakdown': breakdown,
                            'view': {'attacks': True}})  # views

            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()
