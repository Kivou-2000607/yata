from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone

import numpy
import json

from yata.handy import apiCall
from yata.handy import apiCallAttacks
from yata.handy import timestampToDate

from .models import Faction


# render view
def index(request):
    if request.session.get('chainer'):
        # get session info
        factionId = request.session['chainer'].get('factionId')
        key = request.session['chainer'].get('keyValue')

        # get faction
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            faction = Faction.objects.create(tId=factionId, name=request.session['chainer'].get('factionName'))
            print('[VIEW index] faction {} created'.format(factionId))
        else:
            print('[VIEW index] faction {} found'.format(factionId))

        liveChain = apiCall('faction', factionId, 'chain', key, sub='chain')
        if 'apiError' in liveChain:
            return render(request, 'errorPage.html', liveChain)
        activeChain = bool(liveChain['current'])

        if activeChain:
            print('[VIEW index] chain active')
            chain = faction.chain_set.filter(tId=0).first()
            if chain is None:
                print('[VIEW index] live chain 0 created')
                chain = faction.chain_set.create(tId=0, start=1, status=False)
            else:
                print('[VIEW index] live chain 0 found')

            report = chain.report_set.filter(chain=chain).first()
            print('[VIEW index] live report is {}'.format(report))
            if report is None:
                chain.graph = ''
                chain.save()
                counts = None
                bonus = None
                print('[VIEW index] live counts is {}'.format(counts))
                print('[VIEW index] live bonus is {}'.format(bonus))
            else:
                counts = report.count_set.all()
                bonus = report.bonus_set.all()
                print('[VIEW index] live counts of length {}'.format(len(counts)))
                print('[VIEW index] live bonus of length {}'.format(len(bonus)))

            # create graph
            graphSplit = chain.graph.split(',')
            if len(graphSplit) > 1:
                print('[VIEW index] data found for graph of length {}'.format(len(graphSplit)))
                # compute average time for one bar
                bins = (int(graphSplit[-1].split(':')[0]) - int(graphSplit[0].split(':')[0])) / float(60 * (len(graphSplit) - 1))
                graph = {'data': [], 'info': {'binsTime': bins, 'criticalHits': int(bins) / (5)}}
                cummulativeHits = 0
                for line in graphSplit:
                    splt = line.split(':')
                    cummulativeHits += int(splt[1])
                    graph['data'].append([timestampToDate(int(splt[0])), int(splt[1]), cummulativeHits])
            else:
                print('[VIEW index] no data found for graph')
                graph = {'data': [], 'info': {'binsTime': 5, 'criticalHits': 1}}

            # context
            context = dict({'liveChain': liveChain, 'chain': chain, 'bonus': bonus, 'counts': counts, 'view': {'report': True, 'liveReport': True}, 'graph': graph})

        else:
            chain = faction.chain_set.filter(tId=0).first()
            if chain is not None:
                chain.delete()
                print('[VIEW index] chain 0 deleted')

            # context
            context = dict({'liveChain': liveChain, 'view': {'liveReport': True}})

        # render if logged
        return render(request, 'chain.html', context)

    # render if logged
    return render(request, 'chain.html')


# render view
def list(request):
    if request.session.get('chainer'):
        # get session info
        factionId = request.session['chainer'].get('factionId')

        # get faction
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            faction = Faction.objects.create(tId=factionId, name=request.session['chainer'].get('factionName'))
            print('[VIEW list] faction {} created'.format(factionId))
        else:
            print('[VIEW list] faction {} found'.format(factionId))

        # get chains
        chains = faction.chain_set.filter(status=True).order_by('-end')

        # context
        context = dict({'chains': chains, 'view': {'list': True}})

        # render if logged
        return render(request, 'chain.html', context)

    else:
        # render if not logged
        return render(request, 'errorPage.html', {'errorMessage': 'You shouldn\'t be here. You need to enter valid API key.'})


