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
# django
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db import connection

# cache and rate limit
from django.views.decorators.cache import cache_page
from ratelimit.decorators import ratelimit
from ratelimit.core import get_usage, is_ratelimited

# standards
import json

# yaya
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
            player.active = True
            player.save()

        else:
            player = Player.objects.filter(tId=-1).first()

        NPCs = [npc for npc in NPC.objects.filter(show=True).order_by('tId')]
        context = {"player": player, "NPCs": NPCs}
        return render(request, "loot.html", context)

    except Exception as e:
        return returnError(exc=e, session=request.session)


# API
# @cache_page(60)
@ratelimit(key='ip', rate='1/30s')
def timings(request):
    if getattr(request, 'limited', False):
        return JsonResponse({"error": {"code": 429, "error": "Rate limit of 1 call / 30s"}}, status=429)

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
                "levels": {'current': c['lvl'], 'next': n['lvl']}}

        return HttpResponse(json.dumps(npcs, separators=(',', ':')), content_type="application/json")

    except BaseException as e:
        return HttpResponse(json.dumps({"error": {"code": 500, "error": "{}".format(type(e))}}), content_type="application/json")
    # return HttpResponse(json.dumps({"error": {"code": 500, "error": "API currently closed... sorry"}}), content_type="application/json")
