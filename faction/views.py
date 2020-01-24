from django.shortcuts import render
from django.shortcuts import redirect

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


def configurations(request):
    try:
        if request.session.get('player'):
            # get player
            player = getPlayer(request.session["player"].get("tId"))

            if player.factionAA:
                faction = Faction.objects.filter(tId=player.factionId).first()
                faction.manageKey(player)

                # update members before to avoid coming here before having members
                updateMembers(faction, key=player.getKey(), force=False)

                # get keys
                keys = faction.masterKeys.filter(useSelf=True)
                faction.nKeys = len(keys.filter(useFact=True))
                faction.save()

                # upgrade key
                context = {'player': player, 'factioncat': True, "bonus": BONUS_HITS, "faction": faction, 'keys': keys, 'view': {'aa': True}}
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

            faction.save()

            context = {'faction': faction}
            return render(request, 'faction/aa/poster.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()
