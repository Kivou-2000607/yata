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
from django.views.decorators.cache import cache_page
from ratelimit.decorators import ratelimit
from ratelimit.core import get_usage, is_ratelimited

# yata
from yata.handy import tsnow
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

# @cache_page(60*5)
@ratelimit(key='ip', rate='5/m')
def loot(request):
    try:

        if getattr(request, 'limited', False):
            payload = {"error": {"code": 2, "error": "Rate limit of 5 calls / m"}}
            status = 429

        else:
            # get time
            ts = tsnow()

            # get npcs
            npcs = {npc.tId: npc.hospitalTS for npc in NPC.objects.filter(show=True).order_by('hospitalTS')}

            # by default next update is in an hour
            next_update = ts + DEFAULT_UPDATE
            for id, hosp_out in npcs.items():
                # check if not to be ignored ignored (IGNORE_TIME seconds after loot level)
                if ts + IGNORE_TIME < hosp_out + UPDATE_LEVEL:
                    next_update = hosp_out + UPDATE_LEVEL + UPDATE_TIME
                    break

            payload = {
                "hosp_out": npcs,
                "next_update": next_update
            }

            status = 200
            return JsonResponse(payload, status=200)

    except BaseException as e:
        payload = {"error": {"code": 1, "error": f'{e}'}}
        status = 500

    return JsonResponse(payload, status=status)
