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
from player.models import Key


@ratelimit(key='ip', rate='10/h')
def exportTargets(request):
    try:
        if getattr(request, 'limited', False):
            return JsonResponse({"error": {"code": 3, "error": "Too many requests (10 calls / hour)"}}, status=429)

        # get api key
        key = request.GET.get("key")

        if key is None:
            return JsonResponse({"error": {"code": 2, "error": "You need to enter your API key"}}, status=400)

        # get user
        player_key = Key.objects.filter(value=key).first()
        if player_key is None:
            return JsonResponse({"error": {"code": 2, "error": "Player not found in YATA's database"}}, status=400)

        targets = {}
        for t in player_key.player.targetinfo_set.all():
            _, _, target = t.getTarget()
            targets[str(t.target_id)] = target

        return JsonResponse({"targets": targets}, status=200)

    except BaseException as e:
        return JsonResponse({"error": {"code": 1, "error": str(e)}}, status=500)


@csrf_exempt
def importTargets(request):
    try:
        if request.method != 'POST':
            return JsonResponse({"error": {"code": 2, "error": "POST request needed"}}, status=400)

        # get payload
        body = json.loads(request.body)

        for key in ["key", "targets"]:
            if key not in body:
                return JsonResponse({"error": {"code": 2, "error": f"Couldn't find key '{key}' in the payload"}}, status=400)

        # get user
        player_key = Key.objects.filter(value=body.get("key")).first()
        if player_key is None:
            return JsonResponse({"error": {"code": 2, "error": "Player not found in YATA's database"}}, status=400)

        added = []
        for target_id, target_data in body.get("targets", {}).items():
            if target_id.isdigit():
                info, create = player_key.player.targetinfo_set.update_or_create(target_id=int(target_id), defaults=target_data)
                if create:
                    added.append(target_id)

        if len(added):
            return JsonResponse({"message": f'You added {len(added)} targets: {", ".join(added)}'}, status=200)
        else:
            return JsonResponse({"message": f'No new targets added'}, status=200)

    except BaseException as e:
        return JsonResponse({"error": {"code": 1, "error": str(e)}}, status=500)
