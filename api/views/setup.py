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


@cache_page(3600)
def donations(request):
    try:

        b = Balance.objects.last()
        balance = {
            "paypal": b.paypal_balance,
            "droplet": b.droplet_account_balance,
            "string": f'{float(b.paypal_balance)-float(b.droplet_account_balance):0.2f} EUR'
        }
        balance = f'{float(b.paypal_balance)-float(b.droplet_account_balance):0.2f}'
        return JsonResponse(balance, status=200)

    except BaseException as e:
        return JsonResponse({"error": {"code": 1, "error": str(e)}}, status=500)


@cache_page(5)
def players(request):
    try:

        nPlayers = PlayerData.objects.first()
        last_actions = {
            "hour": nPlayers.nHour,
            "day": nPlayers.nDay,
            "month": nPlayers.nMonth,
            "total": nPlayers.nTotal,
            "string": f"{nPlayers.nTotal} / {nPlayers.nMonth} / {nPlayers.nDay} / {nPlayers.nHour}",
        }
        return JsonResponse(last_actions, status=200)

    except BaseException as e:
        return JsonResponse({"error": {"code": 1, "error": str(e)}}, status=500)
