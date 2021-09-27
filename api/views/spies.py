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
import time

# yata
from yata.handy import getPlayerBykey
from yata.handy import getFaction
from yata.regex import compile_api_key
from faction.models import SpyDatabase


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


@csrf_exempt
def importSpies(request):
    try:
        if request.method != 'POST':
            return JsonResponse({"error": {"code": 2, "error": "POST request needed"}}, status=400)

        # get payload
        body = json.loads(request.body)

        for key in ["key", "spies"]:
            if key not in body:
                return JsonResponse({"error": {"code": 2, "error": f"Couldn't find key '{key}' in the payload"}}, status=400)

        # check key
        key = body["key"]
        if compile_api_key().match(key) is None:
            return JsonResponse({"error": {"code": 2, "error": f"Invalid API key"}}, status=400)

        # get player
        player = getPlayerBykey(key)
        if player is None:
            return JsonResponse({"error": {"code": 2, "error": "Player not found"}}, status=400)

        # get faction
        faction = getFaction(player.factionId)
        if faction is None:
            return JsonResponse({"error": {"code": 2, "error": "Faction not found"}}, status=400)

        # get spy databases
        if "secret" in body:
            databases = SpyDatabase.objects.filter(secret=body["secret"]).all()
        else:
            databases = faction.spydatabase_set.all()

        # check if database
        if not len(databases):
            return JsonResponse({"error": {"code": 2, "error": "No spies databases found"}}, status=400)

        # add spies
        for db in databases:
            spies = {}
            for target_id, v in body["spies"].items():
                # refactor payload
                strength = v.get("strength", -1)
                speed = v.get("speed", -1)
                defense = v.get("defense", -1)
                dexterity = v.get("dexterity", -1)
                total = v.get("total", -1)
                spies[target_id] = {
                    "target_name": v.get("target_name", "Player"),
                    "target_faction_name": v.get("target_faction_name", "Faction"),
                    "target_faction_id": v.get("target_faction_id", 0),
                    "strength": strength,
                    "speed": speed,
                    "defense": defense,
                    "dexterity": dexterity,
                    "total": total,
                    "strength_timestamp": v.get("timestamp", int(time.time())) if strength + 1 else 0,
                    "speed_timestamp": v.get("timestamp", int(time.time())) if speed + 1 else 0,
                    "defense_timestamp": v.get("timestamp", int(time.time())) if defense + 1 else 0,
                    "dexterity_timestamp": v.get("timestamp", int(time.time())) if dexterity + 1 else 0,
                    "total_timestamp": v.get("timestamp", int(time.time())) if total + 1 else 0,
                }
            db.updateSpies(payload=spies)

        if len(spies):
            return JsonResponse({"message": f'You added {len(spies)} spies in {len(databases)} db'}, status=200)
        else:
            return JsonResponse({"message": f'No new targets added'}, status=200)

    except BaseException as e:
        return JsonResponse({"error": {"code": 1, "error": str(e)}}, status=500)
