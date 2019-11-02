from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.db import connection

import json

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

            context = {"player": player, "NPCs": [npc for npc in NPC.objects.filter(show=True).order_by('tId')]}
            return render(request, "loot.html", context)

        else:

            player = Player.objects.filter(tId=-1).first()
            context = {"player": player, "NPCs": [npc for npc in NPC.objects.filter(show=True).order_by('tId')]}
            return render(request, "loot.html", context)
            # return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


# API
def timings(request):
    try:
        npcs = dict({})
        for npc in NPC.objects.filter(show=True).order_by('tId'):
            t = npc.lootTimings()
            c = npc.lootTimings("current")
            n = npc.lootTimings("next")
            del t[0]
            npcs[npc.tId] = {
                "name": npc.name,
                "hospout": npc.hospitalTS,
                "update": npc.updateTS,
                "status": npc.status,
                "timings": {k: {"due": t[k]['due'], "ts": t[k]['ts'], "pro": t[k]['pro']} for k in t},
                "levels": {'current': c['lvl'], 'next': n['lvl']}
                }

        return HttpResponse(json.dumps(npcs), content_type="application/json")

    except BaseException as e:
        return HttpResponse(json.dumps({"error": {"code": 500, "error": "{}".format(type(e))}}), content_type="application/json")
    # return HttpResponse(json.dumps({"error": {"code": 500, "error": "API currently closed... sorry"}}), content_type="application/json")