# action view
def createList(request):  # no context
    if request.session.get('chainer') and request.method == 'POST':
        # get session info
        factionId = request.session['chainer'].get('factionId')
        key = request.session['chainer'].get('keyValue')

        # get faction
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            faction = Faction.objects.create(tId=factionId, name=request.session['chainer'].get('factionName'))
            print('[VIEW createList] faction {} created'.format(factionId))
        else:
            print('[VIEW createList] faction {} found'.format(factionId))

        # if AA refresh list of chains
        if request.session['chainer'].get('AA'):
            chains = apiCall('faction', faction.tId, 'chains', key, sub='chains')
            if 'apiError' in chains:
                return render(request, 'errorPage.html', chains)

            nCreated = 0
            nIgnored = 0
            for k, v in chains.items():
                if v['chain'] >= faction.hitsThreshold:
                    chain = faction.chain_set.filter(tId=k).first()
                    if chain is None:
                        print('[VIEW createList] chain {} created'.format(k))
                        nCreated += 1
                        faction.chain_set.create(tId=k, nHits=v['chain'], respect=v['respect'],
                                                 start=v['start'], startDate=timestampToDate(v['start']),
                                                 end=v['end'], endDate=timestampToDate(v['end']))
                    else:
                        print('[VIEW createList] chain {} found'.format(k))
                else:
                    # print('[VIEW createList] chain {} ignored'.format(k))
                    nIgnored += 1

        # get chains
        chains = faction.chain_set.filter(status=True).order_by('-end')

        # context
        subcontext = dict({'chains': chains})

        return render(request, 'chain/{}.html'.format(request.POST.get("html")), subcontext)

    return render(request, 'errorPage.html', {'errorMessage': 'You need to POST.'})


# render view
def members(request):
    if request.session.get('chainer'):
        # get session info
        factionId = request.session['chainer'].get('factionId')

        # get faction
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            faction = Faction.objects.create(tId=factionId, name=request.session['chainer'].get('factionName'))
            print('[VIEW members] faction {} created'.format(factionId))
        else:
            print('[VIEW members] faction {} found'.format(factionId))

        # get members
        members = faction.member_set.all()

        # context
        context = dict({'members': members, 'view': {'members': True}})

        # render if logged
        return render(request, 'chain.html', context)

    else:
        # render if logged
        return render(request, 'errorPage.html', {'errorMessage': 'You shouldn\'t be here. You need to enter valid API key.'})


# action view
def createMembers(request):  # no context
    if request.session.get('chainer') and request.method == 'POST':
        # get session info
        factionId = request.session['chainer'].get('factionId')
        key = request.session['chainer'].get('keyValue')

        # get faction
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            faction = Faction.objects.create(tId=factionId, name=request.session['chainer'].get('factionName'))
            print('[VIEW members] faction {} created'.format(factionId))
        else:
            print('[VIEW members] faction {} found'.format(factionId))

        # call members
        members = apiCall('faction', factionId, 'basic', key, sub='members')
        if 'apiError' in members:
            return render(request, 'errorPage.html', members)

        # delete all and recreate all members
        faction.member_set.all().delete()
        for m in members:
            faction.member_set.create(tId=m, name=members[m]['name'], lastAction=members[m]['last_action'], daysInFaction=members[m]['days_in_faction'])

        # context
        members = faction.member_set.all()
        subcontext = dict({'members': members})

        return render(request, 'chain/{}.html'.format(request.POST.get("html")), subcontext)
    return render(request, 'errorPage.html', {'errorMessage': 'You need to POST.'})


