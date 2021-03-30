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

import json

from stock.models import Stock
from yata.handy import tsnow

def alerts(request):
    try:
        stocks = Stock.objects.all()
        payload = dict({})
        for stock in stocks:
            triggers = json.loads(stock.triggers)
            # if triggers:
            #     ts = tsnow()
            #     periodS = 3600 * 24 * 14
            #     graph = []
            #     for h in stock.history_set.filter(timestamp__gte=(ts - periodS)).order_by('timestamp'):
            #         graph.append([h.timestamp, h.tCurrentPrice])

            payload[str(stock.tId)] = {"alerts": triggers, "price": stock.tCurrentPrice, "shares": stock.tAvailableShares}

            # debug
            if request.GET.get("debug", False):
                payload["42"] = {"alerts": {"below": True, "enough": True, "forecast": True}, "price": 42, "shares": 10}

        return JsonResponse(payload, status=200)

    except BaseException as e:
        return JsonResponse({"error": {"code": 1, "error": str(e)}}, status=500)
