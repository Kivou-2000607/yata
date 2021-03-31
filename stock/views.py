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
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings

import json

from player.models import Player
from stock.models import Stock

from yata.handy import apiCall
from yata.handy import returnError
from yata.handy import timestampToDate
from yata.handy import getPlayer


def index(request, select='all'):
    try:
        player = getPlayer(request.session.get("player", {}).get("tId", -1))
        key = player.getKey()

        # update personal stocks
        error = False
        if player.tId > 0:
            myStocks = apiCall("user", "", "stocks,timestamp", key=key)
            if 'apiError' in myStocks:
                error = {"apiErrorSub": myStocks["apiError"]}
            else:
                print('[view.stock.list] save my stocks')
                if myStocks.get("stocks") is not None:
                    myStocks["stocks"] = myStocks.get("stocks")
                else:
                    myStocks["stocks"] = dict({})
                player.stocksJson = json.dumps(myStocks.get("stocks", dict({})))
                player.stocksInfo = len(myStocks.get("stocks", []))
                player.stocksUpda = int(myStocks.get("timestamp", 0))
        player.save()

        # load torn stocks and add personal stocks to torn stocks
        stocks = {s.tId: {'t': s} for s in Stock.objects.all()}
        ts = stocks[0]['t'].timestamp

        for k, v in json.loads(player.stocksJson).items():
            tId = v['stock_id']
            if tId in stocks:
                tstock = stocks[tId].get('t')
                # ts = max(ts, tstock.timestamp)

                # add profit
                v['profit'] = (float(tstock.tCurrentPrice) - float(v["bought_price"])) / float(v["bought_price"])
                # add if bonus
                if tstock.tRequirement:
                    v['bonus'] = 1 if v['shares'] >= tstock.tRequirement else 0

                if stocks[tId].get('p') is None:
                    stocks[tId]['p'] = [v]
                else:
                    stocks[tId]['p'].append(v)

        # select stocks
        if select in ['hd']:
            stocks = {k: v for k, v in sorted(stocks.items(), key=lambda x: x[1]['t'].dayTendency) if v['t'].tDemand in ["High", "Very High"]}
        elif select in ['ld']:
            stocks = {k: v for k, v in sorted(stocks.items(), key=lambda x: -x[1]['t'].dayTendency) if v['t'].tDemand in ["Low", "Very Low"]}
        elif select in ['gf']:
            stocks = {k: v for k, v in sorted(stocks.items(), key=lambda x: x[1]['t'].dayTendency) if v['t'].tForecast in ["Good", "Very Good"]}
        elif select in ['pf']:
            stocks = {k: v for k, v in sorted(stocks.items(), key=lambda x: -x[1]['t'].dayTendency) if v['t'].tForecast in ["Poor", "Very Poor"]}
        elif select in ['ns']:
            stocks = {k: v for k, v in sorted(stocks.items(), key=lambda x: -x[1]['t'].dayTendency) if v['t'].tAvailableShares in [0]}
        elif select in ['lo']:
            stocks = {k: v for k, v in sorted(stocks.items(), key=lambda x: -x[1]['t'].dayTendency) if v['t'].tAvailableShares <= 0.01 * v['t'].tTotalShares}
        elif select in ['my']:
            stocks = {k: v for k, v in sorted(stocks.items(), key=lambda x: x[1]['t'].dayTendency) if v.get('p') is not None}
        else:
            stocks = {k: v for k, v in sorted(stocks.items(), key=lambda x: x[0])}

        context = {'player': player, 'stocks': stocks, 'lastUpdate': ts, 'stockcat': True, 'view': {'list': True}}
        if error:
            context.update(error)
        page = 'stock/content-reload.html' if request.method == 'POST' else 'stock.html'
        return render(request, page, context)

    except Exception:
        return returnError()


