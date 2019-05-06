from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone

import numpy
from scipy import stats
import json

from player.models import Player

from yata.handy import apiCall
from yata.handy import timestampToDate

from chain.functions import apiCallAttacks
from chain.functions import fillReport
from chain.functions import BONUS_HITS
from chain.functions import updateMembers

from chain.models import Faction
from chain.models import Member
from chain.models import Preference

preferences = Preference.objects.first()

# render view
def index(request):
    if request.session.get('player'):
        print('[view.chain.index] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        key = player.key
        context = {"player": player, "chain": True}

        # get user info
        error = False
        user = apiCall('user', '', 'profile', key)
        if 'apiError' in user:
            error = user

        if not error:
            # try:
            factionId = int(user.get("faction")["faction_id"])
            allowedFactions = json.loads(preferences.allowedFactions) if preferences is not None else []
            if factionId in allowedFactions:
                player.chainInfo = user.get("faction")["faction_name"]
                player.factionId = factionId
                if 'chains' in apiCall('faction', factionId, 'chains', key):
                    player.chainInfo += " [AA]"
                    player.factionAA = True
                player.lastUpdateTS = int(timezone.now().timestamp())
                player.save()
                print('[view.chain.index] player in faction {}'.format(player.chainInfo))
            else:
                print('[view.chain.index] player in non registered faction {}'.format(user.get("faction")["faction_name"]))
                context = {"player": player, "errorMessage": "Faction not registered. PM Kivou [2000607] for details."}
                return render(request, 'chain.html', context)

            # except:
            #     player.chainInfo = "N/A"
            #     player.factionId = 0
            #     player.factionAA = False
            #     player.save()
            #     context.update({"errorMessage": "You're not in any faction"})
            #     print('[view.chain.index] player without faction')
            #     return render(request, 'chain.html', context)

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
                faction.add_key(player.name, player.key)
                faction.save()

        else:
            print("[view.chain.index] api error {}".format(error))
            context.update(error)
            return render(request, 'chain.html', context)

        # render if logged
        chains = faction.chain_set.filter(status=True).order_by('-end')
        context.update({'chains': chains, 'view': {'list': True}})
        return render(request, 'chain.html', context)

    # logout if no session
    return HttpResponseRedirect(reverse('logout'))


def live(request):
    if request.session.get('player'):
        print('[view.chain.index] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        factionId = player.factionId
        key = player.key
        context = {"player": player, "chain": True}

        # get live chain and next bonus
        liveChain = apiCall('faction', factionId, 'chain', key, sub='chain')
        if 'apiError' in liveChain:
            context.update(liveChain)
            return render(request, 'chain.html', context)

        activeChain = bool(liveChain['current'])
        print("[view.chain.index] live chain: {}".format(activeChain))
        liveChain["nextBonus"] = 10
        for i in BONUS_HITS:
            liveChain["nextBonus"] = i
            if i >= int(liveChain["current"]):
                break

        faction = Faction.objects.filter(tId=factionId).first()
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
                counts = report.count_set.all()
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
                ETA = timestampToDate(int((liveChain["nextBonus"] - b) / a))
                graph['info']['ETALast'] = ETA
                graph['info']['regLast'] = [a, b]

                a, b, _, _, _ = stats.linregress(x, y)
                ETA = timestampToDate(int((liveChain["nextBonus"] - b) / a))
                graph['info']['ETA'] = ETA
                graph['info']['reg'] = [a, b]

            else:
                print('[view.chain.index] no data found for graph')
                graph = {'data': [], 'info': {'binsTime': 5, 'criticalHits': 1}}

            # context
            context.update({'faction': faction, 'chain': chain, 'bonus': bonus, 'counts': counts, 'view': {'report': True, 'liveReport': True}, 'graph': graph})

        # no active chain
        else:
            chain = faction.chain_set.filter(tId=0).first()
            if chain is not None:
                chain.delete()
                print('[view.chain.index] chain 0 deleted')
            context.update({'faction': faction, 'chain': True, 'view': {'report': True, 'liveReport': True}})  #  set chain to True to display category links

        # context
        context.update({'faction': faction, 'liveChain': liveChain})
        if request.method == 'POST':
            return render(request, 'chain/content-reload.html', context)
        else:
            return render(request, 'chain.html', context)



    return HttpResponseRedirect(reverse('logout'))


# render view
def list(request):
    if request.session.get('player'):
        print('[view.chain.list] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        key = player.key
        factionId = player.factionId
        context = {"player": player}

        # get faction
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            print('[view.chain.list] faction {} not found'.format(factionId))
            return HttpResponseRedirect(reverse('logout'))
        else:
            print('[view.chain.list] faction {} found'.format(factionId))

        # update chains if AA
        if player.factionAA:
            chains = apiCall('faction', faction.tId, 'chains', key, sub='chains')
            if 'apiError' in chains:
                context.update(chains)

            else:
                for k, v in chains.items():
                    chain = faction.chain_set.filter(tId=k).first()
                    if v['chain'] >= faction.hitsThreshold:
                        if chain is None:
                            print('[view.chain.list] chain {} created'.format(k))
                            faction.chain_set.create(tId=k, nHits=v['chain'], respect=v['respect'],
                                                     start=v['start'],
                                                     end=v['end'])
                        else:
                            print('[view.chain.list] chain {} updated'.format(k))
                            chain.start = v['start']
                            chain.end = v['end']
                            chain.nHits = v['chain']
                            # chain.reportNHits = 0
                            chain.respect = v['respect']
                            chain.save()

                    else:
                        if chain is not None:
                            print('[view.chain.list] chain {} deleted'.format(k))
                            chain.delete()

        # get chains
        chains = faction.chain_set.filter(status=True).order_by('-end')

        # context
        context.update({'chains': chains, 'view': {'list': True}})
        if request.method == 'POST':
            return render(request, 'chain/content-reload.html', context)
        else:
            return render(request, 'chain.html', context)

    return HttpResponseRedirect(reverse('logout'))


# render view
def report(request, chainId):
    if request.session.get('player'):
        print('[view.chain.list] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        factionId = player.factionId

        # get faction
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            return render(request, 'chain.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId), "player": player, "chain": True})
        print('[VIEW report] faction {} found'.format(factionId))

        # get chain
        chain = faction.chain_set.filter(tId=chainId).first()
        if chain is None:
            return render(request, 'chain.html', {'errorMessage': 'Chain {} not found in the database.'.format(chainId), "player": player, "chain": True})
        print('[VIEW report] chain {} found'.format(chainId))

        # get report
        report = chain.report_set.filter(chain=chain).first()
        if report is None:
            # context
            print('[VIEW report] report of {} not found'.format(chain))
            context = dict({"player": player,
                            'chain': chain,  # for general info
                            'view': {'report': True}})  # views
            if request.method == 'POST':
                return render(request, 'chain/content-reload.html', context)
            else:
                return render(request, 'chain.html', context)

        print('[VIEW report] report of {} found'.format(chain))

        # create graph
        graphSplit = chain.graph.split(',')
        if len(graphSplit) > 1:
            print('[VIEW report] data found for graph of length {}'.format(len(graphSplit)))
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
            print('[VIEW report] no data found for graph')
            graph = {'data': [], 'info': {'binsTime': 5, 'criticalHits': 1, 'speedRate': 0}}

        # context
        context = dict({"player": player,
                        'chain': chain,  # for general info
                        'chains': faction.chain_set.filter(status=True).order_by('-end'),  # for chain list after report
                        'counts': report.count_set.all(),  # for report
                        'bonus': report.bonus_set.all(),  # for report
                        'graph': graph,  # for report
                        'view': {'report': True}})  # views

        # render if logged
        if request.method == 'POST':
            return render(request, 'chain/content-reload.html', context)
        else:
            return render(request, 'chain.html', context)

    return HttpResponseRedirect(reverse('logout'))


# render view
def jointReport(request):
    if request.session.get('player'):
        print('[view.chain.list] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        factionId = player.factionId

        # get faction
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
        print('[VIEW jointReport] faction {} found'.format(factionId))

        # get chains
        chains = faction.chain_set.filter(jointReport=True).order_by('start')
        print('[VIEW jointReport] {} chains for the joint report'.format(len(chains)))
        if len(chains) < 1:
            context = {'errorMessage': 'No chains found for the joint report.',
                          'chains': faction.chain_set.filter(status=True).order_by('-end'),
                          'player': player}
            return render(request, 'chain/list.html', context)

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
                if bonus.name in bonuses:
                    bonuses[bonus.name][0].append(bonus.hit)
                    bonuses[bonus.name][1] += bonus.respect
                else:
                    bonuses[bonus.name] = [[bonus.hit], bonus.respect, 0]

            for count in chainCounts:

                if count.attackerId in counts:
                    counts[count.attackerId]['hits'] += count.hits
                    counts[count.attackerId]['wins'] += count.wins
                    counts[count.attackerId]['respect'] += count.respect
                    counts[count.attackerId]['fairFight'] += count.fairFight
                    counts[count.attackerId]['war'] += count.war
                    counts[count.attackerId]['retaliation'] += count.retaliation
                    counts[count.attackerId]['groupAttack'] += count.groupAttack
                    counts[count.attackerId]['overseas'] += count.overseas
                    counts[count.attackerId]['watcher'] += count.watcher /  float(len(chains))
                    counts[count.attackerId]['beenThere'] = count.beenThere or counts[count.attackerId]['beenThere']  # been present to at least one chain
                else:
                    counts[count.attackerId] = {'name': count.name,
                                                'hits': count.hits,
                                                'wins': count.wins,
                                                'respect': count.respect,
                                                'fairFight': count.fairFight,
                                                'war': count.war,
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
            if v["name"] in bonuses:
                if v["daysInFaction"] >= 0:
                    bonuses[v["name"]][2] = v["wins"]
                    smallHit = min(int(v["wins"]), smallHit)
                else:
                    del bonuses[v["name"]]

        for k, v in counts.items():
            if v["name"] not in bonuses and int(v["wins"]) >= smallHit and v["daysInFaction"] >= 0:
                bonuses[v["name"]] = [[], 0, v["wins"]]

            # else:
            #     if int(v["wins"]) >= int(smallestNwins):
            #         bonuses.append([[v["name"]], [[], 1, v["wins"]]])


        # aggregate counts
        arrayCounts = [v for k, v in counts.items()]
        arrayBonuses = [[name, ", ".join([str(h) for h in sorted(hits)]), respect, wins] for name, (hits, respect, wins) in sorted(bonuses.items(), key=lambda x: x[1][1], reverse=True)]

        # add last time connected
        updateMembers(faction, key=player.key)
        for i, bonus in enumerate(arrayBonuses):
            try:
                arrayBonuses[i].append(faction.member_set.filter(name=bonus[0]).first().lastAction)
            except:
                arrayBonuses[i].append("-")

        # context
        context = dict({'chainsReport': chains,  # chains of joint report
                        'total': total,  # for general info
                        'counts': arrayCounts,  # counts for report
                        'bonuses': arrayBonuses,  # bonuses for report
                        'chains': faction.chain_set.filter(status=True).order_by('-end'),  # for chain list after report
                        'player': player,
                        # 'chain': True, # to display categories
                        'view': {'jointReport': True, 'list': True}})  # view

        # render if logged
        if request.method == 'POST':
            return render(request, 'chain/content-reload.html', context)
        else:
            return render(request, 'chain.html', context)

    return HttpResponseRedirect(reverse('logout'))


# action view
def createReport(request, chainId):
    if request.session.get('player') and request.method == 'POST':
        print('[view.chain.createReport] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        key = player.key
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

    return HttpResponseRedirect(reverse('logout'))


# action view
def renderIndividualReport(request, chainId, memberId):
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
            print('[VIEW report] no data found for graph')
            graph = {'data': [], 'info': {'binsTime': 5, 'criticalHits': 1, 'speedRate': 0}}

        # context
        context = dict({'graph': graph,  # for report
                           'memberId': memberId})  # for selecting to good div

        print('[view.chain.renderIndividualReport] render')
        return render(request, 'chain/ireport.html', context)

    else:
        print('[view.chain.renderIndividualReport] render error')
        return render(request, 'yata/error.html', {'errorMessage': 'You need to be logged.'})


# action view
def deleteReport(request, chainId):
    if request.session.get('player') and request.method == 'POST':
        print('[view.chain.deleteReport] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        key = player.key
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

        context = {"player": player, "chain": chain}
        return render(request, 'chain/list-buttons.html', context)

    return HttpResponseRedirect(reverse('logout'))


# action view
def toggleReport(request, chainId):
    if request.session.get('player') and request.method == 'POST':
        print('[view.chain.deleteReport] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        key = player.key
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

    return HttpResponseRedirect(reverse('logout'))


# # action view
# def toggleFactionKey(request):
#     if request.session.get('chainer') and request.session['chainer'].get('AA'):
#         # get session info
#         factionId = request.session['chainer'].get('factionId')
#
#         # get faction
#         faction = Faction.objects.filter(tId=factionId).first()
#         if faction is None:
#             return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
#         print('[VIEW toggleFactionKey] faction {} found'.format(factionId))
#
#         faction.toggle_key(request.session['chainer'].get("name"),
#                            request.session['chainer'].get("keyValue"))
#
#         # render for on the fly modification
#         if request.method == "POST":
#             print('[VIEW toggleFactionKey] render')
#             context = dict({"faction": faction})
#             return render(request, 'chain/{}.html'.format(request.POST.get('html')), context)
#
#         # else redirection
#         else:
#             print('[VIEW toggleFactionKey] redirect')
#             return HttpResponseRedirect(reverse('chain:index'))
#
#     else:
#         print('[VIEW toggleFactionKey] render error')
#         return render(request, 'yata/error.html', {'errorMessage': 'You need to be logged and have AA rights.'})


def tree(request):
    if request.session.get('chainer') and request.session['chainer'].get('AA'):
        # get session info
        factionId = request.session['chainer'].get('factionId')
        key = request.session['chainer'].get('keyValue')

        # get faction
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
        print('[VIEW tree] faction {} found'.format(factionId))

        # call for upgrades
        upgrades = apiCall('faction', factionId, 'upgrades', key, sub='upgrades')
        if 'apiError' in upgrades:
            return render(request, 'yata/error.html', upgrades)

        # building upgrades tree
        tree = dict({})
        for k, upgrade in sorted(upgrades.items(), key=lambda x: x[1]['branchorder'], reverse=False):
            if upgrade['branch'] != 'Core':
                if tree.get(upgrade['branch']) is None:
                    tree[upgrade['branch']] = dict({})
                tree[upgrade['branch']][upgrade['name']] = upgrade

        for k, upgrade in tree.items():
            print('[VIEW tree] {} ({} upgrades)'.format(k, len(upgrade)))

        # context
        context = dict({'tree': tree, 'view': {'tree': True}})

        # render if logged
        return render(request, 'chain.html', context)
    else:
        # render if not logged
        return render(request, 'yata/error.html', {'errorMessage': 'You shouldn\'t be here. You need to enter valid API key.'})
