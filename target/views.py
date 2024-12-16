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

import json
import time

from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse

# from django.core.exceptions import PermissionDenied
# from django.utils import timezone
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from faction.models import Faction, FactionTarget
from player.models import Key, Player
from target.functions import getTargets, updateAttacks, updateRevives
from yata.handy import getFaction, getPlayer, returnError

# from django.core.cache import cache


def index(request):
    try:
        if request.session.get("player"):
            # if cache.get('disable-status', False):
            #     return returnError(
            #         type=503,
            #         msg="The server is currently overloaded. This section has been automatically disabled in order to insure a normal functionning of the other features of the website.")

            player = getPlayer(request.session["player"].get("tId"))

            targets = getTargets(player)

            # get faction
            faction = Faction.objects.filter(tId=player.factionId).first()
            factionTargets = [] if faction is None else faction.getTargetsId()

            player.targetInfo = len(targets)
            player.save()
            context = {
                "player": player,
                "targetcat": True,
                "factionTargets": factionTargets,
                "targets": targets,
                "ts": int(time.time()),
                "view": {"targets": True},
            }
            return render(request, "target.html", context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def attacks(request):
    try:
        if request.session.get("player"):
            player = getPlayer(request.session["player"].get("tId"))

            full = request.GET.get("full", False)
            error, attacks = updateAttacks(player, full=full)
            targets = getTargets(player)

            # get breakdown
            breakdownType = dict({})
            breakdownPlayer = dict({})
            for attack in attacks.all():
                i = 0 if attack.attacker else 1

                target_id = attack.defender_id if attack.attacker else attack.attacker_id
                target_name = attack.defender_name if attack.attacker else attack.attacker_name

                if attack.result not in breakdownType:
                    breakdownType[attack.result] = [0, 0]
                if target_id not in breakdownPlayer:
                    breakdownPlayer[target_id] = [0, 0, target_name]

                breakdownType[attack.result][i] += 1
                breakdownPlayer[target_id][i] += 1

            breakdownType = sorted(breakdownType.items(), key=lambda x: x[0])
            breakdownPlayer = sorted(breakdownPlayer.items(), key=lambda x: x[0])

            # sluts
            losses = player.attack_set.filter(result="Lost").exclude(attacker_id=player.tId)

            sluts = {i: [] for i in set(losses.values_list("attacker_id", flat=True))}
            for i in sluts:
                a = losses.order_by("timestamp_ended").filter(attacker_id=i)
                if len(a):
                    # name, paid, total
                    sluts[i] = [
                        a.first().attacker_name,
                        len(a.filter(paid=True)),
                        len(a.all()),
                        a.first().timestamp_ended,
                        a.first().code,
                    ]

            # sort sluts
            sluts = sorted(sluts.items(), key=lambda x: (x[1][1] - x[1][2], -x[1][3]))

            # paginator
            paginator = Paginator(attacks, 25)
            attacks = paginator.get_page(request.GET.get("p_at"))

            context = {
                "player": player,
                "targetcat": True,
                "attacks": attacks,
                "sluts": sluts,
                "breakdownType": breakdownType,
                "breakdownPlayer": breakdownPlayer,
                "targets": targets,
                "view": {"attacks": True},
            }
            context["apiErrorSub"] = error["apiError"] if error else False

            page = "target/content-reload.html" if request.method == "POST" else "target.html"
            if request.GET.get("p_at", False):
                page = "target/attacks/attacks.html"

            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def losses(request):
    try:
        if request.session.get("player") and request.method == "POST":
            player = getPlayer(request.session["player"].get("tId"))

            losses = player.attack_set.filter(result="Lost").exclude(attacker_id=player.tId)

            if request.POST.get("payall") is not None:
                attacker_id = request.POST.get("payall", "None")
                if attacker_id.isdigit():
                    print("update ", attacker_id)
                    losses.filter(attacker_id=attacker_id).update(paid=True)
                elif attacker_id == "all":
                    print("update all")
                    losses.update(paid=True)

            sluts = {i: [] for i in set(losses.values_list("attacker_id", flat=True))}
            for i in sluts:
                a = losses.order_by("timestamp_ended").filter(attacker_id=i)
                if len(a):
                    # name, paid, total
                    sluts[i] = [
                        a.first().attacker_name,
                        len(a.filter(paid=True)),
                        len(a.all()),
                        a.first().timestamp_ended,
                        a.first().code,
                    ]

            # sort sluts
            sluts = sorted(sluts.items(), key=lambda x: (x[1][1] - x[1][2], -x[1][3]))

            context = {"player": player, "sluts": sluts}
            return render(request, "target/attacks/losses.html", context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don't try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def attack(request):
    try:
        if request.session.get("player") and request.method == "POST":
            player = getPlayer(request.session["player"].get("tId"))

            if request.POST["type"] == "paid":
                # paid attack
                attack = player.attack_set.filter(tId=request.POST.get("attackId", 0)).first()
                if attack is not None:
                    attack.paid = not attack.paid
                    attack.save()

                context = {"v": attack, "targets": getTargets(player), "ts": int(time.time())}
                return render(request, "target/attacks/button-paid.html", context)

            elif request.POST["type"] == "toggle":
                # toggle target
                target_id = int(request.POST["targetId"])
                attack_id = int(request.POST["attackId"])
                try:
                    targetInfo, state = player.targetinfo_set.get_or_create(target_id=target_id)
                except BaseException:
                    player.targetinfo_set.filter(target_id=target_id).all().delete()
                    targetInfo, state = player.targetinfo_set.get_or_create(target_id=target_id)

                if state:
                    # create/update target
                    _, targetId, target = targetInfo.getTarget(update=True)

                else:
                    # delete target
                    targetInfo.delete()

                attack = player.attack_set.filter(tId=attack_id).first

            else:
                returnError(type=403, msg="Unknown request")
            faction = getFaction(player.factionId)

            faction_targets = FactionTarget.objects.filter(target_id__in=faction.getTargetsId())
            context = {
                "v": attack,
                "targets": getTargets(player),
                "ts": int(time.time()),
                "faction_targets": faction_targets.values_list("target_id", flat=True),
            }
            return render(request, "target/attacks/button-target.html", context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don't try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def targets(request):
    try:
        if request.session.get("player"):
            player = getPlayer(request.session["player"].get("tId"))

            targets = getTargets(player)

            # get faction
            faction = Faction.objects.filter(tId=player.factionId).first()
            factionTargets = [] if faction is None else faction.getTargetsId()

            context = {
                "player": player,
                "targetcat": True,
                "targets": targets,
                "factionTargets": factionTargets,
                "ts": int(time.time()),
                "view": {"targets": True},
            }
            page = "target/content-reload.html" if request.method == "POST" else "target.html"
            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def targetsList(request):
    try:
        if request.session.get("player") and request.method == "POST":
            player = getPlayer(request.session["player"].get("tId"))

            if request.POST["action_type"] == "export":
                targets = getTargets(player)
                response = HttpResponse(json.dumps(targets, separators=(",", ":")), content_type="text/json")
                response["Content-Disposition"] = 'attachment; filename="target_list.json"'
                return response

            elif request.POST["action_type"] == "delete":
                player.targetinfo_set.all().delete()

            elif request.POST["action_type"] == "import" and len(request.FILES):
                file = request.FILES["json_file"]

                if file.content_type == "application/json":
                    targets = json.loads(file.read())
                    try:
                        for k, v in targets.items():
                            defaults = {
                                "update_timestamp": int(v["update_timestamp"]),
                                "last_attack_timestamp": int(v["last_attack_timestamp"]),
                                "fair_fight": float(v["fair_fight"]),
                                "base_respect": float(v["base_respect"]),
                                "flat_respect": float(v["flat_respect"]),
                                "result": str(v["result"])[:16],
                                "color": int(v["color"]),
                                "note": str(v["note"])[:128],
                            }

                            player.targetinfo_set.get_or_create(target_id=k, defaults=defaults)

                    except BaseException as e:
                        message = "Error in the json file: {}".format(e)
                        return returnError(type=404, msg=message)

                else:
                    targets = getTargets(player)
                    message = "Wrong file format. Require: application/json. Give: {}".format(file.content_type)
                    return returnError(type=404, msg=message)

            return redirect("/target/")

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don't try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def target(request):
    try:
        if request.session.get("player") and request.method == "POST":
            player = getPlayer(request.session["player"].get("tId"))

            # if cache.get('disable-status', False):
            #     context = {"apiErrorLine": "Server overloaded. Feature temporarily disabled."}
            #     return render(request, 'target/targets/line.html', context)

            if request.POST.get("type", False):
                # update target
                if request.POST["type"] == "update":
                    target_id = int(request.POST["targetId"])
                    try:
                        targetInfo, _ = player.targetinfo_set.get_or_create(target_id=target_id)
                    except BaseException:
                        player.targetinfo_set.filter(target_id=target_id).all().delete()
                        targetInfo, _ = player.targetinfo_set.get_or_create(target_id=target_id)

                    error, targetId, target = targetInfo.getTarget(update=True)

                    if error:
                        context = {"apiErrorLine": "Error while updating {}: {}".format(target, error.get("apiError", "Unknown error"))}
                    else:
                        faction = Faction.objects.filter(tId=player.factionId).first()
                        factionTargets = [] if faction is None else faction.getTargetsId()
                        context = {
                            "player": player,
                            "factionTargets": factionTargets,
                            "target": target,
                            "targetId": target_id,
                            "ts": int(time.time()),
                        }

                    return render(request, "target/targets/line.html", context)

                if request.POST["type"] == "note":
                    target_id = int(request.POST["targetId"])
                    targetInfo, _ = player.targetinfo_set.get_or_create(target_id=target_id)
                    targetInfo.note = str(request.POST["note"])[:128]
                    targetInfo.save()

                    context = {
                        "target": {"note": targetInfo.note, "color": targetInfo.color},
                        "targetId": target_id,
                    }

                    return render(request, "target/targets/note.html", context)

                if request.POST["type"] == "note-color":
                    target_id = int(request.POST["targetId"])
                    targetInfo, _ = player.targetinfo_set.get_or_create(target_id=target_id)
                    targetInfo.color = (targetInfo.color + 1) % 4
                    targetInfo.save()

                    context = {
                        "target": {"note": targetInfo.note, "color": targetInfo.color},
                        "targetId": target_id,
                    }

                    return render(request, "target/targets/note.html", context)

                # add by Id target
                if request.POST["type"] == "addById":
                    try:
                        target_id = int(request.POST["targetId"])
                        targetInfo, _ = player.targetinfo_set.get_or_create(target_id=target_id)
                        targetInfo.getTarget(update=True)

                        faction = getFaction(player.factionId)
                        factionTargets = [] if faction is None else faction.getTargetsId()
                        targets = getTargets(player)
                        context = {
                            "player": player,
                            "targets": targets,
                            "factionTargets": factionTargets,
                            "targetId": target_id,
                            "ts": int(time.time()),
                        }

                    except BaseException as e:
                        faction = getFaction(player.factionId)
                        factionTargets = [] if faction is None else faction.getTargetsId()
                        targets = getTargets(player)
                        context = {
                            "player": player,
                            "targets": targets,
                            "factionTargets": factionTargets,
                            "addError": e,
                            "ts": int(time.time()),
                        }

                    return render(request, "target/targets/index.html", context)

                # delete target
                if request.POST["type"] == "delete":
                    target_id = int(request.POST["targetId"])
                    targetInfo, _ = player.targetinfo_set.get(target_id=target_id).delete()

                    return render(request, "target/targets/line.html")

            else:
                # should not happen
                context = {"target": None, "targetId": None, "ts": int(time.time())}
                return render(request, "target/targets/line.html", context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don't try to be a smart ass."
            return returnError(type=403, msg=message)

    except BaseException as e:
        context = {"apiErrorLine": "Error while updating target: {}".format(e)}
        return render(request, "target/targets/line.html", context)


def revives(request):
    try:
        if request.session.get("player"):
            print("[view.traget.attacks] get player id from session")
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(time.time())
            player.save()

            error, revives = updateRevives(player)

            # breakdown
            breakdownType = dict({})
            breakdownStatus = dict({})
            breakdownPlayer = dict({})
            for r in player.revive_set.all():
                outgoing = r.reviver_id == player.tId
                i = 0 if outgoing else 1
                target_id = r.target_id if outgoing else r.reviver_id
                target_name = r.target_name if outgoing else r.reviver_name

                if r.target_hospital_reason not in breakdownType:
                    breakdownType[r.target_hospital_reason] = [0, 0]

                if r.target_last_action_status not in breakdownStatus:
                    breakdownStatus[r.target_last_action_status] = [0, 0]

                if target_id not in breakdownPlayer:
                    breakdownPlayer[target_id] = [0, 0, target_name]

                breakdownType[r.target_hospital_reason][i] += 1
                breakdownStatus[r.target_last_action_status][i] += 1
                breakdownPlayer[target_id][i] += 1

            breakdownType = sorted(breakdownType.items(), key=lambda x: x[0])
            breakdownStatus = sorted(breakdownStatus.items(), key=lambda x: x[0])
            breakdownPlayer = sorted(breakdownPlayer.items(), key=lambda x: x[0])

            revives = Paginator(revives, 25).get_page(request.GET.get("p_re"))

            context = {
                "player": player,
                "targetcat": True,
                "revives": revives,
                "breakdownPlayer": breakdownPlayer,
                "breakdownType": breakdownType,
                "breakdownStatus": breakdownStatus,
                "view": {"revives": True},
            }
            context["apiErrorSub"] = error["apiError"] if error else False

            page = "target/content-reload.html" if request.method == "POST" else "target.html"
            if request.GET.get("p_re", False):
                page = "target/revives/revives.html"

            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def revive(request):
    try:
        if request.session.get("player") and request.method == "POST":
            player = getPlayer(request.session["player"].get("tId"))

            r = player.revive_set.filter(tId=request.POST.get("reviveId", 0)).first()
            if r is not None:
                r.paid = not r.paid
                r.save()

            return render(request, "target/revives/buttons.html", {"revive": r})

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don't try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


@csrf_exempt
def targetImport(request):
    if request.method == "POST":
        try:
            # get payload
            body = json.loads(request.body)

            if "key" not in body:
                return JsonResponse({"message": "couldn't find key 'key' in the payload"}, status=400)
            if "targets" not in body:
                return JsonResponse(
                    {"message": "couldn't find key 'targets' in the payload"},
                    status=400,
                )

            # get user
            player_key = Key.objects.filter(value=body.get("key")).first()
            if player_key is None:
                return JsonResponse({"message": "Player not found in YATA's database"}, status=400)

            added = []

            if "user" not in body:
                print("old version")

                # old version of torn pda
                for target_id, note in body.get("targets", {}).items():
                    if target_id.isdigit():
                        (
                            info,
                            create,
                        ) = player_key.player.targetinfo_set.update_or_create(target_id=int(target_id), defaults={"note": note})
                        if create:
                            added.append(target_id)

            else:
                print("new version")
                # old version of torn pda
                for target_id, target_data in body.get("targets", {}).items():
                    if target_id.isdigit():
                        (
                            info,
                            create,
                        ) = player_key.player.targetinfo_set.update_or_create(target_id=int(target_id), defaults=target_data)
                        if create:
                            added.append(target_id)

            if len(added):
                return JsonResponse(
                    {"message": f'You added {len(added)} targets: {", ".join(added)}'},
                    status=200,
                )
            else:
                return JsonResponse({"message": "No targets have been added"}, status=200)

        except BaseException as e:
            return JsonResponse({"message": f"YATA error: {e}"}, status=500)

    else:
        return JsonResponse({"message": "POST request needed"}, status=400)


def targetExport(request):
    try:
        # get api key
        key = request.GET.get("key")

        if key is None:
            return JsonResponse({"message": "You need to enter your API key"}, status=400)

        # get user
        player_key = Key.objects.filter(value=key).first()
        if player_key is None:
            return JsonResponse({"message": "Player not found in YATA's database"}, status=400)

        targets = {}
        for t in player_key.player.targetinfo_set.all():
            _, _, target = t.getTarget()
            targets[str(t.target_id)] = target

        return JsonResponse({"targets": targets}, status=200)

    except BaseException as e:
        return JsonResponse({"message": f"YATA error: {e}"}, status=500)

