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

#
# def index(request):
#     try:
#         if request.session.get('player'):
#             print('[view.stock.index] get player id from session')
#             tId = request.session["player"].get("tId")
#             player = Player.objects.filter(tId=tId).first()
#             player.lastActionTS = int(timezone.now().timestamp())
#             key = player.key
#
#             stocks = Stock.objects.all().order_by("tId")
#
#             context = {'player': player, 'stocks': stocks, 'lastUpdate': stocks[0].timestamp, 'stockcat': True, 'view': {'list': True}}
#             return render(request, 'stock.html', context)
#
#         else:
#             return returnError(type=403, msg="You might want to log in.")
#
#     except Exception:
#         return returnError()


def list(request):
    try:
        if request.session.get('player'):
            print('[view.stock.list] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            key = player.key

            # update personal stocks
            error = False
            myStocks = apiCall("user", "", "stocks,timestamp", key=key)
            if 'apiError' in myStocks:
                error = {"apiErrorSub": myStocks["apiError"]}
            else:
                print('[view.stock.list] save my stocks')
                player.stocksJson = json.dumps(myStocks.get("stocks", dict({})))
                player.stocksUpda = int(myStocks.get("timestamp", 0))
                player.save()

            # update the torn stock (or not...)
            # stocks = apiCall("torn", "", "stocks,timestamp", key=key)
            # for k, v in stocks["stocks"].items():
            #     stock = Stock.objects.filter(tId=int(k)).first()
            #     if stock is None:
            #         stock = Stock.create(k, v, stocks["timestamp"])
            #     else:
            #         stock.update(k, v, stocks["timestamp"])
            #     stock.save()

            # load torn stocks
            stocks = {s.tId: {'t': s} for s in Stock.objects.all().order_by("tId")}

            # # add personal stocks to torn stocks
            for k, v in json.loads(player.stocksJson).items():
                tId = v['stock_id']
                if stocks[tId].get('p') is None:
                    stocks[tId]['p'] = [v]
                else:
                    stocks[tId]['p'].append(v)

            context = {'player': player, 'stocks': stocks, 'lastUpdate': stocks[0]['t'].timestamp, 'stockcat': True, 'view': {'list': True}}
            if error:
                context.update(error)
            page = 'stock/content-reload.html' if request.method == 'POST' else 'stock.html'
            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


def details(request, tId):
    try:
        if request.session.get('player') and request.method == "POST":
            stock = {'t': Stock.objects.filter(tId=tId).first()}

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
            player = Player.objects.filter(tId=request.session["player"].get("tId")).first()
            stock = {'t': Stock.objects.filter(tId=tId).first()}

            # create price histogram
            priceHistory = sorted(json.loads(stock.get('t').priceHistory).items(), key=lambda x: x[0])

            graph = [[timestampToDate(int(t)), p, stock.get('t').dayTendencyA * float(t) + stock.get('t').dayTendencyB, stock.get('t').weekTendencyA * float(t) + stock.get('t').weekTendencyB] for t, p in priceHistory]
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

            # # add personal stocks to torn stocks
            for k, v in json.loads(player.stocksJson).items():
                if int(v['stock_id']) == int(tId):
                    v['profit'] = float(float(stock.get('t').tCurrentPrice) - float(v["bought_price"])) / float(v["bought_price"])
                    if stock.get('p') is None:
                        stock['p'] = [v]
                    else:
                        stock['p'].append(v)

            context = {'stock': stock, "graph": graph, "graphLength": graphLength}
            return render(request, 'stock/prices.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()
