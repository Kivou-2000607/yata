from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone

import numpy
import json

from yata.handy import apiCall
from yata.handy import apiCallAttacks
from yata.handy import timestampToDate
from yata.handy import fillReport
from yata.handy import BONUS_HITS

from .models import Faction
from .models import Member


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

        # get live chain and next bonus
        liveChain = apiCall('faction', factionId, 'chain', key, sub='chain')
        if 'apiError' in liveChain:
            return render(request, 'errorPage.html', liveChain)
        activeChain = bool(liveChain['current'])
        liveChain["nextBonus"] = 10
        for i in BONUS_HITS:
            liveChain["nextBonus"] = i
            if i >= int(liveChain["current"]):
                break

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
                graph = {'data': [], 'info': {'binsTime': bins, 'criticalHits': int(bins) / 5}}
                cummulativeHits = 0
                for line in graphSplit:
                    splt = line.split(':')
                    cummulativeHits += int(splt[1])
                    graph['data'].append([timestampToDate(int(splt[0])), int(splt[1]), cummulativeHits])
                speedRate = cummulativeHits*300/float((int(graphSplit[-1].split(':')[0]) - int(graphSplit[0].split(':')[0])))  # hits every 5 minutes
                graph['info']['speedRate'] = speedRate

            else:
                print('[VIEW index] no data found for graph')
                graph = {'data': [], 'info': {'binsTime': 5, 'criticalHits': 1}}

            # context
            context = dict({'faction': faction, 'liveChain': liveChain, 'chain': chain, 'bonus': bonus, 'counts': counts, 'view': {'report': True, 'liveReport': True}, 'graph': graph})

        else:
            chain = faction.chain_set.filter(tId=0).first()
            if chain is not None:
                chain.delete()
                print('[VIEW index] chain 0 deleted')

            # context
            context = dict({'faction': faction, 'liveChain': liveChain, 'view': {'liveReport': True}})

        # render if logged
        return render(request, 'chain.html', context)

    # render if logged
    return render(request, 'chain.html')