# render view
def report(request, chainId):
    if request.session.get('chainer'):
        # get session info
        factionId = request.session['chainer'].get('factionId')

        # get faction
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            return render(request, 'errorPage.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
        print('[VIEW report] faction {} found'.format(factionId))

        # get chain
        chain = faction.chain_set.filter(tId=chainId).first()
        if chain is None:
            return render(request, 'errorPage.html', {'errorMessage': 'Chain {} not found in the database.'.format(chainId)})
        print('[VIEW report] chain {} found'.format(chainId))

        # get report
        report = chain.report_set.filter(chain=chain).first()
        if report is None:
            return render(request, 'errorPage.html', {'errorMessage': 'Report of chain {} not found in the database.'.format(chainId)})
        print('[VIEW report] report of {} found'.format(chain))

        # create graph
        graphSplit = chain.graph.split(',')
        if len(graphSplit) > 1:
            print('[VIEW report] data found for graph of length {}'.format(len(graphSplit)))
            # compute average time for one bar
            bins = (int(graphSplit[-1].split(':')[0]) - int(graphSplit[0].split(':')[0])) / float(60 * (len(graphSplit) - 1))
            graph = {'data': [], 'info': {'binsTime': bins, 'criticalHits': int(bins) / (5)}}
            cummulativeHits = 0
            for line in graphSplit:
                splt = line.split(':')
                cummulativeHits += int(splt[1])
                graph['data'].append([timestampToDate(int(splt[0])), int(splt[1]), cummulativeHits])
        else:
            print('[VIEW report] no data found for graph')
            graph = {'data': [], 'info': {'binsTime': 5, 'criticalHits': 1}}

        # context
        context = dict({'chain': chain,  # for general info
                        'chains': faction.chain_set.filter(status=True).order_by('-end'),  # for chain list after report
                        'counts': report.count_set.all(),  # for report
                        'bonus': report.bonus_set.all(),  # for report
                        'graph': graph,  # for report
                        'view': {'report': True, 'list': True}})  # views

        # render if logged
        return render(request, 'chain.html', context)

    else:
        # render if not logged
        return render(request, 'errorPage.html', {'errorMessage': 'You shouldn\'t be here. You need to enter valid API key.'})


# render view
def jointReport(request):
    if request.session.get('chainer'):
        # get session info
        factionId = request.session['chainer'].get('factionId')

        # get faction
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            return render(request, 'errorPage.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
        print('[VIEW jointReport] faction {} found'.format(factionId))

        # get chains
        chains = faction.chain_set.filter(jointReport=True)
        print('[VIEW jointReport] {} chains for the joint report'.format(len(chains)))
        if len(chains) < 1:
            return HttpResponseRedirect(reverse('chain:list'))

        # loop over chains
        counts = dict({})
        total = {'nHits': 0, 'respect': 0.0}
        for chain in chains:
            print('[VIEW jointReport] chain {} found'.format(chain.tId))
            # get report
            report = chain.report_set.filter(chain=chain).first()
            if report is None:
                return render(request, 'errorPage.html', {'errorMessage': 'Report of chain {} not found in the database.'.format(chain.tId)})
            print('[VIEW jointReport] report of {} found'.format(chain))
            # loop over counts
            chainCounts = report.count_set.all()
            for count in chainCounts:
                total['nHits'] += count.wins
                total['respect'] += float(count.respect)
                if count.attackerId in counts:
                    counts[count.attackerId]['hits'] += count.hits
                    counts[count.attackerId]['wins'] += count.wins
                    counts[count.attackerId]['respect'] += count.respect
                    counts[count.attackerId]['fairFight'] += count.fairFight
                else:
                    counts[count.attackerId] = {'name': count.name,
                                                'hits': count.hits,
                                                'wins': count.wins,
                                                'respect': count.respect,
                                                'fairFight': count.fairFight,
                                                'daysInFaction': count.daysInFaction,
                                                'attackerId': count.attackerId}
            print('[VIEW jointReport] {} counts for {}'.format(len(counts), chain))

        # aggregate counts
        arrayCounts = [v for k, v in counts.items()]

        # context
        context = dict({'chainsReport': chains,  # chains of joint report
                        'total': total,  # for general info
                        'counts': arrayCounts,  # counts for report
                        'chains': faction.chain_set.filter(status=True).order_by('-end'),  # for chain list after report
                        'view': {'jointReport': True, 'list': True}})  # view

        # render if logged
        return render(request, 'chain.html', context)

    else:
        # render if not logged
        return render(request, 'errorPage.html', {'errorMessage': 'You shouldn\'t be here. You need to enter valid API key.'})


# action view
def createReport(request, chainId):
    if request.session.get('chainer') and request.session['chainer'].get('AA'):
        # get session info
        factionId = request.session['chainer'].get('factionId')
        key = request.session['chainer'].get('keyValue')

        # get faction
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            return render(request, 'errorPage.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
        print('[VIEW createReport] faction {} found'.format(factionId))

        # get chain
        chain = faction.chain_set.filter(tId=chainId).first()
        if chain is None:
            return render(request, 'errorPage.html', {'errorMessage': 'Chain {} not found in the database.'.format(chainId)})
        print('[VIEW createReport] chain {} found'.format(chainId))

        # delete old report and create new
        chain.report_set.all().delete()
        report = chain.report_set.create()
        print('[VIEW createReport] new report created')

        # refresh members
        members = apiCall('faction', factionId, 'basic', key, sub='members')
        if 'apiError' in members:
            return render(request, 'errorPage.html', members)
        faction.member_set.all().delete()
        for m in members:
            faction.member_set.create(tId=m, name=members[m]['name'], lastAction=members[m]['last_action'], daysInFaction=members[m]['days_in_faction'])
        members = faction.member_set.all()

        # case of live chain
        if int(chainId) == 0:
            print('[VIEW createReport] this is a live report')
            # change dates and status
            chain.status = True
            chain.end = int(timezone.now().timestamp())
            chain.start = 1
            chain.endDate = timestampToDate(chain.end)
            chain.save()
            # get number of attacks
            chainInfo = apiCall('faction', factionId, 'chain', key, sub='chain')
            if 'apiError' in chainInfo:
                return render(request, 'errorPage.html', chainInfo)
            stopAfterNAttacks = chainInfo.get('current')
            print('[VIEW createReport] stop after {} attacks'.format(stopAfterNAttacks))
            if stopAfterNAttacks:
                attacks = apiCallAttacks(factionId, chain.start, chain.end, key, stopAfterNAttacks=stopAfterNAttacks)
            else:
                attacks = dict({})
                chain.delete()
                return render(request, 'empty.html')

        # case registered chain
        else:
            attacks = apiCallAttacks(factionId, chain.start, chain.end, key)
            stopAfterNAttacks = False

        # initialisation of variables before loop
        bonus_hits = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000]  # bonus respect values are 4.2**n
        nWR = [0, 0.0]  # number of wins and respect
        bonus = []  # chain bonus
        attacksForHisto = []  # record attacks timestamp histogram

        # create attackers array on the fly to avoid db connection in the loop
        attackers = dict({})
        for m in members:
            attackers[m.name] = [0, 0, 0.0, 0.0, m.daysInFaction, m.tId]

        # loop over attacks
        tmp = dict({})
        for k, v in sorted(attacks.items(), key=lambda x: x[1]['timestamp_ended'], reverse=True):
            attackerID = int(v['attacker_id'])
            attackerName = v['attacker_name']
            # if attacker part of the faction at the time of the chain
            if(int(v['attacker_faction']) == faction.tId):
                if tmp.get(v["result"]) is None:
                    tmp[v["result"]] = 1
                else:
                    tmp[v["result"]] += 1
                # if attacker not part of the faction at the time of the call
                if attackerName not in attackers:
                    print('[VIEW createReport] hitter out of faction: {}'.format(attackerName))
                    attackers[attackerName] = [0, 0, 0.0, 0.0, -1, attackerID]  # add out of faction attackers on the fly

                # if it's a hit
                respect = float(v['respect_gain'])
                if respect > 0.0:
                    attacksForHisto.append(v['timestamp_ended'])
                    nWR[0] += 1
                    attackers[attackerName][0] += 1
                    if v['chain'] in bonus_hits:
                        r = 4.2 * 2**(1 + float([i for i, x in enumerate(bonus_hits) if x == int(v['chain'])][0]))
                        print('[VIEW createReport] bonus {}: {} respects'.format(v['chain'], r))
                        bonus.append((v['chain'], attackerName, respect, r))
                    attackers[attackerName][2] += float(v['modifiers']['fairFight'])
                    attackers[attackerName][3] += respect / float(v['modifiers']['chainBonus'])
                    nWR[1] += respect

                attackers[attackerName][1] += 1

                if stopAfterNAttacks is not False and nWR[0] >= stopAfterNAttacks:
                    break

        for k, v in tmp.items():
            print(k, v)

        # create histogram
        chain.start = int(attacksForHisto[-1])
        chain.startDate = timestampToDate(chain.start)
        diff = int(chain.end - chain.start)
        binsGapMinutes = 5
        while diff / (binsGapMinutes * 60) > 256:
            binsGapMinutes += 5

        bins = [chain.start]
        for i in range(256):
            add = bins[i] + (binsGapMinutes * 60)
            if add > chain.end:
                break
            bins.append(add)

        # bins = max(min(int(diff / (5 * 60)), 256), 1)  # min is to limite the number of bins for long chains and max is to insure minimum 1 bin
        print('[VIEW createReport] chain delta time: {} second'.format(diff))
        print('[VIEW createReport] histogram bins delta time: {} second'.format(binsGapMinutes * 60))
        print('[VIEW createReport] histogram number of bins: {}'.format(len(bins) - 1))
        histo, bin_edges = numpy.histogram(attacksForHisto, bins=bins)
        binsCenter = [int(0.5 * (a + b)) for (a, b) in zip(bin_edges[0:-1], bin_edges[1:])]
        chain.nHits = nWR[0]
        chain.respect = nWR[1]
        chain.graph = ','.join(['{}:{}'.format(a, b) for (a, b) in zip(binsCenter, histo)])
        chain.save()

        # fill the database with counts and bonuses
        for k, v in attackers.items():
            # if v[1]:
            report.count_set.create(attackerId=v[5], name=k, wins=v[0], hits=v[1], fairFight=v[2], respect=v[3], daysInFaction=v[4])
        for b in bonus:
            report.bonus_set.create(hit=b[0], name=b[1], respect=b[2], respectMax=b[3])

        # render for on the fly modification
        if request.method == 'POST':
            if len(binsCenter) > 1:
                print('[VIEW createReport] data found for graph of length {}'.format(len(binsCenter)))
                binsTime = (binsCenter[-1] - binsCenter[0]) / float(60 * (len(histo) - 1))
                graph = {'data': [[timestampToDate(a), b, c] for a, b, c in zip(binsCenter, histo, numpy.cumsum(histo))],
                         'info': {"binsTime": binsTime, "criticalHits": binsTime / 5}}
            else:
                print('[VIEW createReport] no data found for graph')
                graph = {'data': [], 'info': {'binsTime': 5, 'criticalHits': 1}}

            # context
            subcontext = dict({'liveChain': not bool(chain.tId),
                               'chain': chain,  # for general info
                               'chains': faction.chain_set.filter(status=True).order_by('-end'),  # for chain list after report
                               'counts': report.count_set.all(),  # for report
                               'bonus': report.bonus_set.all(),  # for report
                               'graph': graph,  # for report
                               'view': {'report': True, 'list': True}})  # views

            print('[VIEW createReport] render')
            return render(request, 'chain/{}.html'.format(request.POST.get('html')), subcontext)

        # redirect
        else:
            print('[VIEW createReport] redirect')
            return HttpResponseRedirect(reverse('chain:report', kwargs={'chainId': chainId}))

    else:
        print('[VIEW createReport] render error')
        return render(request, 'errorPage.html', {'errorMessage': 'You need to be logged.'})


# action view
def deleteReport(request, chainId):
    if request.session.get('chainer') and request.session['chainer'].get('AA'):
        # get session info
        factionId = request.session['chainer'].get('factionId')

        # get faction
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            return render(request, 'errorPage.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
        print('[VIEW deleteReport] faction {} found'.format(factionId))

        # get chain
        chain = faction.chain_set.filter(tId=chainId).first()
        if chain is None:
            return render(request, 'errorPage.html', {'errorMessage': 'Chain {} not found in the database.'.format(chainId)})
        print('[VIEW deleteReport] chain {} found'.format(chainId))

        # delete old report and remove from joint report
        chain.report_set.all().delete()
        chain.jointReport = False
        chain.save()
        print('[VIEW deleteReport] report deleted')

        # render for on the fly modification
        if request.method == "POST":
            print('[VIEW deleteReport] render')
            return render(request, 'chain/{}.html'.format(request.POST.get('html')))

        # else redirection
        else:
            print('[VIEW deleteReport] redirect')
            return HttpResponseRedirect(reverse('chain:list'))

    else:
        print('[VIEW deleteReport] render error')
        return render(request, 'errorPage.html', {'errorMessage': 'You need to be logged.'})


# action view
def toggleReport(request, chainId):
    if request.session.get('chainer') and request.session['chainer'].get('AA'):
        # get session info
        factionId = request.session['chainer'].get('factionId')

        # get faction
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            return render(request, 'errorPage.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
        print('[VIEW toggleReport] faction {} found'.format(factionId))

        # get chain
        chain = faction.chain_set.filter(tId=chainId).first()
        if chain is None:
            return render(request, 'errorPage.html', {'errorMessage': 'Chain {} not found in the database.'.format(chainId)})
        print('[VIEW toggleReport] chain {} found'.format(chainId))

        # toggle
        chain.toggle_report()
        chain.save()

        # render for on the fly modification
        if request.method == "POST":
            print('[VIEW toggleReport] render')
            subcontext = dict({"chain": chain})
            return render(request, 'chain/{}.html'.format(request.POST.get('html')), subcontext)

        # else redirection
        else:
            print('[VIEW toggleReport] redirect')
            return HttpResponseRedirect(reverse('chain:list'))

    else:
        print('[VIEW toggleReport] render error')
        return render(request, 'errorPage.html', {'errorMessage': 'You need to be logged and have AA rights.'})


def tree(request):
    if request.session.get('chainer') and request.session['chainer'].get('AA'):
        # get session info
        factionId = request.session['chainer'].get('factionId')
        key = request.session['chainer'].get('keyValue')

        # get faction
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            return render(request, 'errorPage.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
        print('[VIEW tree] faction {} found'.format(factionId))

        # call for upgrades
        upgrades = apiCall('faction', factionId, 'upgrades', key, sub='upgrades')
        if 'apiError' in upgrades:
            return render(request, 'errorPage.html', upgrades)

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
        return render(request, 'errorPage.html', {'errorMessage': 'You shouldn\'t be here. You need to enter valid API key.'})


# UPDATE ON THE FLY
def updateKey(request):
    print('[updateKey] in')

    # request.session['chainer'] = {'keyValue': 'myKeyForDebug',
    #                               'name': 'Kivou',
    #                               'playerId': 2000607,
    #                               'factionName': 'Nub Navy',
    #                               'factionId': 33241,
    #                               'AA': True,
    #                               }
    # request.session.set_expiry(0)  # logout when close browser
    # return render(request, 'chain/login.html')

    if request.method == 'POST':
        p = request.POST
        user = apiCall('user', '', 'profile', p.get('keyValue'))
        if 'apiError' in user:
            return render(request, 'chain/{}.html'.format(p['html']), user)

        if user['faction']['faction_id'] in [33241]:
            AArights = 'chains' in apiCall('faction', user['faction']['faction_id'], 'chains', p.get('keyValue'))
            request.session['chainer'] = {'keyValue': p['keyValue'],
                                          'name': user['name'],
                                          'playerId': user['player_id'],
                                          'factionName': user['faction']['faction_name'],
                                          'factionId': user['faction']['faction_id'],
                                          'AA': AArights,
                                          }
            check = json.loads(p.get('rememberSession'))
            if check:
                request.session.set_expiry(31536000)  # 1 year
            else:
                request.session.set_expiry(0)  # logout when close browser
            return render(request, 'chain/{}.html'.format(p['html']))

        else:
            user = {'apiError': 'Sorry but this website is not yet opened to your faction'}
            return render(request, 'chain/{}.html'.format(p['html']), user)

    else:
        return HttpResponse('Don\'t try to be a smart ass, you need to post.')


def logout(request):
    try:
        del request.session['chainer']
    except:
        pass
    return HttpResponseRedirect(reverse('chain:index'))
