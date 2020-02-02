from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

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
            reports = faction.chain_set.filter(report=True).order_by('-start')
            context = {'player': player, 'faction': faction, 'reports': reports, 'factioncat': True, 'view': {'index': True}}
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

                # get computing reports
                reports = dict({})
                reports["Chain report"] = [r for r in faction.chain_set.filter(computing=True).all()]
                # reports["Live report"] = [] if faction.chain_set.filter(live=True).first() is not None else [("", "")]

                context = {'player': player, 'factioncat': True, "reports": reports, "bonus": BONUS_HITS, "faction": faction, 'keys': keys, 'view': {'aa': True}}

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
            message = False
            if player.factionAA and (tsnow() - faction.chainsUpda) > 15 * 60:
                key = player.getKey()
                req = apiCall('faction', faction.tId, 'chain,chains', key=key)
                faction.chainsUpda = tsnow()
                faction.save()
                if 'apiError' in req:
                    error = req
                    req = dict({})
                else:
                    message = "Chain list updated"

                chains = faction.chain_set.all()
                for k, v in req["chains"].items():
                    chain = chains.filter(tId=k).first()
                    old = tsnow() - int(v['end']) > 3600 * 24 * 31 * 6
                    if chain is None:
                        if v['chain'] >= faction.hitsThreshold and not old:
                            faction.chain_set.create(tId=k, **v)
                    else:
                        if v['chain'] < faction.hitsThreshold or old:
                            chain.delete()

                # check if live chain
                live = chains.filter(live=True).first()
                key = player.getKey()
                # req["chain"]["current"] = 15
                # req["chain"]["max"] = 10
                # req["chain"]["timeout"] = 0
                # req["chain"]["modifier"] = 1
                # req["chain"]["cooldown"] = 0
                # req["chain"]["start"] = tsnow() - 10

                if 'apiError' in req["chain"]:
                    error = req["chain"]

                elif req["chain"]["current"] > 9:
                    if live is None:
                        message = "New live report created"
                        live = faction.chain_set.create(tId=0, live=True, chain=req["chain"]["current"], start=req["chain"]["start"], end=tsnow())
                    else:
                        if live.start != int(req["chain"]["start"]):
                            message = "Old live report replaced by a new one"
                            live.delete()
                            live = faction.chain_set.create(tId=0, live=True, chain=req["chain"]["current"], start=req["chain"]["start"], end=tsnow())
                        else:
                            # message = "Update live report"
                            live.chain = req["chain"]["current"]
                            live.end = tsnow()
                            live.save()
                else:

                    if live is not None:
                        message = "Live report deleted"
                        live.delete()

            # get chains
            chains = faction.chain_set.all().order_by('-end')
            combined = len(chains.filter(combine=True))
            for chain in chains:
                chain.status = CHAIN_ATTACKS_STATUS[chain.state]
            context = {'player': player, 'faction': faction, 'combined': combined, 'factioncat': True, 'chains': chains, 'view': {'chains': True}}
            if error:
                selectError = 'apiErrorSub' if request.method == 'POST' else 'apiError'
                context.update({selectError: error["apiError"] + " List of chains not updated."})
            if message:
                selectMessage = 'validMessageSub' if request.method == 'POST' else 'validMessage'
                context.update({selectMessage: message})

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
                return render(request, 'yata/error.html', {'inlineError': 'Faction {} not found in the database.'.format(factionId)})

            chainId = request.POST.get("chainId", 0)
            memberId = request.POST.get("memberId", 0)
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
                    return render(request, 'yata/error.html', {'inlineError': 'Chain {} not found in the database.'.format(chainId)})

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
                context = {selectError: 'No chains found for the combined report. Add chains through the chain list.',
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


# SECTION: walls
def walls(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})

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

            for wall in walls:
                wall.report = wall.getReport(faction)
            context = {'player': player, 'factioncat': True, 'faction': faction, "walls": walls, 'summary': summary, 'view': {'walls': True}}
            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'
            return render(request, page, context)

        else:
            message = "You might want to log in."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


