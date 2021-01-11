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
# django
from django.http import JsonResponse

# cache and rate limit
from django.utils.decorators import method_decorator
from yata.decorators import never_ever_cache

# yata
from yata.handy import tsnow
from yata.handy import timestampToDate
from loot.models import NPC

# update level
# UPDATE_LEVEL = 0  # level 1
# UPDATE_LEVEL = 30 * 60  # level 2
# UPDATE_LEVEL = 90 * 60  # level 3
UPDATE_LEVEL = 210 * 60  # level 4
# UPDATE_LEVEL = 450 * 60  # level 5

IGNORE_TIME = 30 * 60  # ignore a NPC if he passes the loot level

DEFAULT_UPDATE = 60 * 60  # by default next update is in an hour

UPDATE_TIME = 15 * 60  # time elapsed after the loot level to do the update


@method_decorator(never_ever_cache)
def loot(request):
    try:

        if getattr(request, 'limited', False):
            return JsonResponse({"error": {"code": 3, "error": "Too many requests (10 calls / hour)"}}, status=429)

        # get time
        ts = tsnow()

        # get npcs
        npcs = {npc.tId: npc.hospitalTS for npc in NPC.objects.filter(show=True).order_by('hospitalTS')}

        # by default next update is in an hour
        next_update = ts + DEFAULT_UPDATE
        for id, hosp_out in npcs.items():
            # check if not to be ignored (IGNORE_TIME seconds after loot level)
            if ts + IGNORE_TIME < hosp_out + UPDATE_LEVEL:
                next_update = hosp_out + UPDATE_LEVEL + UPDATE_TIME
                break

        debug = {
            "hosp_out": {k: timestampToDate(v, fmt=True) for k, v in npcs.items()},
            "next_update": timestampToDate(next_update, fmt=True),
            "timestamp": timestampToDate(ts, fmt=True),
            "message": "This field is temporary to help debug cloudflare cache system. Don't use it in your code."
        }

        payload = {
            "hosp_out": npcs,
            "next_update": next_update,
            "timestamp": ts,
            "debug": debug
        }


        return JsonResponse(payload, status=200)

    except BaseException as e:
        return JsonResponse({"error": {"code": 1, "error": str(e)}}, status=500)
