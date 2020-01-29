from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings

import os
import json

from yata.handy import *
from faction.models import *
from faction.functions import *


def index(request):
    try:
        if request.session.get('player'):
            # get player and key
            player = getPlayer(request.session["player"].get("tId"))
            key = player.getKey()

            # get user info
            user = apiCall('user', '', 'profile', key)
            if 'apiError' in user:
                context = {'player': player, 'apiError': user["apiError"] + " We can't check your faction so you don't have access to this section."}
                player.chainInfo = "N/A"
                player.factionId = 0
                player.factionNa = "-"
                player.factionAA = False
                player.save()
                return render(request, 'faction.html', context)

            # update faction information
            factionId = int(user.get("faction")["faction_id"])
            player.chainInfo = user.get("faction")["faction_name"]
            player.factionNa = user.get("faction")["faction_name"]
            player.factionId = factionId
            if 'chains' in apiCall('faction', factionId, 'chains', key):
                player.chainInfo += " [AA]"
                player.factionAA = True
            else:
                player.factionAA = False
            player.save()

            # get /create faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                faction = Faction.objects.create(tId=factionId, name=user.get("faction")["faction_name"])
            else:
                faction.name = user.get("faction")["faction_name"]
                faction.save()

            # add/remove key depending of AA member
            faction.manageKey(player)

            context = {'player': player, 'faction': faction, 'factioncat': True, 'view': {'index': True}}
            return render(request, 'faction.html', context)

        else:
            # return redirect('/faction/territories/')
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


# SECTION: configuration

def configurations(request):
    try:
        if request.session.get('player'):
            # get player
            player = getPlayer(request.session["player"].get("tId"))

            if player.factionAA:
                faction = Faction.objects.filter(tId=player.factionId).first()
                faction.manageKey(player)

                # update members before to avoid coming here before having members
                faction.updateMembers(key=player.getKey(value=False), force=False)

                # get keys
                keys = faction.masterKeys.filter(useSelf=True)
                faction.nKeys = len(keys.filter(useFact=True))
                faction.save()

                context = {'player': player, 'factioncat': True, "bonus": BONUS_HITS, "faction": faction, 'keys': keys, 'view': {'aa': True}}

                # add poster
                if faction.poster:
                    fntId = {i: [f.split("__")[0].replace("-", " "), int(f.split("__")[1].split(".")[0])] for i, f in enumerate(sorted(os.listdir(settings.STATIC_ROOT + '/perso/font/')))}
                    posterOpt = json.loads(faction.posterOpt)
                    context['posterOpt'] = posterOpt
                    context['random'] = random.randint(0, 65535)
                    context['fonts'] = fntId

                page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'
                return render(request, page, context)

            else:
                return returnError(type=403, msg="You need AA rights.")

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


