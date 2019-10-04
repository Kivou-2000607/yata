from django.shortcuts import render
from django.utils import timezone

from yata.handy import returnError
from player.models import Player
from loot.models import NPC


def index(request):
    try:
        if request.session.get('player'):
            print('[view.loot.index] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())

            # update NPC status
            # for npc in NPC.objects.all():
            #     npc.update(key=player.key)

            context = {"player": player, "NPCs": NPC.objects.all()}
            return render(request, "loot.html", context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()
