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

# standard
import json

# yata
from yata.handy import *
from player.models import Player
from loot.models import *


def index(request):
    try:
        player = getPlayer(request.session.get("player", {}).get("tId", -1))

        if player.tId > 0 and request.POST.get("type") in ["npc-vote", "npc-schedule"]:
            npc = NPC.objects.filter(show=True, tId=request.POST.get("npc_id")).first()
            if npc is not None:
                timestamp = int(request.POST.get("schedule_timestamp"))
                timestamp -= timestamp % 3600
                scheduled_attack = npc.scheduledattack_set.filter(timestamp=timestamp).first()
                if scheduled_attack is None:
                    scheduled_attack = npc.scheduledattack_set.create(timestamp=timestamp, author=f'{player.name} [{player.tId}]')

                users = json.loads(scheduled_attack.users)
                if str(player.tId) in users:
                    del users[str(player.tId)]
                else:
                    users[str(player.tId)] = f'{player.name} [{player.tId}]'

                scheduled_attack.vote = len(users)
                scheduled_attack.users = json.dumps(users)

                if not scheduled_attack.vote:
                    scheduled_attack.delete()
                else:
                    scheduled_attack.save()

                if request.POST.get("type") == "npc-vote":
                    return render(request, "loot/vote.html", {"player": player, "sa": scheduled_attack})

        ScheduledAttack.objects.filter(timestamp__lt=tsnow()).delete()
        scheduled_attacks = ScheduledAttack.objects.all().order_by("timestamp")

        NPCs = [npc for npc in NPC.objects.filter(show=True).order_by('tId')]

        context = {"player": player, "NPCs": NPCs, "scheduled_attacks": scheduled_attacks}
        page = 'loot/content-reload.html' if request.method == 'POST' else 'loot.html'
        page = "loot/vote.html" if request.POST.get("type") == "npc-vote" else page
        return render(request, page, context)

    except Exception as e:
        return returnError(exc=e, session=request.session)
