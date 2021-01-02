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
from setup.models import Balance
from player.models import PlayerData


def donations(request):
    try:

        b = Balance.objects.last()
        payload = {
            "schemaVersion": 1,
            "label": "Donations",
            "message": f'{float(b.paypal_balance)-float(b.droplet_account_balance):0.2f} EUR',
            "color": "orange",
            "cacheSeconds": 3600,
            "namedLogo": "paypal",
        }
        return JsonResponse(payload, status=200, safe=False)

    except BaseException as e:
        return JsonResponse({"error": {"code": 1, "error": str(e)}}, status=500)


def players(request):
    try:

        nPlayers = PlayerData.objects.first()
        payload = {
            "schemaVersion": 1,
            "label": "Users: Total / Monthly / Daily / Hourly",
            "message": f"{nPlayers.nTotal} / {nPlayers.nMonth} / {nPlayers.nDay} / {nPlayers.nHour}",
            "color": "orange",
            "cacheSeconds": 3600,
        }
        return JsonResponse(last_actions, status=200, safe=False)

    except BaseException as e:
        return JsonResponse({"error": {"code": 1, "error": str(e)}}, status=500)
