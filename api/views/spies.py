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
from django.views.decorators.csrf import csrf_exempt

# cache and rate limit
from django.views.decorators.cache import cache_page
from ratelimit.decorators import ratelimit
from ratelimit.core import get_usage, is_ratelimited

# standards
import json

# yata
from yata.handy import getPlayerBykey
from yata.handy import getFaction
from yata.regex import compile_api_key


def getSpy(request, target_id):
    try:

        # check if key is correct
        key = str(request.GET.get("key"))
        if compile_api_key().match(key) is None:
            return JsonResponse({"error": {"code": 2, "error": f"Invalid API key"}}, status=400)

        # get user
        player = getPlayerBykey(key)
        if player is None:
            return JsonResponse({"error": {"code": 2, "error": "Player not found"}}, status=400)

        faction = getFaction(player.factionId)
        if faction is None:
            return JsonResponse({"error": {"code": 2, "error": "Faction not found"}}, status=400)
        spies = faction.getSpies()

        return JsonResponse({"spies": {str(target_id): spies.get(int(target_id))}}, status=200)

    except BaseException as e:
        return JsonResponse({"error": {"code": 1, "error": str(e)}}, status=500)


@ratelimit(key='ip', rate='1/h')
def getSpies(request):
    try:

        # check if key is correct
        key = str(request.GET.get("key"))
        if compile_api_key().match(key) is None:
            return JsonResponse({"error": {"code": 2, "error": f"Invalid API key"}}, status=400)

        # get user
        player = getPlayerBykey(key)
        if player is None:
            return JsonResponse({"error": {"code": 2, "error": "Player not found"}}, status=400)

        faction = getFaction(player.factionId)
        if faction is None:
            return JsonResponse({"error": {"code": 2, "error": "Faction not found"}}, status=400)
        spies = faction.getSpies()

        return JsonResponse({"spies": spies}, status=200)

    except BaseException as e:
        return JsonResponse({"error": {"code": 1, "error": str(e)}}, status=500)