def configurationsKey(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            player = getPlayer(request.session["player"].get("tId"))
            key = player.key_set.first()
            key.useFact = not key.useFact
            key.save()

            context = {"player": player, "key": key}
            return render(request, 'faction/aa/keys.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


def configurationsThreshold(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})

            previousThreshold = faction.hitsThreshold
            faction.hitsThreshold = int(request.POST.get("threshold", 100))
            faction.save()

            context = {"player": player, "faction": faction, "bonus": BONUS_HITS, "onChange": True, "previousThreshold": previousThreshold}
            return render(request, 'faction/aa/threshold.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


def configurationsPoster(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})

            # case we enable/disable or hold/unhold the poster
            if request.POST.get("type", False) == "enable":
                faction.poster = not faction.poster
                faction.posterHold = faction.posterHold if faction.poster else False

            elif request.POST.get("type", False) == "hold":
                faction.posterHold = not faction.posterHold

            # update poster
            if request.method == "POST" and request.POST.get("posterConf"):
                updatePosterConf(faction, request.POST.dict())
                updatePoster(faction)

            faction.save()

            context = {'faction': faction}

            # update poster if needed
            url = "{}/posters/{}.png".format(settings.STATIC_ROOT, faction.tId)
            if faction.poster:
                fntId = {i: [f.split("__")[0].replace("-", " "), int(f.split("__")[1].split(".")[0])] for i, f in enumerate(sorted(os.listdir(settings.STATIC_ROOT + '/perso/font/')))}
                posterOpt = json.loads(faction.posterOpt)
                context['posterOpt'] = posterOpt
                context['random'] = random.randint(0, 65535)
                context['fonts'] = fntId
            elif not faction.poster and os.path.exists(url):
                os.remove(url)
                context['posterDeleted'] = True

            return render(request, 'faction/aa/poster.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


# SECTION: members

def members(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Click on chain report again please."}
                return render(request, page, context)

            # update chains if AA
            key = player.getKey(value=False)
            members = faction.updateMembers(key=key, force=False)
            error = False
            if 'apiError' in members:
                error = members

            # get members
            members = faction.member_set.all()

            context = {'player': player, 'factioncat': True, 'faction': faction, 'members': members, 'view': {'members': True}}
            if error:
                selectError = 'apiErrorSub' if request.method == 'POST' else 'apiError'
                context.update({selectError: error["apiError"] + " Members not updated."})
            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


def updateMember(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            if player is None:
                return render(request, 'faction/members/line.html', {'member': False, 'errorMessage': 'Who are you?'})

            # get faction (of the user, not the member)
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'faction/members/line.html', {'errorMessage': 'Faction {} not found'.format(factionId)})

            # update members status for the faction (skip < 30s)
            membersAPI = faction.updateMemberStatus(key=player.getKey(value=False))

            # get member id
            memberId = request.POST.get("memberId", 0)

            # get member
            member = faction.member_set.filter(tId=memberId).first()
            if member is None:
                return render(request, 'faction/members/line.html', {'errorMessage': 'Member {} not found in faction {}'.format(memberId, factionId)})

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
            return render(request, 'faction/members/line.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


def toggleMemberShare(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'faction/members/energy.html', {'errorMessage': 'Faction {} not found'.format(factionId)})

            # get member
            member = faction.member_set.filter(tId=player.tId).first()
            if member is None:
                return render(request, 'faction/members/energy.html', {'errorMessage': 'Member {} not found'.format(player.tId)})

            # toggle share energy
            if request.POST.get("type") == "energy":
                member.shareE = 0 if member.shareE else 1
                error = member.updateEnergy(key=player.getKey())
                # handle api error
                if error:
                    member.shareE = 0
                    member.energy = 0
                    return render(request, 'faction/members/energy.html', {'errorMessage': error.get('apiErrorString', 'error')})
                else:
                    context = {"player": player, "member": member}
                    return render(request, 'faction/members/energy.html', context)

            elif request.POST.get("type") == "nerve":
                member.shareN = 0 if member.shareN else 1
                error = member.updateNNB(key=player.getKey())
                # handle api error
                if error:
                    member.shareN = 0
                    member.nnb = 0
                    return render(request, 'faction/members/nnb.html', {'errorMessage': error.get('apiErrorString', 'error')})
                else:
                    context = {"player": player, "member": member}
                    return render(request, 'faction/members/nnb.html', context)

                # member.save()
            else:
                return render(request, 'faction/members/energy.html', {'errorMessage': '?'})

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


# SECTION: chains
def chains(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            # get page
            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Click on chain report again please."}
                return render(request, page, context)

            # update chains if AA
            error = False
            if player.factionAA:
                key = player.getKey()
                chains = apiCall('faction', faction.tId, 'chains', key=key, sub='chains')
                if 'apiError' in chains:
                    error = chains
                    chains = dict({})

                for k, v in chains.items():
                    chain = faction.chain_set.filter(tId=k).first()
                    old = tsnow() - int(v['end']) > 3600 * 24 * 31 * 6
                    if chain is None:
                        if v['chain'] >= faction.hitsThreshold and not old:
                            faction.chain_set.create(tId=k, **v)
                    else:
                        if v['chain'] < faction.hitsThreshold or old:
                            chain.delete()

            # get chains
            chains = faction.chain_set.all().order_by('-end')
            combined = len(chains.filter(combine=True))
            for chain in chains:
                chain.status = CHAIN_ATTACKS_STATUS[chain.state]
            context = {'player': player, 'faction': faction, 'combined': combined, 'factioncat': True, 'chains': chains, 'view': {'chains': True}}
            if error:
                selectError = 'apiErrorSub' if request.method == 'POST' else 'apiError'
                context.update({selectError: error["apiError"] + " List of chains not updated."})
            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


def manageReport(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId
            context = {"player": player}

            # get faction
            chainId = request.POST.get("chainId", -1)
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'inlineError': 'Faction {} not found in the database.'.format(factionId)})

            # get chain
            chain = faction.chain_set.filter(tId=chainId).first()
            if chain is None:
                return render(request, 'yata/error.html', {'inlineError': 'Chain {} not found in the database.'.format(chainId)})

            if request.POST.get("type", False) == "combine":
                chain.combine = not chain.combine
                chain.save()

            if request.POST.get("type", False) == "create":
                chain.report = True
                chain.computing = True
                c = chain.assignCrontab()
                print("report assigned to {}".format(c))
                chain.save()

            if request.POST.get("type", False) == "delete":
                chain.report = False
                chain.computing = False
                chain.combine = False
                chain.current = 0
                chain.crontab = 0
                chain.state = 0
                chain.attackchain_set.all().delete()
                chain.count_set.all().delete()
                chain.bonus_set.all().delete()
                chain.save()

            chain.status = CHAIN_ATTACKS_STATUS[chain.state]
            context = {"player": player, "chain": chain}
            return render(request, 'faction/chains/buttons.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


def report(request, chainId):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            # get page
            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Click on chain report again please."}
                return render(request, page, context)

            chains = faction.chain_set.order_by('-end')
            combined = len(chains.filter(combine=True))
            for chain in chains:
                chain.status = CHAIN_ATTACKS_STATUS[chain.state]

            # get chain
            chain = faction.chain_set.filter(tId=chainId).first()
            if chain is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, 'faction': faction, selectError: "Chain not found. It might come from a API issue. Click on chain report again please."}
                return render(request, page, context)

            # create graph
            graphs = json.loads(chain.graphs)
            graphSplit = graphs.get("hits", "").split(',')
            graphSplitCrit = graphs.get("crit", "").split(',')
            graphSplitStat = graphs.get("members", "").split(',')
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
            counts = chain.count_set.extra(select={'fieldsum': 'wins + bonus'}, order_by=('-fieldsum', '-respect'))
            chain.status = CHAIN_ATTACKS_STATUS[chain.state]
            context = dict({"player": player,
                            'factioncat': True,
                            'faction': faction,
                            'combined': combined,
                            'chain': chain,  # for general info
                            'chains': chains,  # for chain list after report
                            'counts': counts,  # for report
                            'bonus': chain.bonus_set.all(),  # for report
                            'graph': graph,  # for report
                            'view': {'chains': True, 'report': True}})  # views

            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


def iReport(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})

            chainId = request.POST.get("chainId", 0)
            memberId = request.POST.get("memberId", 0)
            print(chainId)
            if chainId in ["combined"]:
                # get all chains from joint report
                chains = faction.chain_set.filter(combine=True).order_by('start')
                counts = []
                for chain in chains:
                    count = chain.count_set.filter(attackerId=memberId).first()
                    counts.append(count)
                context = dict({'counts': counts, 'memberId': memberId})
                return render(request, 'faction/chains/ireport.html', context)
            else:
                # get chain
                chain = faction.chain_set.filter(tId=chainId).first()
                if chain is None:
                    return render(request, 'yata/error.html', {'errorMessage': 'Chain {} not found in the database.'.format(chainId)})

                # create graph
                count = chain.count_set.filter(attackerId=memberId).first()
                if count is not None:
                    graphSplit = count.graph.split(',')
                    if len(graphSplit) > 1:
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
                        graph = {'data': [], 'info': {'binsTime': 5, 'criticalHits': 1, 'speedRate': 0}}

                    context = dict({'graph': graph, 'memberId': memberId})

                    return render(request, 'faction/chains/ireport.html', context)

                else:
                    context = dict({'graph': None, 'memberId': memberId})
                    return render(request, 'faction/chains/ireport.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


def combined(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            key = player.getKey(value=False)
            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'

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
            update = faction.updateMembers(key=key, force=False)
            if 'apiError' in update:
                error = update

            # get chains
            chains = faction.chain_set.filter(combine=True).order_by('start')

            print('[VIEW jointReport] {} chains for the joint report'.format(len(chains)))
            if len(chains) < 1:
                chains = faction.chain_set.all().order_by('start')
                combined = len(chains.filter(combine=True))
                for chain in chains:
                    chain.status = CHAIN_ATTACKS_STATUS[chain.state]
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {selectError: 'No chains found for the combined report. Add chains throught the chain list.',
                           'faction': faction,
                           'combined': combined,
                           'chains': chains,
                           'player': player, 'factioncat': True, 'view': {'chains': True}}
                return render(request, page, context)

            # loop over chains
            counts = dict({})
            bonuses = dict({})
            total = {'nHits': 0, 'respect': 0.0}
            for chain in chains:
                print('[VIEW jointReport] chain {} found'.format(chain.tId))
                total['nHits'] += chain.current
                total['respect'] += float(chain.respect)
                # loop over counts
                chainCounts = chain.count_set.all()
                chainBonuses = chain.bonus_set.all()
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
            chain = {"start": 0, "end": totalTime, "tId": False}
            # context
            context = dict({'chainsReport': chains,  # chains of joint report
                            'total': total,  # for general info
                            'counts': arrayCounts,  # counts for report
                            'bonuses': arrayBonuses,  # bonuses for report
                            'player': player,
                            'chain': chain,
                            'faction': faction,
                            'factioncat': True,  # to display categories
                            'view': {'combined': True}})  # view

            if error:
                selectError = 'apiErrorSub' if request.method == 'POST' else 'apiError'
                context.update({selectError: error["apiError"] + " List of members not updated."})
            return render(request, page, context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()
