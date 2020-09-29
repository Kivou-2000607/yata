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

@cache_page(60*5)
@ratelimit(key='ip', rate='5/m')
def loot(request):
    try:

        if getattr(request, 'limited', False):
            payload = {"error": {"code": 2, "error": "Rate limit of 5 calls / m"}}
            status = 429

        else:
                payload = {
                    "hospout": {npc.tId: npc.hospitalTS for npc in NPC.objects.filter(show=True).order_by('tId')},
                    "timestamp": tsnow()
                    }
                status = 200
                return JsonResponse(payload, status=200)

    except BaseException as e:
        payload = {"error": {"code": 1, "error": f'{e}'}}
        status = 500

    return JsonResponse(payload, status=status)