def details(request, tId):
    try:
        if request.method == "POST":
            stock = {'t': Stock.objects.filter(tId=tId).first()}

            context = {'stock': stock}
            return render(request, 'stock/details.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


def prices(request, tId, period=None):
    try:
        if request.method == "POST":
            player = getPlayer(request.session.get("player", {}).get("tId", -1))
            stock = {'t': Stock.objects.filter(tId=tId).first()}

            # timestamp rounded at the hour
            ts = int(timezone.now().timestamp())
            ts = int(ts) - int(ts) % 3600

            page = "stock/prices.html" if period is None else "stock/prices-graphs.html"
            period = "7" if period is None else period

            try:
                periodS = int(period) * 24 * 3600
            except BaseException:
                periodS = ts

            history = stock.get('t').history_set.filter(timestamp__gte=(ts - periodS)).order_by('timestamp')

            av = stock.get('t').averagePrice

            graph = []
            firstTS = history.first().timestamp
            lastTS = history.last().timestamp

            # if periodS > 2592000:  # use averaged values for larg graphs (> 1 month)
            if periodS > 1209600:  # use averaged values for larg graphs (> 2 weeks)
                floatingTS = history.first().timestamp
                avg_val = [0, 0, 0, 0]
                n = 0
                for h in history:
                    n += 1
                    t = h.timestamp
                    dt = stock.get('t').dayTendencyA * float(t) + stock.get('t').dayTendencyB  # day tendancy
                    wt = stock.get('t').weekTendencyA * float(t) + stock.get('t').weekTendencyB  # week tendancy

                    avg_val[0] += h.timestamp
                    avg_val[1] += h.tCurrentPrice
                    avg_val[2] += h.tAvailableShares
                    avg_val[3] += h.tTotalShares

                    # make the average and save the line every week
                    if t - floatingTS > (lastTS - firstTS) / 256:
                        floatingTS = t
                        line = [avg_val[0] // n, avg_val[1] / float(n), dt, wt, avg_val[2] // n, avg_val[3] // n, h.tForecast, h.tDemand, av]
                        graph.append(line)
                        avg_val = [0, 0, 0, 0]
                        n = 0

                # record last point
                if n > 0:
                    line = [avg_val[0] // n, avg_val[1] / float(n), dt, wt, avg_val[2] // n, avg_val[3] // n, h.tForecast, h.tDemand, av]
                    graph.append(line)

            else:  # use all values for recent data

                for h in history:
                    t = h.timestamp
                    dt = stock.get('t').dayTendencyA * float(t) + stock.get('t').dayTendencyB  # day tendancy
                    wt = stock.get('t').weekTendencyA * float(t) + stock.get('t').weekTendencyB  # week tendancy
                    line = [t, h.tCurrentPrice, dt, wt, h.tAvailableShares, h.tTotalShares, h.tForecast, h.tDemand, av]
                    graph.append(line)

            # convert timestamp to date and remove clean interplation lines
            # keep last point as is (for interpolation problems)
            graphLength = 0
            maxTS = ts
            for i, (t, p, dt, wt, _, _, _, _, _) in enumerate(graph[:-1]):

                # remove 0 prices
                if not int(p):
                    graph[i][1] = "null"
                else:
                    graphLength += 1

                if int(maxTS) - int(t) > 3600 * 24 or dt < 0:
                    graph[i][2] = "null"
                if int(maxTS) - int(t) > 3600 * 24 * 7 or wt < 0:
                    graph[i][3] = "null"

                # convert timestamp to date
                graph[i][0] = timestampToDate(int(t))
            graph[-1][0] = timestampToDate(graph[-1][0])

            # add personal stocks to torn stocks
            for k, v in json.loads(player.stocksJson).items():
                if int(v['stock_id']) == int(tId):

                    # add profit
                    v['profit'] = (float(stock.get('t').tCurrentPrice) - float(v["bought_price"])) / float(v["bought_price"])
                    # add if bonus
                    if stock.get('t').tRequirement:
                        v['bonus'] = 1 if v['shares'] >= stock.get('t').tRequirement else 0

                    if stock.get('p') is None:
                        stock['p'] = [v]
                    else:
                        stock['p'].append(v)

            context = {'stock': stock, "graph": graph, "graphLength": graphLength, "period": period}
            return render(request, page, context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()