def manageWall(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            if player.factionAA:
                faction = Faction.objects.filter(tId=factionId).first()
                if faction is None:
                    return render(request, 'yata/error.html', {'inlineError': 'Faction {} not found in the database.'.format(factionId)})

                wallId = request.POST.get("wallId", 0)
                wall = Wall.objects.filter(tId=wallId).first()
                if wall is None:
                    return render(request, 'yata/error.html', {'inlineError': 'Wall {} not found in the database.'.format(wallId)})

                elif request.POST.get("type") == "delete":
                    wall.attacksreport_set.filter(faction=faction).delete()
                    wall.factions.remove(faction)
                    if not len(wall.factions.all()):
                        wall.delete()
                    return render(request, 'faction/walls/buttons.html')

                elif request.POST.get("type") == "toggle":

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
                wall.report = wall.getReport(faction)

                context = {"player": player, "wall": wall}
                return render(request, 'faction/walls/buttons.html', context)
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
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")
            # print("Author in yata: checked")

            # check if API key is valid with api call
            HTTP_KEY = request.META.get("HTTP_KEY")
            call = apiCall('user', '', '', key=HTTP_KEY)
            if "apiError" in call:
                t = -1
                m = call
                # print({"message": m, "type": t})
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")

            # check if API key sent == API key in YATA
            if HTTP_KEY != author.getKey():
                t = 0
                m = "Your API key seems to be out of date in YATA, please log again"
                # print(m)
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")
            # print("API keys match: checked")

            #  check if AA of a faction
            if not author.factionAA:
                t = 0
                m = "You don't have AA perm"
                # print(m)
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")
            # print("AA perm: checked")

            #  check if can get faction
            faction = Faction.objects.filter(tId=author.factionId).first()
            if faction is None:
                t = 0
                m = "Can't find faction {} in YATA database".format(author.factionId)
                # print(m)
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")
            # print("Faction exists: checked")

            attackers = dict({})
            defenders = dict({})
            i = 0
            for p in req.get("participants"):
                i += 1
                # print("import wall, participants before: ", p)
                p = {k.split(" ")[0].strip(): v for k, v in p.items()}
                if p.get("Name")[0] == '=':
                    p["Name"] = p["Name"][2:-1]
                # print("import wall, participants after: ", p)
                if p.get("Position") in ["Attacker"]:
                    attackers[p.get('XID')] = p
                else:
                    defenders[p.get('XID')] = p
            # print("Wall Participants: {}".format(i))

            if i > 500:
                t = 0
                m = "{} is too much participants for a wall".format(i)
                # print(m)
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")
            # print("# Participant: checked")

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
            # print("Wall headers: processed")

            if faction.tId not in [wallDic.get('attackerFactionId'), wallDic.get('defenderFactionId')]:
                t = 0
                m = "{} is not involved in this war".format(faction)
                # print(m)
                return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")
            # print("Faction in wall: checked")

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

            t = 1
            m = ", ".join(messageList)
            return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")

        except BaseException as e:
            t = 0
            m = "Server error... YATA's been poorly coded: {}".format(e)
            return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")

    else:
        return returnError(type=403, msg="You need to post. Don\'t try to be a smart ass.")


# SECTION: attacks
def attacksReports(request):
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

            # delete contract
            if request.POST.get("type") == "delete":
                contract = faction.attacksreport_set.filter(pk=request.POST["contractId"])
                contract.delete()
                # dummy render
                return render(request, page)

            # create contract
            message = False
            wallId = request.POST.get("wallId", 0)
            if wallId:
                wall = Wall.objects.filter(tId=wallId).first()
                if wall is None:
                    message = ["errorMessageSub", "Could not import Wall [{}]".format(wallId)]
                elif len(faction.attacksreport_set.filter(start=wall.tss).filter(end=wall.tse)):
                    message = ["errorMessageSub", "Wall [{}] already exists".format(wallId)]
                else:
                    report = faction.attacksreport_set.create(start=wall.tss, end=wall.tse, computing=True)
                    report.wall.add(wall)
                    c = report.assignCrontab()
                    report.save()
                    message = ["validMessageSub", "New wall created.<br>Start: {}<br>Ends: {}".format(timestampToDate(wall.tss), timestampToDate(wall.tse))]

            elif request.POST.get("type") == "new":
                try:
                    live = int(request.POST.get("live", 0))
                    start = int(request.POST.get("start", 0))
                    end = int(request.POST.get("end", 0))
                    if start and live:
                        report = faction.attacksreport_set.create(start=start, end=0, live=True, computing=True)
                        c = report.assignCrontab()
                        report.save()
                        message = ["validMessageSub", "New live report created.<br>Start: {}".format(timestampToDate(start))]
                    elif start and end and start < end:
                        report = faction.attacksreport_set.create(start=start, end=end, live=False, computing=True)
                        c = report.assignCrontab()
                        report.save()
                        message = ["validMessageSub", "New report created.<br>Start: {}<br>Ends: {}".format(timestampToDate(start), timestampToDate(end))]
                    else:
                        message = ["errorMessageSub", "Error while creating new report"]
                except BaseException as e:
                    message = ["errorMessageSub", "Error while creating new report: {}".format(e)]

            # get reports
            reports = faction.attacksreport_set.all().order_by('-end')
            for report in reports:
                report.status = REPORT_ATTACKS_STATUS[report.state]

            context = {'player': player, 'faction': faction, 'factioncat': True, 'reports': reports, 'view': {'attacksReports': True}}
            if message:
                context[message[0]] = message[1]
            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


def manageAttacks(request):
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

            reportId = request.POST.get("reportId", 0)
            report = AttacksReport.objects.filter(pk=reportId).first()
            if report is None:
                return render(request, 'yata/error.html', {'inlineError': 'Report {} not found in the database.'.format(reportId)})

            # delete contract
            if request.POST.get("type") == "delete":
                report.delete()

            return render(request, page)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


def attacksReport(request, reportId):
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

            # get breakdown
            report = faction.attacksreport_set.filter(pk=reportId).first()
            if report is None:
                context = dict({"player": player,
                                'chaincat': True,
                                'faction': faction,
                                'report': False,
                                'view': {'attacks': True}})  # views
                return render(request, page, context)

            # if modify end date
            if 'modifyEnd' in request.POST:
                tse = int(request.POST.get("end", 0))
                if report.start < tse:
                    report.end = tse
                    report.live = False
                    report.computing = True
                    report.assignCrontab()
                    report.attackreport_set.filter(timestamp_ended__gt=tse).delete()
                    report.last = min(report.end, report.last)
                    report.state = 0
                    report.save()

            attackerFactions = json.loads(report.attackerFactions)
            defenderFactions = json.loads(report.defenderFactions)

            # if click on toggle
            if request.POST.get("type") == "attackers":
                if int(request.POST["factionId"]) in attackerFactions:
                    attackerFactions.remove(int(request.POST["factionId"]))
                else:
                    attackerFactions.append(int(request.POST["factionId"]))
                report.attackerFactions = json.dumps(attackerFactions)
            elif request.POST.get("type") == "defenders":
                if int(request.POST["factionId"]) in defenderFactions:
                    defenderFactions.remove(int(request.POST["factionId"]))
                else:
                    defenderFactions.append(int(request.POST["factionId"]))
                report.defenderFactions = json.dumps(defenderFactions)
            report.save()

            attacks = dict({})
            attacksMade = 0
            attacksReceived = 0
            for r in report.attackreport_set.all():
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

            report.attacks = attacksMade
            report.defends = attacksReceived

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
            attackerFactions = json.loads(report.attackerFactions)
            defenderFactions = json.loads(report.defenderFactions)

            # context
            report.status = REPORT_ATTACKS_STATUS[report.state]
            context = dict({"player": player,
                            'factioncat': True,
                            'faction': faction,
                            'report': report,
                            'attacks': attacks,
                            'breakdown': breakdown,
                            'view': {'attacksReport': True}})  # views

            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


# SECTION: armory
def armory(request):
    from bazaar.models import BazaarData

    try:
        ITEM_TYPE = json.loads(BazaarData.objects.first().itemType)
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'

            faction = Faction.objects.filter(tId=player.factionId).first()
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found in the database."}
                return render(request, page, context)

            # update and get news
            if tsnow() - faction.armoryUpda > 60 * 15:
                state, message = faction.updateLog()
            else:
                message = False
                state = False
            news = faction.news_set.order_by("-timestamp").all()

            # get start/end ts
            start = news.last().timestamp
            end = news.first().timestamp

            # filter start/end if asked
            tss = int(request.POST.get("start", 0))
            if tss:
                print("filter tss {}".format(timestampToDate(tss)))
                news = news.filter(timestamp__gt=tss - 1)
            tse = int(request.POST.get("end", 0))
            if tse:
                print("filter tse {}".format(timestampToDate(tse)))
                news = news.filter(timestamp__lt=tse + 1)

            # get filtered start/end
            fstart = news.last().timestamp
            fend = news.first().timestamp

            # record all timestamps
            timestamps = {"start": start, "end": end, "fstart": fstart, "fend": fend, "size": len(news)}

            armory = dict({})
            timestamps["nObjects"] = 0
            for new in news.filter(type="armorynews"):
                k = new.tId
                ns = new.news.split(" ")
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

            for new in news.filter(type="fundsnews"):
                k = new.tId
                ns = new.news.split(" ")
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

            logs = dict({})
            if player.factionAA:
                r = 0
                m = 0
                for i, log in enumerate(faction.log_set.order_by("timestamp").all()):
                    if i:
                        logs[log.timestamp] = [log.money, log.donationsmoney, log.money - log.donationsmoney, log.respect, (log.money - log.donationsmoney) - m, log.respect - r]
                    r = log.respect
                    m = log.money - log.donationsmoney

            logs = sorted(logs.items(), key=lambda x: x[0], reverse=True)

            context = {'player': player, 'logs': logs, 'factioncat': True, 'faction': faction, "timestamps": timestamps, "armory": armoryType, 'view': {'armory': True}}
            if message:
                err = "validMessage" if state else "errorMessage"
                sub = "Sub" if request.method == 'POST' else ""
                context[err + sub] = message
            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()