# action view
def updateLive(request):  # no context
    if request.session.get('chainer') and request.method == 'POST':
        # get session info
        factionId = request.session['chainer'].get('factionId')
        key = request.session['chainer'].get('keyValue')

        # get faction
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            faction = Faction.objects.create(tId=factionId, name=request.session['chainer'].get('factionName'))
            print('[VIEW updateLive] faction {} created'.format(factionId))
        else:
            print('[VIEW updateLive] faction {} found'.format(factionId))

        # get live chain and next bonus
        liveChain = apiCall('faction', factionId, 'chain', key, sub='chain')
        if 'apiError' in liveChain:
            return render(request, 'errorPage.html', liveChain)
        liveChain["nextBonus"] = 10
        for i in BONUS_HITS:
            liveChain["nextBonus"] = i
            if i >= int(liveChain["current"]):
                break

        # context
        subcontext = dict({'liveChain': liveChain})
        return render(request, 'chain/{}.html'.format(request.POST.get("html")), subcontext)

    return render(request, 'errorPage.html', {'errorMessage': 'You need to POST.'})




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

            for k, v in chains.items():
                chain = faction.chain_set.filter(tId=k).first()
                if v['chain'] >= faction.hitsThreshold:
                    if chain is None:
                        print('[VIEW createList] chain {} created'.format(k))
                        faction.chain_set.create(tId=k, nHits=v['chain'], respect=v['respect'],
                                                 start=v['start'], startDate=timestampToDate(v['start']),
                                                 end=v['end'], endDate=timestampToDate(v['end']))
                    else:
                        print('[VIEW createList] chain {} found'.format(k))
                else:
                    if chain is not None:
                        print('[VIEW createList] chain {} deleted'.format(k))
                        chain.delete()

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

        # update members
        membersDB = faction.member_set.all()
        for m in members:
            memberDB = membersDB.filter(tId=m).first()
            if memberDB is not None:
                print('[VIEW members] member {} updated'.format(members[m]['name']))
                memberDB.name = members[m]['name']
                memberDB.lastAction = members[m]['last_action']
                memberDB.daysInFaction = members[m]['days_in_faction']
                memberDB.save()
            else:
                print('[VIEW members] member {} created'.format(members[m]['name']))
                faction.member_set.create(tId=m, name=members[m]['name'], lastAction=members[m]['last_action'], daysInFaction=members[m]['days_in_faction'])

        # context
        subcontext = dict({'members': membersDB})

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
            graph = {'data': [], 'info': {'binsTime': bins, 'criticalHits': int(bins) / 5}}
            cummulativeHits = 0
            for line in graphSplit:
                splt = line.split(':')
                cummulativeHits += int(splt[1])
                graph['data'].append([timestampToDate(int(splt[0])), int(splt[1]), cummulativeHits])
                speedRate = cummulativeHits*300/float((int(graphSplit[-1].split(':')[0]) - int(graphSplit[0].split(':')[0])))  # hits every 5 minutes
                graph['info']['speedRate'] = speedRate
        else:
            print('[VIEW report] no data found for graph')
            graph = {'data': [], 'info': {'binsTime': 5, 'criticalHits': 1, 'speedRate': 0}}

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
            total['nHits'] += chain.nHits
            total['respect'] += float(chain.respect)
            # get report
            report = chain.report_set.filter(chain=chain).first()
            if report is None:
                return render(request, 'errorPage.html', {'errorMessage': 'Report of chain {} not found in the database.'.format(chain.tId)})
            print('[VIEW jointReport] report of {} found'.format(chain))
            # loop over counts
            chainCounts = report.count_set.all()
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
                                                'daysInFaction': count.daysInFaction,
                                                'beenThere': count.beenThere,
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

        # update members
        membersDB = faction.member_set.all()
        # for m in members:
        #     memberDB = membersDB.filter(tId=m).first()
        #     if memberDB is not None:
        #         print('[VIEW members] member {} updated'.format(members[m]['name']))
        #         memberDB.name = members[m]['name']
        #         memberDB.lastAction = members[m]['last_action']
        #         memberDB.daysInFaction = members[m]['days_in_faction']
        #         memberDB.save()
        #     else:
        #         print('[VIEW members] member {} created'.format(members[m]['name']))
        #         faction.member_set.create(tId=m, name=members[m]['name'], lastAction=members[m]['last_action'], daysInFaction=members[m]['days_in_faction'])

        # case of live chain
        if int(chainId) == 0:
            print('[VIEW createReport] this is a live report')
            # change dates and status
            chain.status = True
            chain.end = int(timezone.now().timestamp())
            # chain.start = 1
            chain.endDate = timestampToDate(chain.end)
            chain.save()
            # get number of attacks
            chainInfo = apiCall('faction', factionId, 'chain', key, sub='chain')
            if 'apiError' in chainInfo:
                return render(request, 'errorPage.html', chainInfo)
            stopAfterNAttacks = chainInfo.get('current')
            print('[VIEW createReport] stop after {} attacks'.format(stopAfterNAttacks))
            if stopAfterNAttacks:
                attacks = apiCallAttacks(factionId, 1, chain.end, key, stopAfterNAttacks=stopAfterNAttacks)
            else:
                attacks = dict({})
                chain.delete()
                return render(request, 'empty.html')

        # case registered chain
        else:
            attacks = apiCallAttacks(factionId, chain.start, chain.end, key)
            stopAfterNAttacks = False

        chain, report, (binsCenter, histo) = fillReport(faction, membersDB, chain, report, attacks, stopAfterNAttacks)

        # render for on the fly modification
        if request.method == 'POST':
            if len(binsCenter) > 1:
                print('[VIEW createReport] data found for graph of length {}'.format(len(binsCenter)))
                binsTime = (binsCenter[-1] - binsCenter[0]) / float(60 * (len(histo) - 1))
                speedRate = numpy.sum(histo)*300/float(binsCenter[-1] - binsCenter[0])  # hits every 5 minutes
                graph = {'data': [[timestampToDate(a), b, c] for a, b, c in zip(binsCenter, histo, numpy.cumsum(histo))],
                         'info': {'binsTime': binsTime, 'criticalHits': binsTime / 5, 'speedRate': speedRate}}
            else:
                print('[VIEW createReport] no data found for graph')
                graph = {'data': [], 'info': {'binsTime': 5, 'criticalHits': 1, 'speedRate': 0}}

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
def renderIndividualReport(request, chainId, memberId):
    if request.session.get('chainer'):
        # get session info
        factionId = request.session['chainer'].get('factionId')
        key = request.session['chainer'].get('keyValue')

        # get faction
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            return render(request, 'errorPage.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
        print('[VIEW renderIndividualReport] faction {} found'.format(factionId))

        # get chain
        chain = faction.chain_set.filter(tId=chainId).first()
        if chain is None:
            return render(request, 'errorPage.html', {'errorMessage': 'Chain {} not found in the database.'.format(chainId)})
        print('[VIEW renderIndividualReport] chain {} found'.format(chainId))

        # get report
        report = chain.report_set.filter(chain=chain).first()
        if report is None:
            return render(request, 'errorPage.html', {'errorMessage': 'Report of chain {} not found in the database.'.format(chainId)})
        print('[VIEW renderIndividualReport] report of {} found'.format(chain))

        # create graph
        count = report.count_set.filter(attackerId=memberId).first()
        graphSplit = count.graph.split(',')
        if len(graphSplit) > 1:
            print('[VIEW renderIndividualReport] data found for graph of length {}'.format(len(graphSplit)))
            # compute average time for one bar
            bins = (int(graphSplit[-1].split(':')[0]) - int(graphSplit[0].split(':')[0])) / float(60 * (len(graphSplit) - 1))
            graph = {'data': [], 'info': {'binsTime': bins, 'criticalHits': int(bins) / 5}}
            cummulativeHits = 0
            for line in graphSplit:
                splt = line.split(':')
                cummulativeHits += int(splt[1])
                graph['data'].append([timestampToDate(int(splt[0])), int(splt[1]), cummulativeHits])
                speedRate = cummulativeHits*300/float((int(graphSplit[-1].split(':')[0]) - int(graphSplit[0].split(':')[0])))  # hits every 5 minutes
                graph['info']['speedRate'] = speedRate
        else:
            print('[VIEW report] no data found for graph')
            graph = {'data': [], 'info': {'binsTime': 5, 'criticalHits': 1, 'speedRate': 0}}

        # context
        subcontext = dict({'graph': graph,  # for report
                           'memberId': memberId})  # for selecting to good div

        print('[VIEW renderIndividualReport] render')
        return render(request, 'chain/{}.html'.format(request.POST.get('html')), subcontext)


    else:
        print('[VIEW renderIndividualReport] render error')
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

            # context
            subcontext = dict({'chain': chain})  # views

            return render(request, 'chain/{}.html'.format(request.POST.get('html')), subcontext)

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


# action view
def toggleFactionKey(request):
    if request.session.get('chainer') and request.session['chainer'].get('AA'):
        # get session info
        factionId = request.session['chainer'].get('factionId')

        # get faction
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            return render(request, 'errorPage.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})
        print('[VIEW toggleFactionKey] faction {} found'.format(factionId))

        faction.toggle_key(request.session['chainer'].get("name"),
                           request.session['chainer'].get("keyValue"))

        # render for on the fly modification
        if request.method == "POST":
            print('[VIEW toggleFactionKey] render')
            subcontext = dict({"faction": faction})
            return render(request, 'chain/{}.html'.format(request.POST.get('html')), subcontext)

        # else redirection
        else:
            print('[VIEW toggleFactionKey] redirect')
            return HttpResponseRedirect(reverse('chain:index'))

    else:
        print('[VIEW toggleFactionKey] render error')
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


# render view
def targets(request):
    if request.session.get('chainer'):
        # get session info
        key = request.session['chainer'].get('keyValue')
        playerId = request.session['chainer'].get('playerId')
        factionId = request.session['chainer'].get('factionId')

        # get faction
        faction = Faction.objects.filter(tId=factionId).first()
        if faction is None:
            faction = Faction.objects.create(tId=factionId, name=request.session['chainer'].get('factionName'))
            print('[VIEW index] faction {} created'.format(factionId))
        else:
            print('[VIEW index] faction {} found'.format(factionId))

        # get live chain and next bonus
        liveChain = apiCall('faction', factionId, 'chain', key, sub='chain')
        if 'apiError' in liveChain:
            return render(request, 'errorPage.html', liveChain)
        activeChain = bool(liveChain['current'])
        liveChain["nextBonus"] = 10
        for i in BONUS_HITS:
            liveChain["nextBonus"] = i
            if i >= int(liveChain["current"]):
                break

        # call for attacks
        attacks = apiCall('user', "", 'attacks', key, sub='attacks')
        if 'apiError' in attacks:
            return render(request, 'errorPage.html', attacks)

        remove = []
        for k, v in attacks.items():
            # if float(v["respect_gain"]) > 0.0:
            if int(v["defender_id"]) == int(playerId):
                remove.append(k)
            elif int(v["chain"]) in BONUS_HITS:
                attacks[k]["endDate"] = timestampToDate(v["timestamp_ended"])
                attacks[k]["flatRespect"] = float(v["respect_gain"]) / float(v['modifiers']['chainBonus'])
                attacks[k]["bonus"] = int(v["chain"])
            else:
                attacks[k]["endDate"] = timestampToDate(v["timestamp_ended"])
                attacks[k]["flatRespect"] = float(v["respect_gain"]) / float(v['modifiers']['chainBonus'])
                attacks[k]["bonus"] = 0

        for k in remove:
            del attacks[k]

        # context
        chainer = Member.objects.filter(tId=playerId).first()
        targets = chainer.target_set.all()
        allDefenders = [target.targetId for target in targets]
        context = dict({'attacks': attacks,  # list of attacks
                        'targets': targets,
                        'allDefenders': allDefenders,  # list of defenders id
                        'liveChain': liveChain,
                        'view': {'targets': True, 'liveReport': True}})  # views

        # render if logged
        return render(request, 'chain.html', context)

    else:
        # render if not logged
        return render(request, 'errorPage.html', {'errorMessage': 'You shouldn\'t be here. You need to enter valid API key.'})


# action view
def refreshTarget(request, targetId):
    if request.session.get('chainer'):
        if request.method == "POST":
            # get info
            key = request.session['chainer'].get('keyValue')
            playerId = request.session['chainer'].get('playerId')

            # get member
            chainer = Member.objects.filter(tId=playerId).first()
            print('[VIEW refreshTarget] chainer: {}'.format(chainer))

            # get target if exists
            target = chainer.target_set.filter(targetId=targetId).first()

            # call for target info
            # call for attacks
            targetInfo = apiCall('user', targetId, '', key)
            if 'apiError' in targetInfo:
                return render(request, 'errorPage.html', targetInfo)

            # call for attacks
            attacks = apiCall('user', "", 'attacks', key, sub='attacks')
            if 'apiError' in attacks:
                return render(request, 'errorPage.html', attacks)

            # get latest attack to target id
            findInAttacks = False
            for k, v in sorted(attacks.items(), key=lambda x: x[1]['timestamp_ended'], reverse=True):
                if int(v["defender_id"]) == int(targetId) and int(v["chain"]) not in BONUS_HITS:
                    findInAttacks = True
                    print('[VIEW refreshTarget] target find in attacks and refreshed')
                    chainer.target_set.filter(targetId=targetId).delete()
                    target = chainer.target_set.create(targetId=targetId,
                                                       targetName=v["defender_name"],
                                                       result=v["result"],
                                                       endDate=timestampToDate(v["timestamp_ended"]),
                                                       fairFight=float(v['modifiers']['fairFight']),
                                                       respect=float(v["respect_gain"]) / float(v['modifiers']['chainBonus']),
                                                       life=int(targetInfo["life"]["current"]),
                                                       lifeMax=int(targetInfo["life"]["maximum"]),
                                                       # status=" ".join(targetInfo["status"]),
                                                       status=targetInfo["status"][0].replace("In hospital", "Hosp"),
                                                       lastAction=targetInfo["last_action"],
                                                       lastUpdate=int(timezone.now().timestamp()),
                                                       level=targetInfo["level"],
                                                       rank=targetInfo["rank"]
                                                       )
                    break

            if not findInAttacks:
                print('[VIEW refreshTarget] target not found in attacks but refreshed')
                target = chainer.target_set.filter(targetId=targetId).first()
                target.life = int(targetInfo["life"]["current"])
                target.lifeMax = int(targetInfo["life"]["maximum"])
                target.status = targetInfo["status"][0].replace("In hospital", "Hosp")
                target.lastAction = targetInfo["last_action"]
                target.lastUpdate = int(timezone.now().timestamp())
                target.level = targetInfo["level"]
                target.rank = targetInfo["rank"]
                target.save()

            # render for on the fly modification
            print('[VIEW refreshTarget] render')
            subcontext = dict({"target": target})
            return render(request, 'chain/{}.html'.format(request.POST.get('html')), subcontext)

        # else redirection since no post
        else:
            print('[VIEW refreshTarget] no post')
            return HttpResponseRedirect(reverse('chain:list'))

    else:
        print('[VIEW toggleTarget] render error')
        return render(request, 'errorPage.html', {'errorMessage': 'You need to be logged.'})

# action view
def refreshAllTargets(request):
    if request.session.get('chainer'):
        if request.method == "POST":
            # get info
            key = request.session['chainer'].get('keyValue')
            playerId = request.session['chainer'].get('playerId')

            # get member
            chainer = Member.objects.filter(tId=playerId).first()
            print('[VIEW refreshAllTargets] chainer: {}'.format(chainer))

            # get target if exists
            targets = chainer.target_set.all()
            for target in targets:
                # call for target info
                # call for attacks
                targetInfo = apiCall('user', target.targetId, '', key)
                if 'apiError' in targetInfo:
                    return render(request, 'errorPage.html', targetInfo)

                # call for attacks
                attacks = apiCall('user', "", 'attacks', key, sub='attacks')
                if 'apiError' in attacks:
                    return render(request, 'errorPage.html', attacks)

                # get latest attack to target id
                findInAttacks = False
                for k, v in sorted(attacks.items(), key=lambda x: x[1]['timestamp_ended'], reverse=True):
                    if int(v["defender_id"]) == int(target.targetId) and int(v["chain"]) not in BONUS_HITS:
                        findInAttacks = True
                        print('[VIEW refreshAllTarget] target find in attacks and refreshed')
                        chainer.target_set.filter(targetId=target.targetId).delete()
                        target = chainer.target_set.create(targetId=target.targetId,
                                                           targetName=v["defender_name"],
                                                           result=v["result"],
                                                           endDate=timestampToDate(v["timestamp_ended"]),
                                                           fairFight=float(v['modifiers']['fairFight']),
                                                           respect=float(v["respect_gain"]) / float(v['modifiers']['chainBonus']),
                                                           life=int(targetInfo["life"]["current"]),
                                                           lifeMax=int(targetInfo["life"]["maximum"]),
                                                           # status=" ".join(targetInfo["status"]),
                                                           status=targetInfo["status"][0].replace("In hospital", "Hosp"),
                                                           lastAction=targetInfo["last_action"],
                                                           lastUpdate=int(timezone.now().timestamp()),
                                                           level=targetInfo["level"],
                                                           rank=targetInfo["rank"]
                                                           )
                        break

                if not findInAttacks:
                    print('[VIEW refreshAllTarget] target not found in attacks but refreshed')
                    target = chainer.target_set.filter(targetId=target.targetId).first()
                    target.life = int(targetInfo["life"]["current"])
                    target.lifeMax = int(targetInfo["life"]["maximum"])
                    target.status = targetInfo["status"][0].replace("In hospital", "Hosp")
                    target.lastAction = targetInfo["last_action"]
                    target.lastUpdate = int(timezone.now().timestamp())
                    target.level = targetInfo["level"]
                    target.rank = targetInfo["rank"]
                    target.save()


            # render for on the fly modification
            print('[VIEW refreshAllTargets] render')
            subcontext = dict({"targets": chainer.target_set.all()})
            return render(request, 'chain/{}.html'.format(request.POST.get('html')), subcontext)

        # else redirection since no post
        else:
            print('[VIEW refreshAllTargets] no post')
            return HttpResponseRedirect(reverse('chain:list'))

    else:
        print('[VIEW refreshAllTargets] render error')
        return render(request, 'errorPage.html', {'errorMessage': 'You need to be logged.'})


# action view
def reloadAllTargets(request):
    if request.session.get('chainer'):
        # get info
        key = request.session['chainer'].get('keyValue')
        playerId = request.session['chainer'].get('playerId')

        # get member
        chainer = Member.objects.filter(tId=playerId).first()
        print('[VIEW reloadAllTargets] chainer: {}'.format(chainer))

        # render for on the fly modification
        print('[VIEW reloadAllTargets] render')
        subcontext = dict({"targets": chainer.target_set.all()})
        return render(request, 'chain/targets_reload.html', subcontext)

    else:
        print('[VIEW reloadAllTargets] render error')
        return render(request, 'errorPage.html', {'errorMessage': 'You need to be logged.'})


# action view
def deleteTarget(request, targetId):
    if request.session.get('chainer'):
        if request.method == "POST":
            # get info
            playerId = request.session['chainer'].get('playerId')

            # get member
            chainer = Member.objects.filter(tId=playerId).first()

            # delete
            chainer.target_set.filter(targetId=targetId).delete()

            # render for on the fly modification
            print('[VIEW deleteTarget] render')
            return render(request, 'empty.html')

        # else redirection since no post
        else:
            print('[VIEW deleteTarget] no post')
            return HttpResponseRedirect(reverse('chain:list'))

    else:
        print('[VIEW deleteTarget] render error')
        return render(request, 'errorPage.html', {'errorMessage': 'You need to be logged.'})


# action view
def toggleTarget(request, targetId):
    if request.session.get('chainer'):
        if request.method == "POST":
            # get info
            key = request.session['chainer'].get('keyValue')
            playerId = request.session['chainer'].get('playerId')

            # get member
            chainer = Member.objects.filter(tId=playerId).first()

            # call for attacks
            attacks = apiCall('user', "", 'attacks', key, sub='attacks')
            if 'apiError' in attacks:
                return render(request, 'errorPage.html', attacks)

            # get target if exists
            target = chainer.target_set.filter(targetId=targetId).first()
            if target is None:
                print("create target")
                for k, v in sorted(attacks.items(), key=lambda x: x[1]['timestamp_ended'], reverse=True):
                    if int(v["defender_id"]) == int(targetId):
                        target = chainer.target_set.create(targetId=targetId,
                                                           targetName=v["defender_name"],
                                                           result=v["result"],
                                                           endDate=timestampToDate(v["timestamp_ended"]),
                                                           fairFight=float(v['modifiers']['fairFight']),
                                                           respect=float(v["respect_gain"]) / float(v['modifiers']['chainBonus']))
                        break
            else:
                print("delete target")
                target = chainer.target_set.filter(targetId=targetId).delete()

            # render for on the fly modification
            print('[VIEW toggleTarget] render')
            allDefenders = [t.targetId for t in chainer.target_set.all()]
            subcontext = dict({"target": {"defender_id": int(targetId)}, "allDefenders": allDefenders})
            return render(request, 'chain/{}.html'.format(request.POST.get('html')), subcontext)

        # else redirection since no post
        else:
            print('[VIEW toggleTarget] no post')
            return HttpResponseRedirect(reverse('chain:list'))

    else:
        print('[VIEW toggleTarget] render error')
        return render(request, 'errorPage.html', {'errorMessage': 'You need to be logged.'})


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
