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
# from django.core.exceptions import PermissionDenied
# from django.utils import timezone
from django.shortcuts import redirect
from django.http import HttpResponse
from django.core.paginator import Paginator

import json
import math

from yata.handy import *

from player.models import Player
from faction.functions import BONUS_HITS
from target.functions import *


def index(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))

            targets = getTargets(player)

            # get faction
            faction = Faction.objects.filter(tId=player.factionId).first()
            factionTargets = [] if faction is None else faction.getTargetsId()

            player.targetInfo = len(targets)
            player.save()
            context = {"player": player, "targetcat": True, "factionTargets": factionTargets, "targets": targets, "ts": tsnow(), "view": {"targets": True}}
            return render(request, 'target.html', context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


def attacks(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))

            error, attacks = updateAttacks(player)
            targets = getTargets(player)

            paginator = Paginator(attacks, 25)
            attacks = paginator.get_page(request.GET.get('p_at'))

            context = {"player": player, "targetcat": True, "attacks": attacks, "targets": targets, "view": {"attacks": True}}
            context["apiErrorSub"] = error["apiError"] if error else False

            page = 'target/content-reload.html'if request.method == "POST" else 'target.html'
            if request.GET.get('p_at', False):
                page = 'target/attacks/attacks.html'

            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()

def losses(request):
    try:
        if request.session.get('player') and request.method == "POST":
            player = getPlayer(request.session["player"].get("tId"))

            losses = player.attack_set.filter(result="Lost").exclude(attacker_id=player.tId)

            if request.POST.get("payall") is not None:
                losses.filter(attacker_id=request.POST.get("payall")).update(paid=True)

            sluts = {i: [] for i in set(losses.values_list('attacker_id', flat=True))}
            for i in sluts:
                a = losses.filter(attacker_id=i)
                if len(a):
                    # name, paid, total
                    sluts[i] = [a.first().attacker_name, len(a.filter(paid=True)), len(a.all())]

            context = {"player": player, "sluts": sluts}
            return render(request, 'target/attacks/losses.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


def attack(request):
    try:
        if request.session.get('player') and request.method == "POST":
            player = getPlayer(request.session["player"].get("tId"))

            if request.POST["type"] == "paid":
                # paid attack
                attack = player.attack_set.filter(tId=request.POST.get("attackId", 0)).first()
                if attack is not None:
                    attack.paid = not attack.paid
                    attack.save()

                context = {"v": attack, "targets": getTargets(player), "ts": tsnow()}
                return render(request, 'target/attacks/buttons.html', context)

            elif request.POST["type"] == "toggle":
                # toggle target
                target_id = int(request.POST["targetId"])
                attack_id = int(request.POST["attackId"])
                targetInfo, state = player.targetinfo_set.get_or_create(target_id=target_id)
                if state:
                    # create/update target
                    _, targetId, target = targetInfo.getTarget(update=True)

                else:
                    # delete target
                    targetInfo.delete()

                attack = player.attack_set.filter(tId=attack_id).first

            else:
                returnError(type=403, msg="Unkown request")

            context = {"v": attack, "targets": getTargets(player), "ts": tsnow()}
            return render(request, 'target/attacks/buttons.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()

def targets(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))

            targets = getTargets(player)

            # get faction
            faction = Faction.objects.filter(tId=player.factionId).first()
            factionTargets = [] if faction is None else faction.getTargetsId()

            context = {"player": player, "targetcat": True, "targets": targets, "factionTargets": factionTargets, "ts": tsnow(), "view": {"targets": True}}
            page = 'target/content-reload.html' if request.method == "POST" else 'target.html'
            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


def targetsList(request):
    try:
        if request.session.get('player') and request.method == "POST":
            player = getPlayer(request.session["player"].get("tId"))

            if request.POST["action_type"] == 'export':
                targets = getTargets(player)
                response = HttpResponse(json.dumps(targets, separators=(',', ':')), content_type='text/json')
                response['Content-Disposition'] = 'attachment; filename="target_list.json"'
                return response

            elif request.POST["action_type"] == 'delete':
                player.targetinfo_set.all().delete()

            elif request.POST["action_type"] == 'import' and len(request.FILES):
                file = request.FILES["json_file"]

                if file.content_type == 'application/json':
                    targets = json.loads(file.read())
                    try:
                        for k, v in targets.items():
                            defaults = {
                                "update_timestamp": int(v["update_timestamp"]),
                                "last_attack_timestamp": int(v["last_attack_timestamp"]),
                                "fairFight": float(v["fairFight"]),
                                "baseRespect": float(v["baseRespect"]),
                                "flatRespect": float(v["flatRespect"]),
                                "result": str(v["result"])[:16],
                                "note": str(v["note"])[:128]}

                            player.targetinfo_set.get_or_create(target_id=k, defaults=defaults)
                    except BaseException as e:
                        message = "Error in the json file: {}".format(e)
                        return returnError(type=403, msg=message)

                else:
                    targets = getTargets(player)
                    message = "Wrong file format. Require: application/json. Give: {}".format(file.content_type)
                    return returnError(type=403, msg=message)

            return redirect('/target/')

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


def target(request):
    try:
        if request.session.get('player') and request.method == "POST":
            player = getPlayer(request.session["player"].get("tId"))

            if request.POST.get("type", False):

                # update target
                if request.POST["type"] == "update":
                    target_id = int(request.POST["targetId"])
                    targetInfo, _ = player.targetinfo_set.get_or_create(target_id=target_id)
                    error, targetId, target = targetInfo.getTarget(update=True)

                    if error:
                        context = {"apiErrorLine": "Error while updating {}: {}".format(target, error.get("apiError", "Unknown error"))}
                    else:
                        faction = Faction.objects.filter(tId=player.factionId).first()
                        factionTargets = [] if faction is None else faction.getTargetsId()
                        context = {"player": player, "factionTargets": factionTargets, "target": target, "targetId": target_id, "ts": tsnow()}

                    return render(request, 'target/targets/line.html', context)

                if request.POST["type"] == "note":
                    target_id = int(request.POST["targetId"])
                    targetInfo, _ = player.targetinfo_set.get_or_create(target_id=target_id)
                    targetInfo.note = str(request.POST["note"])[:128]
                    targetInfo.save()

                    context = {"target": {"note": targetInfo.note}, "targetId": target_id}

                    return render(request, 'target/targets/note.html', context)

                # add by Id target
                if request.POST["type"] == "addById":
                    target_id = int(request.POST["targetId"])
                    targetInfo, _ = player.targetinfo_set.get_or_create(target_id=target_id)
                    targetInfo.getTarget(update=True)
                    faction = Faction.objects.filter(tId=player.factionId).first()
                    factionTargets = [] if faction is None else faction.getTargetsId()

                    targets = getTargets(player)
                    context = {"player": player, "targets": targets, "factionTargets": factionTargets, "targetId": target_id, "ts": tsnow()}

                    return render(request, 'target/targets/index.html', context)

                # delete target
                if request.POST["type"] == "delete":
                    target_id = int(request.POST["targetId"])
                    targetInfo, _ = player.targetinfo_set.get(target_id=target_id).delete()

                    return render(request, 'target/targets/line.html')

            else:
                # should not happen
                context = {"target": None, "targetId": None, "ts": tsnow()}
                return render(request, 'target/targets/line.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except BaseException as e:
        context = {"apiErrorLine": "Error while updating target: {}".format(e)}
        return render(request, 'target/targets/line.html', context)


def revives(request):
    try:
        if request.session.get('player'):
            print('[view.traget.attacks] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = tsnow()
            player.save()

            error = updateRevives(player)

            revives = player.revive_set.all()

            context = {"player": player, "targetcat": True, "revives": revives, "view": {"revives": True}}
            if error:
                context.update(error)

            page = 'target/content-reload.html' if request.method == "POST" else 'target.html'
            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


def revive(request):
    try:
        if request.session.get('player') and request.method == "POST":
            player = getPlayer(request.session["player"].get("tId"))

            r = player.revive_set.filter(tId=request.POST.get("reviveId", 0)).first()
            if r is not None:
                r.paid = not r.paid
                r.save()

            return render(request, 'target/revives/buttons.html', {"revive": r})

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()
