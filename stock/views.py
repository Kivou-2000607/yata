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

from django.shortcuts import render
from django.utils import timezone
from django.conf import settings

import json

from player.models import Player
from stock.models import Stock

from yata.handy import apiCall
from yata.handy import returnError
from yata.handy import timestampToDate


def index(request):
    try:
        if request.session.get('player'):
            print('[view.stock.index] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            key = player.key

            stocks = Stock.objects.all().order_by("tId")

            context = {'player': player, 'stocks': stocks, 'lastUpdate': stocks[0].timestamp, 'stockcat': True, 'view': {'list': True}}
            return render(request, 'stock.html', context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


def list(request):
    try:
        if request.session.get('player'):
            print('[view.stock.list] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            key = player.key

            stocks = apiCall("torn", "", "stocks,timestamp", key=key)
            for k, v in stocks["stocks"].items():
                stock = Stock.objects.filter(tId=int(k)).first()
                if stock is None:
                    stock = Stock.create(k, v, stocks["timestamp"])
                else:
                    stock.update(k, v, stocks["timestamp"])
                stock.save()

            stocks = Stock.objects.all().order_by("tId")

            context = {'player': player, 'stocks': stocks, 'lastUpdate': stocks[0].timestamp, 'stockcat': True, 'view': {'list': True}}
            page = 'stock/content-reload.html' if request.method == 'POST' else 'stock.html'
            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


def details(request, tId):
    try:
        if request.session.get('player') and request.method == "POST":
            stock = Stock.objects.filter(tId=tId).first()

            context = {'stock': stock}
            return render(request, 'stock/details.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


def prices(request, tId):
    try:
        if request.session.get('player') and request.method == "POST":
            stock = Stock.objects.filter(tId=tId).first()

            # create price histogram
            priceHistory = sorted(json.loads(stock.priceHistory).items(), key=lambda x: x[0])

            graph = [[timestampToDate(int(t)), p, stock.dayTendencyA * float(t) + stock.dayTendencyB, stock.weekTendencyA * float(t) + stock.weekTendencyB] for t, p in priceHistory]
            graphLength = 0
            for i, (_, p, wt, mt) in enumerate(graph):
                if not int(p):
                    graph[i][1] = "null"
                    # graph[i][2] = "null"
                    # graph[i][3] = "null"
                else:
                    graphLength += 1
                if i < len(graph) - 24 or wt < 0:
                    graph[i][2] = "null"
                if i < len(graph) - 24 * 7 or mt < 0:
                    graph[i][3] = "null"

            context = {'stock': stock, "graph": graph, "graphLength": graphLength}
            return render(request, 'stock/prices.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()
