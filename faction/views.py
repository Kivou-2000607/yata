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

from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import StreamingHttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.html import format_html
from django.template import loader
from django.views.decorators.cache import cache_page
from django.db.models.functions import Lower
from django.core.cache import cache
import html
import os
import json
import csv
import math
import sys
import magic

from yata.handy import *
from faction.models import *
from target.models import Target
from faction.functions import *
from scipy import stats
from faction.forms import *

# (json compatible)
def index(request):
    try:
        if request.session.get('player'):
            # get player and key
            player = getPlayer(request.session["player"].get("tId"))
            key = player.getKey()

            # get user info
            user = apiCall('user', '', 'profile', key)
            if 'apiError' in user:
                msg = f'{user["apiError"]} We can\'t check your faction so you don\'t have access to this section.'
                player.chainInfo = "N/A"
                player.factionId = 0
                player.factionNa = "-"
                player.factionAA = False
                player.save()
                return JsonResponse({'error': msg}, status=400) if request.session.get('json-output') else render(request, 'faction.html', {'player': player, 'apiError': msg})


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

            targets = faction.target_set.all()

            # add/remove key depending of AA member
            faction.manageKey(player)
            chainsreports = faction.chain_set.filter(computing=True).order_by('-start')
            attacksreports = faction.attacksreport_set.filter(computing=True).order_by('-start')
            revivesreports = faction.revivesreport_set.filter(computing=True).order_by('-start')
            events = faction.event_set.order_by('timestamp')

            # get logs
            if player.factionAA:
                logs, logsAll = faction.getLogs()
            else:
                logsAll = []
                logs = []

            context = {'player': player, 'faction': faction, 'logs': logs, 'logsAll': logsAll, 'targets': targets, 'chainsreports': chainsreports, 'attacksreports': attacksreports, 'revivesreports': revivesreports, 'events': events, 'factioncat': True, 'view': {'index': True}}
            if request.session.get('json-output'):
                del context['player']
                context = json_context(context)
                return JsonResponse(context, status=200)
            else:
                return render(request, 'faction.html', context)

        else:
            # return redirect('/faction/territories/')
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def logsList(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            faction = getFaction(player.factionId)
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found in the database."}
                return render(request, 'yata/error.html', context)

            if not player.factionAA:
                return render(request, 'faction/logs/logs.html', {'logs': []})

            logs, _ = faction.getLogs(page=request.GET.get("page", 1))

            return render(request, 'faction/logs/logs.html', {'logs': logs})

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def target(request):
    try:
        if request.session.get('player') and request.method == "POST":
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                context = {"apiErrorLine": 'Faction {} not found in the database.'.format(factionId)}
                return render(request, 'faction/targets/line.html', context)

            if request.POST.get("type", False):

                if request.POST["type"] == "update":
                    # update target
                    target_id = int(request.POST["targetId"])
                    target, _ = faction.target_set.get_or_create(target_id=target_id)
                    req = apiCall("user", target.target_id, "profile,timestamp", player.getKey())
                    error, target = target.updateFromApi(req)
                    if error:
                        context = {"apiErrorLine": "Error while updating {}: {}".format(target, req.get("apiError", "Unknown error"))}
                    else:
                        context = {"player": player, "target": target, "ts": tsnow()}
                    return render(request, 'faction/targets/line.html', context)

                elif request.POST["type"] == "delete":
                    # update target
                    target_id = int(request.POST["targetId"])
                    target = faction.target_set.filter(target_id=target_id).first()
                    if target is not None:
                        faction.target_set.remove(target)

                    return render(request, 'faction/targets/line.html')

                elif request.POST["type"] == "toggle":
                    # toggle target (warning this sends requests to the target section)
                    target_id = int(request.POST["targetId"])
                    target = faction.target_set.filter(target_id=target_id).first()
                    if target is None:
                        target, _ = Target.objects.get_or_create(target_id=target_id)
                        faction.target_set.add(target)
                    else:
                        faction.target_set.remove(target)

                    factionTargets = faction.getTargetsId()
                    context = {"targetId": target_id, "player": player, "factionTargets": factionTargets}
                    return render(request, 'target/targets/faction.html', context)

            # should not happen
            context = {"apiErrorLine": 'Wrong action.'}
            return render(request, 'faction/targets/line.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except BaseException as e:
        context = {"apiErrorLine": "Error while updating target: {}".format(e)}
        return render(request, 'faction/targets/line.html', context)


# SECTION: configuration
def configurations(request):
    try:
        if request.session.get('player'):
            print(request.POST)

            # get player
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            if not player.factionAA:
                return returnError(type=403, msg="You need AA rights.")

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})

            faction.manageKey(player)

            # update members before to avoid coming here before having members
            faction.updateMembers(key=player.getKey(value=False), force=False)

            # get keys
            keys = faction.masterKeys.filter(useSelf=True)
            faction.nKeys = len(keys.filter(useFact=True))
            faction.save()

            # tmp variables to pass for templates
            faction.armoryTime = faction.getHistName("armory")
            faction.chainsTime = faction.getHistName("chains")
            faction.attacksTime = faction.getHistName("attacks")
            faction.revivesTime = faction.getHistName("revives")
            faction.crimesTime = faction.getHistName("crimes")
            faction.liveTime = faction.getHistName("live")

            events = faction.event_set.order_by('timestamp')
            context = {'player': player, "events": events, 'factioncat': True, "bonus": BONUS_HITS, "faction": faction, 'posterForm': [PosterHeadForm(), PosterTailForm()], 'keys': keys, 'view': {'aa': True}}

            # handle upload of poster head/tail
            if request.POST.get("upload_head"):
                form = PosterHeadForm(request.POST, request.FILES, instance=faction)
                valid_form = form.is_valid()
                if valid_form:
                    form.save()
                    context["validMessageSub"] = "Poster header uploaded"
                else:
                    context["errorMessageSub"] = "Error uploading the image (size should be < 500kb)"
            if request.POST.get("upload_tail"):
                form = PosterTailForm(request.POST, request.FILES, instance=faction)
                valid_form = form.is_valid()
                if valid_form:
                    form.save()
                    context["validMessageSub"] = "Poster footer uploaded"
                else:
                    context["errorMessageSub"] = "Error uploading the image (size should be < 500kb)"

            # add poster
            if faction.poster:
                fntId = {i: [f.split("__")[0].replace("-", " "), int(f.split("__")[1].split(".")[0])] for i, f in enumerate(sorted(os.listdir(FONT_DIR)))}
                posterOpt = json.loads(faction.posterOpt)
                context['posterOpt'] = posterOpt
                context['random'] = random.randint(0, 65535)
                context['fonts'] = fntId
                updatePoster(faction)





            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'
            if request.POST.get("upload_image"):
                page = 'faction.html'

            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def configurationsKey(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            player = getPlayer(request.session["player"].get("tId"))

            if not player.factionAA:
                return returnError(type=403, msg="You need AA rights.")

            key = player.key_set.first()
            key.useFact = not key.useFact
            key.save()

            context = {"player": player, "key": key}
            return render(request, 'faction/aa/keys.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def configurationsEvent(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            player = getPlayer(request.session["player"].get("tId"))

            if not player.factionAA:
                return returnError(type=403, msg="You need AA rights.")

            faction = Faction.objects.filter(tId=player.factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})

            if request.POST.get("type") == "delete":
                # delete event
                faction.event_set.filter(pk=request.POST.get("eventId")).delete()
                # dummy return
                return render(request, 'faction/aa/events.html')

            elif request.POST.get("type") == "create":
                v = dict({})
                v["title"] = request.POST.get("title") if request.POST.get("title")[:63] else "{} event".format(faction.name)[:63]
                v["description"] = request.POST.get("description")[:255]
                v["timestamp"] = request.POST.get("ts")
                stack = int(request.POST.get("stack", 0))
                v["stack"] = bool(stack)
                reset = int(request.POST.get("reset", 0))
                v["reset"] = bool(reset)
                faction.event_set.create(**v)

            events = faction.event_set.order_by('timestamp')
            context = {"player": player, "events": events}
            return render(request, 'faction/aa/events.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def configurationsThreshold(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            if not player.factionAA:
                return returnError(type=403, msg="You need AA rights.")

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

    except Exception as e:
        return returnError(exc=e, session=request.session)


def configurationsPoster(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            if not player.factionAA:
                return returnError(type=403, msg="You need AA rights.")

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})

            # case we enable/disable or hold/unhold the poster
            if request.POST.get("type", False) == "enable":
                faction.poster = not faction.poster
                faction.posterHold = faction.posterHold if faction.poster else False

                if not faction.poster:
                    faction.posterImg.delete()
                    faction.posterGymImg.delete()
                    faction.posterHeadImg.delete()
                    faction.posterTailImg.delete()
                    faction.save()

            elif request.POST.get("type", False) == "hold":
                faction.posterHold = not faction.posterHold

            # update poster
            if request.method == "POST" and request.POST.get("posterConf"):
                updatePosterConf(faction, request.POST.dict())

            faction.save()

            context = {'faction': faction}

            # update poster if needed
            url = os.path.join(settings.MEDIA_ROOT, f"posters/{faction.tId}.png")
            if faction.poster:
                fntId = {i: [f.split("__")[0].replace("-", " "), int(f.split("__")[1].split(".")[0])] for i, f in enumerate(sorted(os.listdir(FONT_DIR)))}
                posterOpt = json.loads(faction.posterOpt)
                context['posterOpt'] = posterOpt
                context['random'] = random.randint(0, 65535)
                context['fonts'] = fntId
                updatePoster(faction)

            elif not faction.poster and os.path.exists(url):
                os.remove(url)
                context['posterDeleted'] = True

            return render(request, 'faction/aa/poster.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


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
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Check again later."}
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

    except Exception as e:
        return returnError(exc=e, session=request.session)


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

            # update status and last action
            try:
                status = membersAPI.get(memberId, dict({})).get("status", {})
                member.updateStatus(**status)
                lastAction = membersAPI.get(memberId, dict({})).get("last_action", {})
                member.updateLastAction(**lastAction)
            except BaseException as e:
                return render(request, 'faction/members/line.html', {'errorMessage': 'Error with member {}: {}'.format(memberId, e)})

            # update private data
            tmpP = Player.objects.filter(tId=memberId).first()
            if tmpP is None:
                member.shareE = -1
                member.shareN = -1
                member.shareS = -1
                member.save()
            elif member.shareE > 0 or member.shareN > 0 or member.shareS > 0:
                req = apiCall("user", "", "perks,bars,crimes,battlestats,honors,refills,cooldowns", key=tmpP.getKey())
                member.updateEnergy(key=tmpP.getKey(), req=req)
                member.updateStats(key=tmpP.getKey(), req=req)
                member.updateNNB(key=tmpP.getKey(), req=req)
                member.updateHonors(key=tmpP.getKey(), req=req)
            elif member.singleHitHonors < 3:
                req = apiCall("user", "", "honors", key=tmpP.getKey())
                member.updateHonors(key=tmpP.getKey(), req=req)
            member.save()

            context = {"player": player, "member": member}
            return render(request, 'faction/members/line.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


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
                    member.save()
                    return render(request, 'faction/members/energy.html', {'errorMessage': error.get('apiErrorString', 'error')})
                else:
                    context = {"player": player, "member": member}
                    member.save()
                    return render(request, 'faction/members/energy.html', context)

            elif request.POST.get("type") == "nerve":
                member.shareN = 0 if member.shareN else 1
                error = member.updateNNB(key=player.getKey())
                # handle api error
                if error:
                    member.shareN = 0
                    member.nnb = 0
                    member.arson = 0
                    member.save()
                    return render(request, 'faction/members/nnb.html', {'errorMessage': error.get('apiErrorString', 'error')})
                else:
                    context = {"player": player, "member": member}
                    member.save()
                    return render(request, 'faction/members/nnb.html', context)

            elif request.POST.get("type") == "stats":
                member.shareS = 0 if member.shareS else 1
                error = member.updateStats(key=player.getKey())
                # handle api error
                if error:
                    member.shareS = 0
                    member.dexterity = 0
                    member.defense = 0
                    member.strength = 0
                    member.speed = 0
                    member.save()
                    return render(request, 'faction/members/stats.html', {'errorMessage': error.get('apiErrorString', 'error')})
                else:
                    context = {"player": player, "member": member}
                    member.save()
                    return render(request, 'faction/members/stats.html', context)

                # member.save()
            else:
                return render(request, 'faction/members/nnb.html', {'errorMessage': '?'})

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


# SECTION: chains
# (json compatible)
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
                msg = f'Faction {factionId} not found in the database'
                return JsonResponse({'error': msg}, status=400) if request.session.get('json-output') else render(request, page, {'player': player, selectError: msg})

            # update chains if AA
            error = False
            message = False
            if player.factionAA and tsnow() - faction.chainsUpda > 15 * 60:
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
                apichains = req.get("chains")
                if apichains is not None:
                    for k, v in req.get("chains", dict({})).items():
                        old = tsnow() - int(v['end']) > faction.getHist("chains")
                        new = tsnow() - int(v['end']) < v['chain'] * 10  # wait end of live chain cooldown

                        if v['chain'] < faction.hitsThreshold or old or new:
                            chains.filter(tId=k).delete()
                        elif v['chain'] >= faction.hitsThreshold and not old:
                            try:
                                faction.chain_set.update_or_create(tId=k, defaults=v)
                            except BaseException:
                                faction.chain_set.filter(tId=k).all().delete()
                                faction.chain_set.update_or_create(tId=k, defaults=v)

                # check if live chain
                live = chains.filter(live=True).first()
                key = player.getKey()
                # req["chain"]["current"] = 15
                # req["chain"]["max"] = 10
                # req["chain"]["timeout"] = 0
                # req["chain"]["modifier"] = 1
                # req["chain"]["cooldown"] = 0
                # req["chain"]["start"] = tsnow() - 10

                if 'apiError' in req.get("chain", {"apiError": "chain not found int API request"}):
                    error = req.get("chain", {"apiError": "chain not found int API request"})

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
            chains = faction.chain_set.order_by('-end')
            combined = len(chains.filter(combine=True))
            for chain in chains:
                chain.status = CHAIN_ATTACKS_STATUS[chain.state]
            context = {'player': player, 'faction': faction, 'combined': combined, 'factioncat': True, 'chains': chains, 'view': {'chains': True}}
            if error:
                selectError = 'apiErrorSub' if request.method == 'POST' else 'apiError'
                context.update({selectError: error["apiError"]})
            if message:
                selectMessage = 'validMessageSub' if request.method == 'POST' else 'validMessage'
                context.update({selectMessage: message})

            if request.session.get('json-output'):
                del context['player']
                context = json_context(context)
                # for k, v in context.items():
                #     print(k, v)
                return JsonResponse(context, status=200)
            else:
                return render(request, page, context)


        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)

# (json compatible)
def manageReport(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            post_payload = get_payload(request)

            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId
            context = {"player": player}

            if not player.factionAA:
                return returnError(type=403, msg="You need AA rights.")

            # get faction
            chainId = post_payload.get("chainId", -1)
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                msg = f'Faction {factionId} not found in the database'
                return JsonResponse({'error': msg}, status=400) if request.session.get('json-output') else render(request, 'yata/error.html', {'inlineError': msg})

            # get chain
            chain = faction.chain_set.filter(tId=chainId).first()
            if chain is None:
                msg = f'Chain {chainId} not found in the database'
                return JsonResponse({'error': msg}, status=400) if request.session.get('json-output') else render(request, 'yata/error.html', {'inlineError': msg})

            if post_payload.get("type", False) == "share":
                if chain.shareId == "":
                    chain.shareId = randomSlug()
                else:
                    chain.shareId = ""
                chain.save()
                context = {"chain": chain}
                return JsonResponse(json_context(context), status=200) if request.session.get('json-output') else render(request, 'faction/chains/share.html', context)

            if post_payload.get("type", False) == "combine":
                chain.combine = not chain.combine
                chain.save()

            if post_payload.get("type", False) == "create":
                chain.report = True
                chain.computing = True
                chain.cooldown = False
                chain.status = 1
                chain.addToEnd = 10
                c = chain.assignCrontab()
                # print("report assigned to {}".format(c))
                chain.save()

            if post_payload.get("type", False) == "cooldown":
                if chain.cooldown:
                    chain.attackchain_set.filter(timestamp_ended__gt=chain.end).delete()

                chain.report = True
                chain.cooldown = not chain.cooldown
                chain.computing = True
                chain.state = 1
                c = chain.assignCrontab()
                print("report assigned to {}".format(c))
                chain.save()

            if post_payload.get("type", False) == "delete":
                chain.report = False
                chain.graphs = "{}"
                chain.shareId = ""
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

            if request.session.get('json-output'):
                del context['player']
                return JsonResponse(json_context(context), status=200)
            else:
                return render(request, 'faction/chains/buttons.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


# (json compatible)
def report(request, chainId, share=False):
    try:
        if request.session.get('player') or share == "share":

            # get page
            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'

            if share == "share":
                # if shared report
                chain = Chain.objects.filter(shareId=chainId).first()
                if chain is None:
                    return returnError(type=404, msg="Shared report {} not found.".format(chainId))
                faction = chain.faction

            else:
                player = getPlayer(request.session["player"].get("tId"))
                factionId = player.factionId
                faction = Faction.objects.filter(tId=factionId).first()

                # get faction
                if faction is None:
                    selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                    msg = f'Faction {factionId} not found in the database'
                    return JsonResponse({'error': msg}, status=400) if request.session.get('json-output') else render(request, page, {selectError: msg})

                chains = faction.chain_set.order_by('-end')
                combined = len(chains.filter(combine=True))
                for chain in chains:
                    chain.status = CHAIN_ATTACKS_STATUS[chain.state]

                # get chain
                chain = faction.chain_set.filter(tId=chainId).first() if chainId.isdigit() else None
                if chain is None:
                    selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                    msg = f'Chain {chainId} not found in the database'
                    return JsonResponse({'error': msg}, status=400) if request.session.get('json-output') else render(request, page, {selectError: msg})

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
                x = numpy.zeros(len(graphSplit))
                y = numpy.zeros(len(graphSplit))
                for i, (line, lineCrit) in enumerate(zip(graphSplit, graphSplitCrit)):
                    splt = line.split(':')
                    spltCrit = lineCrit.split(':')
                    cummulativeHits += int(splt[1])
                    graph['data'].append([timestampToDate(int(splt[0])), int(splt[1]), cummulativeHits, int(splt[0])])
                    graph['dataCrit'].append([timestampToDate(int(splt[0])), int(spltCrit[0]), int(spltCrit[1]), int(spltCrit[2])])
                    speedRate = cummulativeHits * 300 / float((int(graphSplit[-1].split(':')[0]) - int(graphSplit[0].split(':')[0])))  # hits every 5 minutes
                    graph['info']['speedRate'] = speedRate
                    x[i] = int(splt[0])
                    y[i] = cummulativeHits

                # get linear regressions
                if chain.live:
                    #  y = ax + b (y: hits, x: timestamp)
                    a, b, _, _, _ = stats.linregress(x[-20:], y[-20:])
                    print("[view.chain.index] linreg a={} b={}".format(a, b))
                    a = max(a, 0.00001)
                    try:
                        ETA = timestampToDate(int((chain.getNextBonus() - b) / a))
                    except BaseException as e:
                        ETA = "unable to compute EAT ({})".format(e)
                    graph['info']['ETALast'] = ETA
                    graph['info']['regLast'] = [a, b]

                    a, b, _, _, _ = stats.linregress(x, y)
                    print("[view.chain.index] linreg a={} b={}".format(a, b))
                    try:
                        ETA = timestampToDate(int((chain.getNextBonus() - b) / a))
                    except BaseException as e:
                        ETA = "unable to compute EAT ({})".format(e)
                    graph['info']['ETA'] = ETA
                    graph['info']['reg'] = [a, b]

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
            if share == "share":
                context = dict({'skipheader': True,
                                'share': True,
                                'faction': faction,
                                'chain': chain,  # for general info
                                'counts': counts,  # for report
                                'bonus': chain.bonus_set.all(),  # for report
                                'graph': graph,  # for report
                                'view': {'report': True}})  # views
            else:
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

            if request.session.get('json-output'):
                del context['player']
                del context['chains']
                return JsonResponse(json_context(context), status=200)
            else:
                return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


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
                member = faction.member_set.filter(tId=memberId).first()
                counts = {"graph": [], "chains": []}
                for chain in chains:
                    inFaction = tsnow() - chain.start - (member.daysInFaction * 3600 * 24) < 0 if member is not None else True
                    if inFaction:
                        count = chain.count_set.filter(attackerId=memberId).first()
                        if count is not None:
                            counts["graph"].append([timestampToDate(count.chain.start), 100 * (count.wins + count.bonus) / float(count.chain.chain)])
                            counts["chains"].append(count)

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

    except Exception as e:
        return returnError(exc=e, session=request.session)


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
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Check again later."}
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
                chains = faction.chain_set.order_by('start')
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
                chain_bonuses = chain.bonus_set.all()
                for bonus in chain_bonuses:
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
                        counts[count.attackerId]['fair_fight'] += count.fair_fight
                        counts[count.attackerId]['war'] += count.war
                        counts[count.attackerId]['warhits'] += count.warhits
                        counts[count.attackerId]['retaliation'] += count.retaliation
                        counts[count.attackerId]['group_attack'] += count.group_attack
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
                                                    'fair_fight': count.fair_fight,
                                                    'war': count.war,
                                                    'warhits': count.warhits,
                                                    'retaliation': count.retaliation,
                                                    'group_attack': count.group_attack,
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

            now = tsnow()
            bulk_u_mgr = BulkUpdateManager(['bonusScore'], chunk_size=100)
            for i, bonus in enumerate(arrayBonuses):
                member = faction.member_set.filter(tId=bonus[0]).first()
                if member is None:
                    arrayBonuses[i].append(False)
                    arrayBonuses[i].append(False)
                    member.bonusScore = 0
                else:
                    arrayBonuses[i].append(now - member.lastActionTS)
                    arrayBonuses[i].append(member.singleHitHonors if member.shareE > -1 else -1)
                    member.bonusScore = int(100 * bonus[4] / float(max(1, bonus[3])))

                bulk_u_mgr.add(member)
            bulk_u_mgr.done()

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

    except Exception as e:
        return returnError(exc=e, session=request.session)


def membersExport(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))

            # in case of error
            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'

            # get faction
            faction = Faction.objects.filter(tId=player.factionId).first()
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Check again later."}
                return render(request, page, context)

            # get members
            members = faction.member_set.all().order_by(Lower("name"))

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="members_report.csv"'

            csv_data = [['Name', 'ID', 'Last Action', 'Status', 'Days In Faction', 'Energy', 'CE Rank', 'NNB', 'EA', 'Strength', 'Speed', 'Defence', 'Dexterity', 'Total']]

            for m in members:
                if not player.factionAA:
                    m.strength = 0
                    m.speed = 0
                    m.defense = 0
                    m.dexterity = 0
                csv_data.append([m.name, m.tId, m.lastAction, m.state, m.daysInFaction, m.energy, m.crimesRank, m.nnb, m.arson, m.strength, m.speed, m.defense, m.dexterity, m.getTotalStats])

            t = loader.get_template('faction/members/export.txt')
            c = {'data': csv_data}
            response.write(t.render(c))

            return response

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def reportExport(request, chainId, type):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            # in case of error
            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Check again later."}
                return render(request, page, context)

            # get chain
            chain = faction.chain_set.filter(tId=chainId).first() if chainId.isdigit() else None
            if chain is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, 'faction': faction, selectError: "Chain not found. It might come from a API issue. Check again later."}
                return render(request, page, context)

            if type == "0":
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="Chain_report_{}_counts.csv"'.format(chain.tId)

                csv_data = [['Attacker ID', 'Name', 'Hits', 'Bonus', 'Wins', 'Respect', 'Fair Fight', 'War', 'Retaliation', 'Group Attack', 'Overseas', 'Days In Faction', 'Watcher', 'War Hits']]

                for c in chain.count_set.extra(select={'fieldsum': 'wins + bonus'}, order_by=('-fieldsum', '-respect')):
                    csv_data.append([c.attackerId, c.name, c.hits, c.bonus, c.wins, c.respect, c.fair_fight, c.war, c.retaliation, c.group_attack, c.overseas, c.daysInFaction, c.watcher, c.warhits])

                t = loader.get_template('faction/chains/csv-counts.txt')
                c = {'data': csv_data}
                response.write(t.render(c))

                return response

            return returnError(type=403, msg="YOLOOO")

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


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

            # get wall history
            wallHistory, state = faction.getWallHistory()
            if state:
                for k, v in wallHistory:
                    for wall in v["walls"]:
                        wall.append(walls.filter(tId=wall[1]).first())
                context['wallHistory'] = wallHistory

            else:
                if 'apiError' in wallHistory:
                    selectError = 'apiErrorSub' if request.method == 'POST' else 'apiError'
                    context[selectError] = wallHistory["apiError"] + " Wall history not displayed."
                else:
                    selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                    context[selectError] = "No AA key found for the faction. Wall history not displayed."

            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'
            return render(request, page, context)

        else:
            message = "You might want to log in."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def manageWall(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            if not player.factionAA:
                return returnError(type=403, msg="You need AA rights.")

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
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


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
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Check again later."}
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
                    message = ["validMessageSub", "New wall created.<br>Starts: {}<br>Ends: {}".format(timestampToDate(wall.tss, fmt=True), timestampToDate(wall.tse, fmt=True))]

            elif request.POST.get("type") == "new":
                try:
                    live = int(request.POST.get("live", 0))
                    start = int(request.POST.get("start", 0))
                    end = int(request.POST.get("end", 0))
                    if tsnow() - start > faction.getHist("attacks"):
                        message = ["errorMessageSub", "Starting date too far in the past (limit is {}).<br>Starts: {}".format(faction.getHistName("attacks"), timestampToDate(start, fmt=True))]
                    elif live and tsnow() - start > faction.getHist("live"):
                        message = ["errorMessageSub", "Starting date too far in the past for a live record (limit is {}).<br>Starts: {}".format(faction.getHistName("live"), timestampToDate(start, fmt=True))]
                    elif start > tsnow():
                        message = ["errorMessageSub", "Select a starting date in the past.<br>Starts: {}".format(timestampToDate(start, fmt=True))]
                    elif start and live:
                        report = faction.attacksreport_set.create(start=start, end=0, live=True, computing=True)
                        c = report.assignCrontab()
                        report.save()
                        message = ["validMessageSub", "New live report created.<br>Starts: {}".format(timestampToDate(start, fmt=True))]
                    elif start and end and start < end:
                        report = faction.attacksreport_set.create(start=start, end=end, live=False, computing=True)
                        c = report.assignCrontab()
                        report.save()
                        message = ["validMessageSub", "New report created.<br>Starts: {}<br>Ends: {}".format(timestampToDate(start, fmt=True), timestampToDate(end, fmt=True))]
                    else:
                        message = ["errorMessageSub", "Error while creating new report"]
                except BaseException as e:
                    message = ["errorMessageSub", "Error while creating new report: {}".format(e)]

            # get reports
            reports = faction.attacksreport_set.order_by('-end')
            for _ in reports:
                _.status = REPORT_ATTACKS_STATUS[_.state]

            context = {'player': player, 'faction': faction, 'factioncat': True, 'reports': reports, 'view': {'attacksReports': True}}
            if message:
                context[message[0]] = message[1]
            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def manageAttacks(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            if not player.factionAA:
                return returnError(type=403, msg="You need AA rights.")

            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Check again later."}
                return render(request, page, context)

            reportId = request.POST.get("reportId", 0)
            report = AttacksReport.objects.filter(pk=reportId).first()
            if report is None:
                return render(request, 'yata/error.html', {'inlineError': 'Report {} not found in the database.'.format(reportId)})

            # toggle share
            if request.POST.get("type", False) == "share":
                if report.shareId == "":
                    report.shareId = randomSlug()
                else:
                    report.shareId = ""
                report.save()
                context = {"report": report}
                return render(request, 'faction/attacks/share.html', context)

            # delete contract
            if request.POST.get("type") == "delete":
                report.delete()

            return render(request, page)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def attacksReport(request, reportId, share=False):
    try:
        if request.session.get('player') or share == "share":
            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'

            if share == "share":
                # if shared report
                player = False
                report = AttacksReport.objects.filter(shareId=reportId).first()
                if report is None:
                    return returnError(type=404, msg="Shared report {} not found.".format(reportId))
                faction = report.faction

            else:
                player = getPlayer(request.session["player"].get("tId"))
                factionId = player.factionId

                # get faction
                faction = Faction.objects.filter(tId=factionId).first()
                if faction is None:
                    selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                    context = {'player': player, selectError: "Faction not found. It might come from a API issue. Check again later."}
                    return render(request, page, context)

                # get breakdown
                if not reportId.isdigit():
                    selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                    context = dict({"player": player, selectError: "Wrong report ID: {}.".format(reportId), 'factioncat': True, 'faction': faction, 'report': False})  # views
                    return render(request, page, context)

                report = faction.attacksreport_set.filter(pk=reportId).first()
                if report is None:
                    selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                    context = dict({"player": player,
                                    selectError: "Report {} not found.".format(reportId),
                                    'factioncat': True,
                                    'faction': faction,
                                    'report': False})  # views
                    return render(request, page, context)

            o_fa = int(request.GET.get('o_fa', 0))
            orders = [False, "-hits", "-attacks", "-defends", "-attacked"]
            order_fa = orders[o_fa]

            if request.GET.get('p_fa') is not None or request.GET.get('o_fa') is not None:
                if order_fa:
                    paginator = Paginator(report.attacksfaction_set.order_by(order_fa), 10)
                else:
                    paginator = Paginator(report.attacksfaction_set.order_by("-hits", "-attacks", "-defends", "-attacked"), 10)
                p_fa = request.GET.get('p_fa')
                factions = paginator.get_page(p_fa)
                page = "faction/attacks/factions.html"
                context = {"player": player, "faction": faction, "report": report, "factions": factions, "o_fa": o_fa}
                return render(request, page, context)

            o_pl = int(request.GET.get('o_pl', 0))
            orders = [False, "-hits", "-attacks", "-defends", "-attacked"]
            order_pl = orders[o_pl]

            if request.GET.get('p_pl') is not None or request.GET.get('o_pl') is not None:
                if order_pl:
                    paginator = Paginator(report.attacksplayer_set.filter(show=True).exclude(player_faction_id=-1).order_by(order_pl), 10)
                else:
                    paginator = Paginator(report.attacksplayer_set.filter(show=True).exclude(player_faction_id=-1).order_by("-hits", "-attacks", "-defends", "-attacked"), 10)
                p_pl = request.GET.get('p_pl')
                players = paginator.get_page(p_pl)
                page = "faction/attacks/players.html"
                context = {"player": player, "faction": faction, "report": report, "players": players, "o_pl": o_pl}
                return render(request, page, context)

            # if modify end date
            if 'modifyEnd' in request.POST:

                if not player.factionAA:
                    return returnError(type=403, msg="You need AA rights.")

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

            # from when reports were filled by the user
            # if 'update' in request.POST:
            #
            #     if not player.factionAA:
            #         return returnError(type=403, msg="You need AA rights.")
            #
            #     report.fillReport()

            factions = json.loads(report.factions)

            # if click on toggle
            p_fa = False
            if request.POST.get("type") == "faction_filter":
                try:
                    f = int(request.POST["factionId"])
                    if f in factions:
                        factions.remove(f)
                        report.attacksfaction_set.filter(faction_id=f).update(show=False)
                        report.attacksplayer_set.filter(player_faction_id=f).update(show=False)
                    else:
                        factions.append(f)
                        report.attacksfaction_set.filter(faction_id=f).update(show=True)
                        report.attacksplayer_set.filter(player_faction_id=f).update(show=True)
                    report.factions = json.dumps(factions)
                    report.save()
                    p_fa = request.POST["page"]
                except BaseException as e:
                    print("Error toggle faction {}".format(e))

            report.player_filter = 0
            report.save()
            attacksFilters = Q(attacker_faction__in=factions) | Q(defender_faction__in=factions)
            attacks_set = report.attackreport_set.filter(attacksFilters).order_by("-timestamp_ended")
            paginator = Paginator(attacks_set, 25)
            p_at = request.GET.get('p_at')
            attacks = paginator.get_page(p_at)

            attackers = dict({})
            defenders = dict({})
            for r in attacks_set:
                attackers[r.attacker_id] = r.attacker_name
                defenders[r.defender_id] = r.defender_name
            attackers = sorted(attackers.items(), key=lambda x: x[1].lower())
            defenders = sorted(defenders.items(), key=lambda x: x[1].lower())

            if order_fa:
                factions = Paginator(report.attacksfaction_set.order_by(order_fa), 10)
            else:
                factions = Paginator(report.attacksfaction_set.order_by("-hits", "-attacks", "-defends", "-attacked"), 10)
            p_fa = request.GET.get('p_fa') if not p_fa else p_fa
            factions = factions.get_page(p_fa)

            if order_pl:
                players = Paginator(report.attacksplayer_set.filter(show=True).exclude(player_faction_id=-1).order_by(order_pl), 10)
            else:
                players = Paginator(report.attacksplayer_set.filter(show=True).exclude(player_faction_id=-1).order_by("-hits", "-attacks", "-defends", "-attacked"), 10)
            p_pl = request.GET.get('p_pl')
            players = players.get_page(p_pl)

            # context
            report.status = REPORT_ATTACKS_STATUS[report.state]
            # get reports
            reports = faction.attacksreport_set.order_by('-end')
            for _ in reports:
                _.status = REPORT_ATTACKS_STATUS[_.state]

            if share == "share":
                context = dict({"skipheader": True,
                                'share': True,
                                'faction': faction,
                                'factions': factions,
                                'players': players,
                                'report': report,
                                'o_pl': o_pl,
                                'o_fa': o_fa,
                                'view': {'attacksReport': True}})  # views
            else:
                context = dict({"player": player,
                                'factioncat': True,
                                'faction': faction,
                                'factions': factions,
                                'players': players,
                                'members': members,
                                'report': report,
                                'reports': reports,
                                'attacks': attacks,
                                'attackers': attackers,
                                'defenders': defenders,
                                'o_pl': o_pl,
                                'o_fa': o_fa,
                                'view': {'attacksReport': True}})  # views

            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def attacksMembers(request, reportId):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Check again later."}
                return render(request, 'yata/error.html', context)

            # get breakdown
            report = faction.attacksreport_set.filter(pk=reportId).first()
            if report is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Report {} not found.".format(reportId)}
                return render(request, 'yata/error.html', context)

            o_me = int(request.GET.get('o_me', 6))
            if request.GET.get('p_me') is not None or request.GET.get('o_me') is not None:
                members = Paginator(report.getMembersBreakdown(order=o_me), 10)
                p_me = request.GET.get('p_me')
                members = members.get_page(p_me)
                page = "faction/attacks/members.html"
                context = {"player": player, "faction": faction, "report": report, "members": members, "o_me": o_me}
                return render(request, page, context)

            members = Paginator(report.getMembersBreakdown(o_me), 10)
            p_me = request.GET.get('p_me')
            members = members.get_page(p_me)

            return render(request, 'faction/attacks/members.html', {'report': report, 'members': members, 'o_me': o_me})

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def attacksList(request, reportId):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Check again later."}
                return render(request, 'yata/error.html', context)

            # get breakdown
            report = faction.attacksreport_set.filter(pk=reportId).first()
            if report is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Report {} not found.".format(reportId)}
                return render(request, 'yata/error.html', context)

            if request.POST.get("type", False) and request.POST["type"] == "filter":
                if report.player_filter == int(request.POST["playerId"]):
                    report.player_filter = 0
                else:
                    report.player_filter = int(request.POST["playerId"])
                report.save()

            factions = json.loads(report.factions)

            if report.player_filter:
                attacksFilters = Q(attacker_id=report.player_filter) | Q(defender_id=report.player_filter)
            else:
                attacksFilters = Q(attacker_faction__in=factions) | Q(defender_faction__in=factions)
            attacks_set = report.attackreport_set.filter(attacksFilters).order_by("-timestamp_ended")
            paginator = Paginator(attacks_set, 25)
            p_at = request.GET.get('p_at', 1)
            attacks = paginator.get_page(p_at)

            attackers = dict({})
            defenders = dict({})
            for r in attacks_set:
                attackers[r.attacker_id] = r.attacker_name
                defenders[r.defender_id] = r.defender_name
            attackers = sorted(attackers.items(), key=lambda x: x[1])
            defenders = sorted(defenders.items(), key=lambda x: x[1])

            if p_at is not None:
                return render(request, 'faction/attacks/attacks.html', {'report': report, 'attacks': attacks, 'defenders': defenders, 'attackers': attackers})
            else:
                return returnError(type=403, msg="You need to get a page.")

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def attacksExport(request, reportId, type):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            # in case of error
            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Check again later."}
                return render(request, page, context)

            # get breakdown
            if not reportId.isdigit():
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = dict({"player": player, selectError: "Wrong report ID: {}.".format(reportId), 'factioncat': True, 'faction': faction, 'report': False})  # views
                return render(request, page, context)

            report = faction.attacksreport_set.filter(pk=reportId).first()
            if report is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = dict({"player": player,
                                selectError: "Report {} not found.".format(reportId),
                                'factioncat': True,
                                'faction': faction,
                                'report': False})  # views
                return render(request, page, context)

            if type == "0":
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="Attacks_report_{}_factions.csv"'.format(report.pk)

                csv_data = [['Faction Id', 'Faction Name', 'Hits', 'Attacks', 'Defends', 'Attacked', 'Filter']]

                factions = report.attacksfaction_set.order_by("-hits", "-attacks", "-defends", "-attacked")
                for faction in factions:
                    if faction.faction_id == 0:
                        faction.faction_name = "-"
                    elif faction.faction_id == -1:
                        faction.faction_name = "Stealth"
                    csv_data.append([faction.faction_id, html.unescape(faction.faction_name), faction.hits, faction.attacks, faction.defends, faction.attacked, faction.show])

                t = loader.get_template('faction/attacks/csv-factions.txt')
                c = {'data': csv_data}
                response.write(t.render(c))

                return response

            elif type == "1":
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="Attacks_report_{}_players.csv"'.format(report.pk)

                csv_data = [['Faction Id', 'Faction Name', 'Player Id', 'Player Name', 'Hits', 'Attacks', 'Defends', 'Attacked', 'Filter']]

                players = report.attacksplayer_set.filter(show=True).exclude(player_faction_id=-1).order_by("-hits", "-attacks", "-defends", "-attacked")
                for player in players:
                    if player.player_faction_id == 0:
                        player.player_faction_name = "-"
                    csv_data.append([player.player_faction_id, html.unescape(player.player_faction_name), player.player_id, player.player_name, player.hits, player.attacks, player.defends, player.attacked, player.show])

                t = loader.get_template('faction/attacks/csv-players.txt')
                c = {'data': csv_data}
                response.write(t.render(c))

                return response

            elif type == "2":
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="Attacks_report_{}_breakdown.csv"'.format(report.pk)

                csv_data = [['Player Id', 'Player Name',
                             'Outgoing Win', 'Outgoing Mug', 'Outgoing Hosp', 'Outgoing War', 'Outgoing Win', 'Outgoing Lost', 'Outgoing Total',
                             'Incoming Win', 'Incoming Mug', 'Incoming Hosp', 'Incoming War', 'Incoming Win', 'Incoming Lost', 'Incoming Total',
                             ]]

                players = report.getMembersBreakdown()
                for k, v in players:
                    # (id, {'name': 'Name', 'out': [40, 2, 1, 0, 43, 1, 44], 'in': [0, 0, 0, 0, 0, 1, 1]})
                    data = [k, v["name"]]
                    for _ in v["out"]:
                        data.append(_)
                    for _ in v["in"]:
                        data.append(_)
                    csv_data.append(data)

                t = loader.get_template('faction/attacks/csv-breakdown.txt')
                c = {'data': csv_data}
                response.write(t.render(c))

                return response

            elif type == "3":
                # return error if no filters
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="Attacks_report_{}_attacks.csv"'.format(report.pk)

                if report.player_filter:
                    attacksFilters = Q(attacker_id=report.player_filter) | Q(defender_id=report.player_filter)
                else:
                    factions = json.loads(report.factions)
                    attacksFilters = Q(attacker_faction__in=factions) | Q(defender_faction__in=factions)

                attacks = report.attackreport_set.filter(attacksFilters).order_by("-timestamp_ended")

                keys = ["tId", "timestamp_started",
                        "attacker_faction", "attacker_factionname", "attacker_id", "attacker_name",
                        "defender_faction", "defender_factionname", "defender_id", "defender_name",
                        "result", "respect_gain", "chain", "fair_fight", "war", "retaliation", "group_attack", "overseas", "chain_bonus", "code"
                        ]

                csv_data = [keys]

                for a in list(attacks.values()):
                    if a.get("defender_faction") == 0:
                        a["defender_factionname"] = "-"
                    elif a.get("defender_faction") == -1:
                        a["defender_factionname"] = "Stealth"
                    if a.get("attacker_faction") == 0:
                        a["attacker_factionname"] = "-"
                    elif a.get("attacker_faction") == -1:
                        a["attacker_factionname"] = "Stealth"
                    data = []

                    for k in keys:
                        if k in ["attacker_factionname", "defender_factionname"]:
                            data.append(html.unescape(a.get(k)))
                        else:
                            data.append(a.get(k))
                    csv_data.append(data)

                t = loader.get_template('faction/attacks/csv-attacks.txt')
                c = {'data': csv_data}
                response.write(t.render(c))

                return response

            return returnError(type=403, msg="YOLOOO")

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


# SECTION: revives
def revivesReports(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Check again later."}
                return render(request, page, context)

            # delete contract
            if request.POST.get("type") == "delete":
                contract = faction.revivesreport_set.filter(pk=request.POST["contractId"])
                contract.delete()
                # dummy render
                return render(request, page)

            # create contract
            message = False
            if request.POST.get("type") == "new":
                try:
                    live = int(request.POST.get("live", 0))
                    start = int(request.POST.get("start", 0))
                    end = int(request.POST.get("end", 0))
                    if tsnow() - start > faction.getHist("revives"):
                        message = ["errorMessageSub", "Starting date too far in the past (limit is {}).<br>Starts: {}".format(faction.getHistName("revives"), timestampToDate(start, fmt=True))]
                    elif live and tsnow() - start > faction.getHist("live"):
                        message = ["errorMessageSub", "Starting date too far in the past for a live record (limit is {}).<br>Starts: {}".format(faction.getHistName("live"), timestampToDate(start, fmt=True))]
                    elif start > tsnow() or end > tsnow():
                        message = ["errorMessageSub", "Select a starting date and ending date in the past.<br>Starts: {}<br>Ends: {}".format(timestampToDate(start, fmt=True), timestampToDate(end, fmt=True))]
                    elif start and live:
                        report = faction.revivesreport_set.create(start=start, end=0, live=True, computing=True)
                        c = report.assignCrontab()
                        report.save()
                        message = ["validMessageSub", "New live report created.<br>Starts: {}".format(timestampToDate(start, fmt=True))]
                    elif start and end and start < end:
                        report = faction.revivesreport_set.create(start=start, end=end, live=False, computing=True)
                        c = report.assignCrontab()
                        report.save()
                        message = ["validMessageSub", "New report created.<br>Starts: {}<br>Ends: {}".format(timestampToDate(start, fmt=True), timestampToDate(end, fmt=True))]
                    else:
                        message = ["errorMessageSub", "Error while creating new report"]
                except BaseException as e:
                    message = ["errorMessageSub", "Error while creating new report: {}".format(e)]

            # get reports
            reports = faction.revivesreport_set.order_by('-end')
            for report in reports:
                report.status = REPORT_REVIVES_STATUS[report.state]

            context = {'player': player, 'faction': faction, 'factioncat': True, 'reports': reports, 'view': {'revivesReports': True}}
            if message:
                context[message[0]] = message[1]
            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def manageRevives(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            if not player.factionAA:
                return returnError(type=403, msg="You need AA rights.")

            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Check again later."}
                return render(request, page, context)

            reportId = request.POST.get("reportId", 0)
            report = RevivesReport.objects.filter(pk=reportId).first()
            if report is None:
                return render(request, 'yata/error.html', {'inlineError': 'Report {} not found in the database.'.format(reportId)})

            # toggle share
            if request.POST.get("type", False) == "share":
                if report.shareId == "":
                    report.shareId = randomSlug()
                else:
                    report.shareId = ""
                report.save()
                context = {"report": report}
                return render(request, 'faction/revives/share.html', context)

            # delete contract
            if request.POST.get("type") == "delete":
                report.delete()

            return render(request, page)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def revivesReport(request, reportId, share=False):
    try:
        if request.session.get('player') or share == "share":
            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'

            if share == "share":
                # if shared report
                player = False
                report = RevivesReport.objects.filter(shareId=reportId).first()
                if report is None:
                    return returnError(type=404, msg="Shared report {} not found.".format(reportId))
                faction = report.faction

            else:
                player = getPlayer(request.session["player"].get("tId"))
                factionId = player.factionId

                # get faction
                faction = Faction.objects.filter(tId=factionId).first()
                if faction is None:
                    selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                    context = {'player': player, selectError: "Faction not found. It might come from a API issue. Check again later."}
                    return render(request, page, context)

                # get breakdown
                if not reportId.isdigit():
                    selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                    context = dict({"player": player, selectError: "Wrong report ID: {}.".format(reportId), 'factioncat': True, 'faction': faction, 'report': False})  # views
                    return render(request, page, context)

                report = faction.revivesreport_set.filter(pk=reportId).first()
                if report is None:
                    selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                    context = dict({"player": player,
                                    selectError: "Report {} not found.".format(reportId),
                                    'factioncat': True,
                                    'faction': faction,
                                    'report': False})  # views
                    return render(request, page, context)

            # if modify end date
            # if 'modifyEnd' in request.POST:
            #     tse = int(request.POST.get("end", 0))
            #     if report.start < tse:
            #         report.end = tse
            #         report.live = False
            #         report.computing = True
            #         report.assignCrontab()
            #         report.revive_set.filter(timestamp__gt=tse).delete()
            #         report.last = min(report.end, report.last)
            #         report.state = 0
            #         report.save()

            if 'type' in request.POST:
                if not player.factionAA:
                    return returnError(type=403, msg="You need AA rights.")

                type = request.POST["type"]
                if type in ["online", "hospit"]:
                    online = not report.filter >= 10 if type == "online" else report.filter >= 10
                    hospit = not bool(report.filter % 10) if type == "hospit" else bool(report.filter % 10)

                    filter = 1 if hospit else 0
                    report.filter = filter + 10 if online else filter
                    report.save()

                elif type in ["failed"]:
                    report.include_failed = not report.include_failed
                    report.save()
                    report.fillReport()

                elif type in ["chance"]:
                    chance = str(request.POST.get("value"))
                    if chance.isdigit():
                        report.chance_filter = int(chance)
                        report.save()
                        report.fillReport()

            e = report.getFilterExt()

            o_pl = int(request.GET.get('o_pl', 1)) if int(request.GET.get('o_pl', 1)) else int(request.POST.get('o_pl', 1))
            orders_pl = [False, ["-revivesMade" + e, "-revivesReceived" + e], ["-revivesReceived" + e, "-revivesMade" + e]]
            order_pl = orders_pl[o_pl]

            o_fa = int(request.GET.get('o_fa', 1)) if int(request.GET.get('o_fa', 1)) else int(request.POST.get('o_pl', 1))
            orders_fa = [False, ["-revivesMade" + e, "-revivesReceived" + e], ["-revivesReceived" + e, "-revivesMade" + e]]
            order_fa = orders_fa[o_fa]

            if request.GET.get('p_fa') is not None or request.GET.get('o_fa') is not None:
                if order_fa:
                    paginator = Paginator(report.revivesfaction_set.order_by(order_fa[0], order_fa[1]), 10)
                else:
                    paginator = Paginator(report.revivesfaction_set.order_by("-revivesMade" + e, "-revivesReceived" + e), 10)
                p_fa = request.GET.get('p_fa')
                factions = paginator.get_page(p_fa)
                page = "faction/revives/factions.html"
                context = {"player": player, "faction": faction, "report": report, "factions": factions, "o_fa": o_fa}
                return render(request, page, context)

            if request.GET.get('p_pl') is not None or request.GET.get('o_pl') is not None:
                if order_pl:
                    paginator = Paginator(report.revivesplayer_set.filter(show=True).order_by(order_pl[0], order_pl[1]), 10)
                else:
                    paginator = Paginator(report.revivesplayer_set.filter(show=True).order_by("-revivesMade" + e, "-revivesReceived" + e), 10)
                p_pl = request.GET.get('p_pl')
                players = paginator.get_page(p_pl)
                page = "faction/revives/players.html"
                context = {"player": player, "faction": faction, "report": report, "players": players, "o_pl": o_pl}
                return render(request, page, context)

            factions = json.loads(report.factions)

            # if click on toggle
            p_fa = False
            if request.POST.get("type") == "toggle":
                try:
                    f = int(request.POST["factionId"])
                    if f in factions:
                        factions.remove(int(request.POST["factionId"]))
                        report.revivesfaction_set.filter(faction_id=f).update(show=False)
                        report.revivesplayer_set.filter(player_faction_id=f).update(show=False)
                    else:
                        factions.append(f)
                        report.revivesfaction_set.filter(faction_id=f).update(show=True)
                        report.revivesplayer_set.filter(player_faction_id=f).update(show=True)
                    report.factions = json.dumps(factions)
                    report.save()
                    p_fa = request.POST["page"]
                except BaseException as e:
                    print("Error toggle faction {}".format(e))

            # handle player filter
            report.player_filter = 0
            report.save()

            if report.player_filter:
                revivesFilter = (Q(reviver_id=report.player_filter) | Q(target_id=report.player_filter)) & Q(chance__gte=report.chance_filter)
            else:
                revivesFilter = (Q(reviver_faction__in=factions) | Q(target_faction__in=factions)) & Q(chance__gte=report.chance_filter)

            if not report.include_failed:
                revivesFilter = revivesFilter & Q(result=True)

            # revivesFilter = Q(reviver_faction__in=factions) | Q(target_faction__in=factions)
            revives_set = report.revive_set.filter(revivesFilter).order_by("-timestamp")
            if report.filter >= 10:
                revives_set = revives_set.filter(target_last_action_status="Online")
            if bool(report.filter % 10):
                revives_set = revives_set.filter(target_hospital_reason__startswith="Hospitalized")
            paginator = Paginator(revives_set, 25)
            p_re = request.GET.get('p_re')
            revives = paginator.get_page(p_re)

            revivers = dict({})
            targets = dict({})
            for r in revives_set:
                revivers[r.reviver_id] = r.reviver_name
                targets[r.target_id] = r.target_name
            revivers = sorted(revivers.items(), key=lambda x: x[1])
            targets = sorted(targets.items(), key=lambda x: x[1])

            if order_fa:
                paginator = Paginator(report.revivesfaction_set.order_by(order_fa[0], order_fa[1]), 10)
            else:
                paginator = Paginator(report.revivesfaction_set.order_by("-revivesMade" + e, "-revivesReceived" + e), 10)
            p_fa = request.GET.get('p_fa') if not p_fa else p_fa
            factions = paginator.get_page(p_fa)

            if order_pl:
                paginator = Paginator(report.revivesplayer_set.filter(show=True).order_by(order_pl[0], order_pl[1]), 10)
            else:
                paginator = Paginator(report.revivesplayer_set.filter(show=True).order_by("-revivesMade" + e, "-revivesReceived" + e), 10)
            p_pl = request.GET.get('p_pl')
            players = paginator.get_page(p_pl)

            # context
            report.status = REPORT_REVIVES_STATUS[report.state]

            if share == "share":
                context = dict({"skipheader": True,
                                'share': True,
                                'faction': faction,
                                'factions': factions,
                                'players': players,
                                'report': report,
                                'o_pl': o_pl,
                                'o_fa': o_fa,
                                'revivers': revivers,
                                'targets': targets,
                                'view': {'revivesReport': True}})  # views
            else:
                context = dict({"player": player,
                                'factioncat': True,
                                'faction': faction,
                                'factions': factions,
                                'players': players,
                                'report': report,
                                'revives': revives,
                                'o_pl': o_pl,
                                'o_fa': o_fa,
                                'revivers': revivers,
                                'targets': targets,
                                'view': {'revivesReport': True}})  # views

            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def revivesList(request, reportId):
    print(request.POST)
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            # get faction
            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Check again later."}
                return render(request, 'yata/error.html', context)

            # get breakdown
            report = faction.revivesreport_set.filter(pk=reportId).first()
            if report is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Report {} not found.".format(reportId)}
                return render(request, 'yata/error.html', context)

            if request.POST.get("type", False) and request.POST["type"] == "filter":
                if report.player_filter == int(request.POST["playerId"]):
                    report.player_filter = 0
                else:
                    report.player_filter = int(request.POST["playerId"])
                report.save()

            factions = json.loads(report.factions)

            if report.player_filter:
                revivesFilter = (Q(reviver_id=report.player_filter) | Q(target_id=report.player_filter)) & Q(chance__gte=report.chance_filter)
            else:
                revivesFilter = (Q(reviver_faction__in=factions) | Q(target_faction__in=factions)) & Q(chance__gte=report.chance_filter)

            if not report.include_failed:
                revivesFilter = revivesFilter & Q(result=True)

            revives_set = report.revive_set.filter(revivesFilter).order_by("-timestamp")
            if report.filter >= 10:
                revives_set = revives_set.filter(target_last_action_status="Online")
            if bool(report.filter % 10):
                revives_set = revives_set.filter(target_hospital_reason__startswith="Hospitalized")
            paginator = Paginator(revives_set, 25)
            p_re = request.GET.get('p_re', 1)
            revives = paginator.get_page(p_re)

            revivers = dict({})
            targets = dict({})
            for r in revives_set:
                revivers[r.reviver_id] = r.reviver_name
                targets[r.target_id] = r.target_name
            revivers = sorted(revivers.items(), key=lambda x: x[1])
            targets = sorted(targets.items(), key=lambda x: x[1])

            if p_re is not None:
                return render(request, 'faction/revives/revives.html', {'report': report, 'revives': revives, 'revivers': revivers, 'targets': targets})
            else:
                return returnError(type=403, msg="You need to get a page.")

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


# SECTION: armory
def armory(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            faction = getFaction(player.factionId)

            message = False
            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'

            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found in the database."}
                return render(request, page, context)

            # create new report
            if request.POST.get("type") == "new" and player.factionAA:
                try:
                    live = int(request.POST.get("live", 0))
                    start = int(request.POST.get("start", 0))
                    end = int(request.POST.get("end", 0))
                    if tsnow() - start > faction.getHist("attacks"):
                        message = ["errorMessageSub", "Starting date too far in the past (limit is {}).<br>Starts: {}".format(faction.getHistName("armory"), timestampToDate(start, fmt=True))]
                    elif live and tsnow() - start > faction.getHist("live"):
                        message = ["errorMessageSub", "Starting date too far in the past for a live record (limit is {}).<br>Starts: {}".format(faction.getHistName("live"), timestampToDate(start, fmt=True))]
                    elif start > tsnow():
                        message = ["errorMessageSub", "Select a starting date in the past.<br>Starts: {}".format(timestampToDate(start, fmt=True))]
                    elif start and live:
                        report = faction.armoryreport_set.create(start=start, end=0, live=True, computing=True)
                        c = report.assignCrontab()
                        report.save()
                        message = ["validMessageSub", "New live report created.<br>Starts: {}".format(timestampToDate(start, fmt=True))]
                    elif start and end and start < end:
                        report = faction.armoryreport_set.create(start=start, end=end, live=False, computing=True)
                        c = report.assignCrontab()
                        report.save()
                        message = ["validMessageSub", "New report created.<br>Starts: {}<br>Ends: {}".format(timestampToDate(start, fmt=True), timestampToDate(end, fmt=True))]
                    else:
                        message = ["errorMessageSub", "Error while creating new report"]
                except BaseException as e:
                    message = ["errorMessageSub", "Error while creating new report: {}".format(e)]

            # delete report
            if request.POST.get("type") == "delete" and player.factionAA:
                ArmoryReport.objects.filter(pk=request.POST.get("reportId")).first().delete()
                return render(request, page)

            reports = faction.armoryreport_set.all()

            context = {'player': player, 'reports': reports, 'factioncat': True, 'faction': faction, 'view': {'armory': True}}
            if message:
                context[message[0]] = message[1]
            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def armoryReport(request, reportId, share=False):
    try:
        if request.session.get('player') or share == "share":
            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'

            player = getPlayer(request.session["player"].get("tId"))
            faction = getFaction(player.factionId)

            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found. It might come from a API issue. Check again later."}
                return render(request, page, context)

            # get breakdown
            if not reportId.isdigit():
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = dict({"player": player, selectError: "Wrong report ID: {}.".format(reportId), 'factioncat': True, 'faction': faction, 'report': False})  # views
                return render(request, page, context)

            report = faction.armoryreport_set.filter(pk=reportId).first()
            print(reportId)
            if report is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = dict({"player": player, selectError: "Report {} not found.".format(reportId), 'factioncat': True, 'faction': faction, 'report': False})  # views
                return render(request, page, context)

            # for item_type, items in armory.items():
            #     print(item_type)
            #     for item, members in items.items():
            #         print(f'\t{item}')
            #         for member_id, transaction in members.items():
            #             print(f'\t\t{member_id:>9}: {transaction}')

            context = dict({"player": player, 'faction': faction, 'report': report, 'factioncat': True, 'view': {'armoryReport': True}})  # views
            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


# SECTION: big brother
def bigBrother(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'

            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})

            message = False
            state = False
            if request.POST.get('add', False) and player.factionAA:
                state, message = faction.addContribution(request.POST.get('add'))

            # get all stats
            allContributors = faction.contributors_set.order_by('timestamp')

            # add on the fly 4 gyms
            # loop over unique ts
            gymsKeys = ["gymstrength", "gymspeed", "gymdefense", "gymdexterity"]
            for uniqueTS in set([s.timestamphour for s in allContributors]):
                gyms = []
                for tsCont in allContributors.filter(timestamphour=uniqueTS):
                    if tsCont.stat in gymsKeys:
                        gyms.append(tsCont)

                if len(gyms) == 4:
                    contributors = dict({})
                    for gym in gyms:
                        for k, v in json.loads(gym.contributors).items():
                            if k in contributors:
                                contributors[k][1] += v[1]
                            else:
                                contributors[k] = v
                    newCont = {"timestamp": gyms[0].timestamp, "contributors": json.dumps(contributors)}
                    faction.contributors_set.update_or_create(stat="allgyms", timestamphour=gyms[0].timestamphour, defaults=newCont)
                    allContributors = faction.contributors_set.order_by('timestamp')

            statsList = dict({})
            contributors = False
            statistics = False
            comparison = False
            for stat in allContributors:
                # create entry if first iteration on this type
                if stat.stat not in statsList:
                    statsList[stat.stat] = []

                # enter contributors
                realName = BB_BRIDGE.get(stat.stat, stat.stat)
                statsList[stat.stat].append([realName, stat.timestamp])

            if request.POST.get('name', False):
                name = request.POST.get('name')
                tsA = int(request.POST.get('tsA'))
                tsB = int(request.POST.get('tsB'))
                comparison = [name, tsA, tsB, str(name)]

                # select first timestamp
                stat = allContributors.filter(stat=name, timestamp=tsA).first()
                contributors = dict({})
                # in case they remove stat and select it before refresh
                if stat is not None:
                    comparison[3] = BB_BRIDGE.get(stat.stat, stat.stat)
                    for k, v in json.loads(stat.contributors).items():
                        contributors[BB_BRIDGE.get(k, k)] = [v[0], v[1], 0]

                    # select second timestamp
                    if tsB > 0:
                        stat = allContributors.filter(stat=name, timestamp=tsB).first()
                        for k, v in json.loads(stat.contributors).items():
                            memberName = BB_BRIDGE.get(k, k)
                            # update 3rd column if already in timestamp A
                            if k in contributors:
                                contributors[memberName][2] = v[1]
                            # add if new
                            else:
                                contributors[memberName] = [v[0], 0, v[1]]
                            c = contributors[memberName]
                            if not c[2] - c[1]:
                                del contributors[memberName]

                        # delete contributors out of faction for ts2
                        todel = [k for k, v in contributors.items() if (not v[2] or not v[1])]
                        for tId in todel:
                            del contributors[tId]

                        contributors = sorted(contributors.items(), key=lambda x: x[1][1] - x[1][2])

                    else:
                        contributors = sorted(contributors.items(), key=lambda x: -x[1][1])

                # [time 1, time 2, diff]
                total = [0, 0, 0]
                mean = [0.0, 0.0, 0.0]
                mean2 = [0.0, 0.0, 0.0]
                std = [0.0, 0.0, 0.0]
                n = len(contributors)
                for k, v in contributors:
                    tmp = [v[1], v[2], v[2] - v[1]]
                    for i in range(3):
                        total[i] += tmp[i]
                        mean[i] += tmp[i] / float(n)
                        mean2[i] += tmp[i]**2 / float(n)

                # [[total, mean, std, cov], []]
                statistics = []
                for i in range(3):
                    std[i] = (mean2[i] - mean[i]**2)**0.5
                    cov = std[i] / mean[i] if mean[i] else 0
                    statistics.append([total[i], mean[i], std[i], cov])

            if contributors:
                faction_members = [str(m.tId) for m in faction.member_set.only("tId").all()]
                for k in contributors:
                    in_fac = True if k[0] in faction_members else False
                    k[1].append(in_fac)

            context = {'player': player, 'factioncat': True, 'faction': faction, 'statsList': statsList, 'contributors': contributors, 'comparison': comparison, 'bridge': BB_BRIDGE, 'statistics': statistics, 'view': {'bb': True}}

            if message:
                err = "validMessage" if state else "errorMessage"
                sub = "Sub" if request.method == 'POST' else ""
                context[err + sub] = message

            if request.method == 'POST':
                page = 'faction/content-reload.html' if request.POST.get('name') is None else 'faction/bigbrother/table.html'
            else:
                page = 'faction.html'
            return render(request, page, context)

        else:
            message = "You might want to log in."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def removeContributors(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            if not player.factionAA:
                return returnError(type=403, msg="You need AA rights.")

            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})

            s = faction.contributors_set.filter(stat=request.POST.get('name')).filter(timestamp=request.POST.get('ts')).first()
            try:
                s.delete()
                m = "Okay"
                t = 1
            except BaseException as e:
                m = str(e)
                t = -1

            return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


# SECTION: territories
def territories(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'

            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})

            # get faction territories
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

            allTerritories = Territory.objects.all()

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

                if racket.war:
                    tmp = Faction.objects.filter(tId=racket.assaulting_faction).first()
                    if tmp is not None:
                        racket.assaulting_faction_name = tmp.name
                    else:
                        racket.assaulting_faction_name = "Faction"

            territoryUpda = FactionData.objects.first().territoryUpda
            context = {'player': player, 'factioncat': True, 'faction': faction, 'rackets': rackets, 'territoryUpda': territoryUpda, 'territories': territories, 'summary': summary, 'view': {'territories': True}}
            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'
            return render(request, page, context)

        else:
            message = "You might want to log in."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def territoriesFullMap(request):
    try:
        if request.method == 'POST':
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})

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
            return render(request, 'faction/territories/fullmap.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


# SECTION: respect simulator
def simulator(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            if not player.factionAA:
                return returnError(type=403, msg="You need AA rights.")

            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})

            # update if needed
            if tsnow() - faction.upgradesUpda > 3600 * 24:
                state, message = faction.updateUpgrades()
            else:
                state = False
                message = False

            # if modifications
            optimize = False
            forceOrder = False
            if request.POST.get("change"):
                optimize = True
                # change level
                if request.POST.get("modification") == "level":
                    shortname = request.POST.get("shortname")
                    level = int(request.POST.get("value"))

                    # get FactionTree
                    if level:
                        u = FactionTree.objects.filter(shortname=shortname, level=level).first()
                        v = {"active": True, "level": level, "branch": u.branch, "tId": u.tId}
                        faction.upgrade_set.update_or_create(simu=True, shortname=shortname, defaults=v)
                        faction.setSimuDependencies(u)
                    else:
                        u = FactionTree.objects.filter(shortname=shortname, level=1).first()
                        v = {"active": False, "level": 1, "branch": u.branch, "tId": u.tId}
                        faction.upgrade_set.update_or_create(simu=True, shortname=shortname, defaults=v)
                        faction.setSimuDependencies(u, unset=True)

                # change order
                if request.POST.get("modification") == "branchorder":
                    branch = request.POST.get("shortname")
                    order = int(request.POST.get("value"))
                    if order:
                        forceOrder = [branch, order]
                    else:
                        faction.upgrade_set.filter(simu=True, branch=branch).update(branchorder=0, level=1, active=False)

                # update simulator TS
                faction.simulationTS = tsnow()
                faction.simulationID = player.tId
                faction.save()

            elif request.POST.get("reset"):
                faction.resetSimuUpgrades(update=False)

            elif request.POST.get("refresh"):
                faction.updateUpgrades()

            tree, respect = faction.getFactionTree(optimize=optimize, forceOrder=forceOrder)

            deltaSimu = tsnow() - faction.simulationTS
            if deltaSimu < 5 * 60 and player.tId != faction.simulationID:
                currentSimu = {"player": getPlayer(faction.simulationID, skipUpdate=True), "delta": deltaSimu}
            else:
                currentSimu = False

            context = {'player': player, 'factioncat': True, 'faction': faction, 'respect': respect, 'tree': tree, 'currentSimu': currentSimu, 'view': {'simulator': True}}
            if message:
                err = "validMessage" if state else "errorMessage"
                sub = "Sub" if request.method == 'POST' else ""
                context[err + sub] = message

            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'
            if request.method == 'POST':
                page = 'faction/simulator/table.html' if (request.POST.get("reset") or request.POST.get("change") or request.POST.get("refresh")) else 'faction/content-reload.html'
            else:
                page = 'faction.html'
            return render(request, page, context)

        else:
            message = "You might want to log in."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def simulatorChallenge(request):
    try:
        if request.session.get('player') and request.method == "POST":
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            if not player.factionAA:
                return returnError(type=403, msg="You need AA rights.")

            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})

            challenges = FactionTree.objects.filter(shortname=request.POST.get("upgradeId")).order_by("level")
            for ch in challenges:
                ch.progress = ch.progress(faction)

            context = {"challenges": challenges}
            page = 'faction/simulator/challenge.html'
            return render(request, page, context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


# SECTION: organised crimes
def oc(request):
    from datetime import datetime
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            faction = getFaction(player.factionId)

            if not player.factionAA:
                return returnError(type=403, msg="You need AA rights.")

            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': f'Faction {player.factionId} not found in the database.'})

            crimes, error, message = faction.updateCrimes()

            filters = {k: request.GET.get(k) for k in ["team_id", "crime_id", "planned_by", "initiated_by"] if request.GET.get(k, False)}
            crimes = crimes.filter(**filters)
            getfilters = "".join(["&{}={}".format(k, v) for k, v in filters.items()])

            currentCrimes = crimes.filter(initiated=False).order_by("time_ready")
            pastCrimes = crimes.filter(initiated=True).order_by("-time_completed")

            # compute breakdown totals
            crimesDB = dict({})
            teamsDB = dict({})
            for crime in pastCrimes:
                if crime.crime_id not in crimesDB:

                    crimesDB[crime.crime_id] = {"name": crime.crime_name, "crimes": [0, 0, 0], "time": [0, 0], "money": [0, 0, 0, 0, 0, 0], "respect": [0, 0, 0, 0, 0, 0]}

                if crime.team_id not in teamsDB:
                    teamsDB[crime.team_id] = {"participants": crime.get_participants(), "crimes": [0, 0, 0], "time": [0, 0], "money": [0, 0, 0], "respect": [0, 0, 0], "active": False}

                crimesDB[crime.crime_id]["crimes"][0] += 1
                crimesDB[crime.crime_id]["crimes"][1] += 1 if crime.success else 0
                crimesDB[crime.crime_id]["money"][0] += crime.money_gain
                crimesDB[crime.crime_id]["respect"][0] += crime.respect_gain
                crimesDB[crime.crime_id]["time"][0] += len(json.loads(crime.participants)) * (crime.time_completed - crime.time_started)

                teamsDB[crime.team_id]["crimes"][0] += 1
                teamsDB[crime.team_id]["crimes"][1] += 1 if crime.success else 0
                teamsDB[crime.team_id]["money"][0] += crime.money_gain
                teamsDB[crime.team_id]["respect"][0] += crime.respect_gain
                teamsDB[crime.team_id]["time"][0] += len(json.loads(crime.participants)) * (crime.time_completed - crime.time_started)

            # compute crimesDB averages
            for k, v in crimesDB.items():
                v["crimes"][2] = round(100 * (v["crimes"][1] / v["crimes"][0]))
                v["time"][1] = round(v["time"][0] / float(v["crimes"][0]))
                v["money"][1] = round(v["money"][0] / float(v["crimes"][0]))
                v["money"][2] = round(v["money"][0] / float(v["time"][1]) * 24 * 3600)
                v["respect"][1] = v["respect"][0] / float(v["crimes"][0])
                v["respect"][2] = v["respect"][0] / float(v["time"][1]) * 24 * 3600
                v["money"][3] = round(v["money"][2] / float(v["crimes"][0]))
                v["money"][4] = OC_EFFICIENCY[k]["money"]
                v["money"][5] = round(100 * v["money"][3] / float(OC_EFFICIENCY[k]["money"]))
                v["respect"][3] = round(v["respect"][2] / float(v["crimes"][0]), 2)
                v["respect"][4] = OC_EFFICIENCY[k]["respect"]
                v["respect"][5] = round(100 * v["respect"][3] / float(OC_EFFICIENCY[k]["respect"]))

            # compute current crimes progress
            now = tsnow()
            for crime in currentCrimes:
                crime.progress = math.floor(100 * min((now - crime.time_started) / (crime.time_ready - crime.time_started), 1))

            # compute teamsDB averages
            todel = []
            for k, v in teamsDB.items():
                v["crimes"][2] = round(100 * (v["crimes"][1] / v["crimes"][0]))
                v["time"][1] = round(v["time"][0] / float(v["crimes"][0]))
                v["money"][1] = round(v["money"][0] / float(v["crimes"][0]))
                v["money"][2] = round(v["money"][0] / float(v["time"][1]) * 24 * 3600)
                v["respect"][1] = v["respect"][0] / float(v["crimes"][0])
                v["respect"][2] = v["respect"][0] / float(v["time"][1]) * 24 * 3600
                if v["crimes"][0] == 1:
                    todel.append(k)
                elif len(currentCrimes.filter(team_id=k)):
                    v["active"] = True

            for k in todel:
                del teamsDB[k]

            # order crimesDB
            crimesDB = sorted(crimesDB.items(), key=lambda x: x[0])
            teamsDB = sorted(teamsDB.items(), key=lambda x: -x[1]["time"][0])

            # pagination
            currentCrimes = Paginator(currentCrimes, 25).get_page(request.GET.get("p_ccrimes"))
            pastCrimes = Paginator(pastCrimes, 25).get_page(request.GET.get("p_pcrimes"))

            context = {'player': player, 'factioncat': True, 'faction': faction, 'crimesDB': crimesDB, 'teamsDB': teamsDB, 'currentCrimes': currentCrimes, 'pastCrimes': pastCrimes, 'tsnow': tsnow(), "filters": filters, 'getfilters': getfilters, 'view': {'oc': True}}
            if message:
                sub = "Sub" if request.method == 'POST' else ""
                if error:
                    context["errorMessage" + sub] = f"Crimes: API error {message}, crimes list not updated"
                else:
                    context["validMessage" + sub] = "Crimes list has been updated. {created} created, {updated} updated, {deleted} deleted, {ready} ready.".format(**message)

            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'
            return render(request, page, context)

        else:
            message = "You might want to log in."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def ocList(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            factionId = player.factionId

            if not player.factionAA:
                return returnError(type=403, msg="You need AA rights.")

            faction = Faction.objects.filter(tId=factionId).first()
            if faction is None:
                return render(request, 'yata/error.html', {'errorMessage': 'Faction {} not found in the database.'.format(factionId)})

            filters = {k: request.GET.get(k) for k in ["team_id", "crime_id", "planned_by", "initiated_by"] if request.GET.get(k, False)}
            getfilters = "".join(["&{}={}".format(k, v) for k, v in filters.items()])
            crimes = faction.crimes_set.filter(**filters)

            if request.GET.get("p_ccrimes", False):
                # current crimes
                crimes = crimes.filter(initiated=False).order_by("time_ready")
                crimes = Paginator(crimes, 25).get_page(request.GET.get("p_ccrimes"))
                context = {'currentCrimes': crimes, "filters": filters, 'getfilters': getfilters, 'reloadTooltips': True}
                page = "faction/oc/list-current.html"
            else:
                crimes = crimes.filter(initiated=True).order_by("-time_completed")
                crimes = Paginator(crimes, 25).get_page(request.GET.get("p_pcrimes"))
                context = {'pastCrimes': crimes, "filters": filters, 'getfilters': getfilters, 'reloadTooltips': True}
                page = "faction/oc/list-past.html"
            return render(request, page, context)

        else:
            message = "You might want to log in."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


# SECTION: spies
def spies(request, secret=False, export=False):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            faction = getFaction(player.factionId)

            if not player.factionAA:
                return returnError(type=403, msg="You need AA rights.")

            message = False
            page = 'faction/content-reload.html' if request.method == 'POST' else 'faction.html'

            if faction is None:
                selectError = 'errorMessageSub' if request.method == 'POST' else 'errorMessage'
                context = {'player': player, selectError: "Faction not found in the database."}
                return render(request, page, context)

            # export
            if secret and export:  # export database
                if export == 'csv':
                    db = SpyDatabase.objects.filter(secret=secret).first()
                    print(secret)
                    print(db)

                    class Echo:
                        def write(self, value):
                            return value

                    # headers
                    spies_keys = [ "target_name", "target_faction_name", "target_faction_id", "strength", "speed", "defense", "dexterity", "total", "strength_timestamp", "speed_timestamp", "defense_timestamp", "dexterity_timestamp", "total_timestamp" ]
                    row = ["target_id"]
                    for k in spies_keys:
                        row.append(k)
                    rows = [row]

                    # rows
                    for target_id, spy in db.get_spies().items():
                        row = [str(target_id)]
                        for k in spies_keys:
                            row.append(str(spy[k]))
                        rows.append(row)

                    pseudo_buffer = Echo()
                    writer = csv.writer(pseudo_buffer)
                    response = StreamingHttpResponse((writer.writerow(row) for row in rows), content_type="text/csv")
                    response['Content-Disposition'] = f'attachment; filename=yata_spies_{db.name.replace(" ", "-")}.csv'
                    return response

                else:
                    db = SpyDatabase.objects.filter(secret=secret).first()
                    if db is not None and faction.tId == db.master_id:
                        payload = {"spies": db.get_spies()}
                        response = JsonResponse(payload)
                        response['Content-Disposition'] = f'attachment; filename=yata_spies_{db.name.replace(" ", "-")}.json'
                        return response

            db = False
            if request.POST.get("action") == "create-database":  # create database
                db = SpyDatabase.objects.create()
                db.change_name()
                db.change_secret()
                db.master_id = faction.tId
                db.save()
                db.factions.add(faction)
                db.updateSpies()

            elif request.POST.get("action") == "view-database":  # view database
                db = SpyDatabase.objects.filter(pk=request.POST.get("pk")).first()

            elif request.POST.get("action") == "update-database":  # update database
                db = SpyDatabase.objects.filter(pk=request.POST.get("pk")).first()
                if db is not None and faction.tId == db.master_id:
                    db.updateSpies()

            elif request.POST.get("action") == "kick-faction":  # change database secret
                db = SpyDatabase.objects.filter(pk=request.POST.get("pk")).first()
                if db is not None and faction.tId == db.master_id:
                    fa = db.factions.filter(tId=request.POST.get("faction_id")).first()
                    if fa is not None:
                        db.factions.remove(fa)
                return render(request, page)

            elif request.POST.get("action") == "change-secret":  # kick from database
                db = SpyDatabase.objects.filter(pk=request.POST.get("pk")).first()
                if db is not None:
                    db.change_secret()
                db.save()
                context = {'player': player, 'faction': faction, 'database': db}
                return render(request, 'faction/spies/db-line.html', context)

            elif request.POST.get("action") == "refresh-target-data":  # refresh target data
                db = SpyDatabase.objects.filter(pk=request.POST.get("pk")).first()
                spy = db.spy_set.filter(target_id=request.POST.get("target_id")).first()
                try:
                    req = apiCall("user", request.POST.get("target_id"), "profile", player.getKey(), verbose=False)
                    if "apiError" in req:
                        return render(request, 'faction/spies/table-line.html', {"error_inline": f'API error: {req["apiError"]}'})

                    # update db
                    spy.target_name = req["name"]
                    spy.target_faction_id = req["faction"]["faction_id"]
                    spy.target_faction_name = req["faction"]["faction_name"]
                    spy.save()

                    # refresh cache
                    all_spies = cache.get(f"spy-db-{db.secret}")
                    all_spies[spy.target_id]["target_name"] = spy.target_name
                    all_spies[spy.target_id]["target_faction_id"] = spy.target_faction_id
                    all_spies[spy.target_id]["target_faction_name"] = spy.target_faction_name
                    cache.set(f"spy-db-{db.secret}", all_spies, 3600)

                except BaseException as e:
                    return render(request, 'faction/spies/table-line.html', {"error_inline": f'Server Error: {e}'})

                context = {"target_id": request.POST.get("target_id"), "spy": spy}
                return render(request, 'faction/spies/table-line.html', context)

            elif request.POST.get("action") == "change-name":  # change database name
                db = SpyDatabase.objects.filter(pk=request.POST.get("pk")).first()
                if db is not None:
                    db.change_name()
                db.save()
                context = {'player': player, 'faction': faction, 'database': db}
                return render(request, 'faction/spies/db-line.html', context)

            elif request.POST.get("action") == "join-database":  # joining database
                db = SpyDatabase.objects.filter(secret=request.POST.get("secret")).first()
                if db is None:
                    message = ["errorMessageSub", f'Secret <tt>{request.POST.get("secret")}</tt> not found in the database']
                else:
                    db.factions.add(faction)
                    db.updateSpies()
                    message = ["validMessageSub", f"You joined the database {db.name}, congratz."]

            elif request.POST.get("action") == "delete-database":  # delete database
                db = SpyDatabase.objects.filter(pk=request.POST.get("pk")).first()
                if db is not None and db.master_id == faction.tId:
                    db.delete()
                return render(request, page)

            elif request.POST.get("action") == "leave-database":  # leave database
                db = SpyDatabase.objects.filter(pk=request.POST.get("pk")).first()
                if db is not None and db.master_id != faction.tId:
                    db.factions.remove(faction)
                return render(request, page)

            # get databases
            databases = faction.spydatabase_set.all()

            context = {'player': player, 'databases': databases, 'factioncat': True, 'faction': faction, 'view': {'spies': True}}
            if message:
                context[message[0]] = message[1]

            if db:
                context['database'] = db

            if 'message' in request.session:
                context[request.session['message'][0]] = request.session['message'][1]
                del request.session['message']
            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def spiesImport(request):
    try:
        if request.session.get('player') and request.method == "POST":
            player = getPlayer(request.session["player"].get("tId"))
            faction = getFaction(player.factionId)

            if not player.factionAA:
                request.session['message'] = ('errorMessageSub', f'You need AA perm.')
                return redirect('faction:spies')

            if faction is None:
                request.session['message'] = ('errorMessageSub', f'Faction not found in the database.')
                return redirect('faction:spies')

            # get database
            db = SpyDatabase.objects.filter(pk=request.POST.get("db-pk")).first()
            if db is None:
                request.session['message'] = ('errorMessageSub', f'Spy database id {request.POST.get("db-pk")} not found.')
                return redirect('faction:spies')

            # get file
            if not len(request.FILES) or "file" not in request.FILES:
                request.session['message'] = ('errorMessageSub', f'No files found.')
                return redirect('faction:spies')

            file = request.FILES["file"]

            # get meme type
            content_type = magic.from_buffer(file.read(2048), mime=True)
            valid_content_type = ['text/csv', 'application/csv', 'application/json']
            if content_type not in valid_content_type:
                request.session['message'] = ('errorMessageSub', f'Unvalid content type {content_type}. Valid content type are: {", ".join(valid_content_type)}.')
                return redirect('faction:spies')

            if file.size > 5000000:
                request.session['message'] = ('errorMessageSub', f'File size too large ({file.size:,d} B). Should be lower than 5 MiB.')
                return redirect('faction:spies')

            new_spies = {}
            if content_type in ['text/csv', 'application/csv']:
                try:

                    header = True
                    for row in file:
                        # skip header
                        if header:
                            header = False
                            continue


                        splt1 = [_.strip('"') for _ in row.rstrip().decode().split("\",\"")]  # try torn stats style
                        splt2 = row.decode().split(",")  # try yata style
                        if len(splt1) == 11:
                            target_id = int(splt1[1].split("[")[1].replace("]", ""))
                            ts = int(time.mktime(datetime.datetime.strptime(splt1[10], "%d/%m/%y").timetuple()))
                            new_spies[target_id] = {}
                            for j, k in enumerate(["strength", "defense", "speed", "dexterity", "total"]):
                                stat = int(splt1[4 + j].replace(",", ""))
                                stat = stat if stat else -1
                                timestamp = ts if stat + 1 else 0
                                new_spies[target_id][k] = stat
                                new_spies[target_id][f'{k}_timestamp'] = timestamp

                            new_spies[target_id]["target_faction_name"] = splt1[3].replace("None", "Faction") if splt1[3] else "Faction"
                            new_spies[target_id]["target_faction_id"] = 0
                            new_spies[target_id]["target_name"] = splt1[1].split()[0]


                        elif len(splt2) == 14:
                            new_spies[int(splt2[0])] = {
                                "target_id": int(splt2[0]),
                                "target_name": splt2[1],
                                "target_faction_name": splt2[2],
                                "target_faction_id": int(splt2[3]),
                                "strength": int(splt2[4]),
                                "speed": int(splt2[5]),
                                "defense": int(splt2[6]),
                                "dexterity": int(splt2[7]),
                                "total": int(splt2[8]),
                                "strength_timestamp": int(splt2[9]),
                                "speed_timestamp": int(splt2[10]),
                                "defense_timestamp": int(splt2[11]),
                                "dexterity_timestamp": int(splt2[12]),
                                "total_timestamp": int(splt2[13]),
                            }
                        else:
                            print(f"spies csv reader invalide columns {len(splt1)} {len(splt2)}")
                            continue


                except BaseException as e:
                    request.session['message'] = ('errorMessageSub', f'Error while importing csv file: {e}. Make sure it follows Torn Stats ')
                    return redirect('faction:spies')

            db.updateSpies(payload=new_spies)

            request.session['message'] = ('validMessageSub', f'{len(new_spies)} spies imported')
            return redirect('faction:spies')

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)

def fightclub(request):
    try:
        if request.session.get('player'):
            player = getFool(request.session["player"].get("tId"))

            if not player.fight_club_gym_access:
                return returnError(type=403, msg="You don't have access to this section.")

            return render(request, "yata/fightclub.html")

        else:
            message = "You might want to log in."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)
