# Copyright 2019 kivou.2000607@gmail.com
# 
# This file is part of yata.
# 
#     yata is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     any later version.
# 
#     yata is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with yata. If not, see <https://www.gnu.org/licenses/>.

from django.shortcuts import render
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from ratelimit.decorators import ratelimit

import json

from bazaar.models import Item
from bazaar.models import BazaarData
from bazaar.models import AbroadStocks
from bazaar.models import VerifiedClient
from player.models import Player
from yata.handy import apiCall
from yata.handy import returnError
from yata.handy import timestampToDate
from yata.handy import tsnow
from yata.handy import getPlayer


def index(request):
    try:
        player = getPlayer(request.session.get("player", {}).get("tId", -1))

        # get items
        itemsOnMarket = Item.objects.filter(onMarket=True).order_by('tName')
        tTypes = {r["tType"] for r in itemsOnMarket.values("tType").distinct()}
        items = []

        # get/update inventory
        inventory = player.getInventory()
        error = inventory if 'apiError' in inventory else False

        # build item list
        for tType in tTypes:
            item_list = []
            for item in itemsOnMarket.filter(tType=tType):
                item.stockI = inventory.get("inventory", {}).get(str(item.tId), [0, 0])[0]
                item.stockB = inventory.get("bazaar", {}).get(str(item.tId), [0, 0])[0]
                item.stockBP = inventory.get("bazaar", {}).get(str(item.tId), [0, 0])[1]
                item.stockD = inventory.get("display", {}).get(str(item.tId), [0, 0])[0]
                item.stock = item.stockI + item.stockB + item.stockD
                item_list.append(item)
            items.append((tType, item_list))

        context = {
            "player": player,
            'list': json.loads(player.bazaarList),
            "bazaarcat": True,
            "allItemsOnMarket": items,
            "view": {
                "refreshType": True,
                "timer": True,
                "hideType": True,
                "loopType": True
                },
            "keyLevelRequired": 2
            }
        if error:
            context.update(error)
        return render(request, 'bazaar.html', context)

        # else:
        #     return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def custom(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session.get("player", {}).get("tId", -1))

            # get items
            itemsOnMarket = Item.objects.filter(tId__in=json.loads(player.bazaarList)).order_by('tName')
            items = []

            # get/update inventory
            inventory = player.getInventory()
            error = inventory if 'apiError' in inventory else False

            # build item list
            item_list = []
            for item in itemsOnMarket:
                item.stockI = inventory.get("inventory", {}).get(str(item.tId), [0, 0])[0]
                item.stockB = inventory.get("bazaar", {}).get(str(item.tId), [0, 0])[0]
                item.stockBP = inventory.get("bazaar", {}).get(str(item.tId), [0, 0])[1]
                item.stockD = inventory.get("display", {}).get(str(item.tId), [0, 0])[0]
                item.stock = item.stockI + item.stockB + item.stockD
                item_list.append(item)
            items.append(('Custom', item_list))

            context = {
                "player": player,
                'list': json.loads(player.bazaarList),
                "bazaarcat": True,
                "allItemsOnMarket": items,
                "view": {"refreshType": True, "timer": True, "loopType": True},
                "keyLevelRequired": 2
            }
            if error:
                context.update(error)
            page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
            return render(request, page, context)
        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)

def my(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session.get("player", {}).get("tId", -1))


            # get/update inventory
            inventory = player.getInventory(force=True)
            error = inventory if 'apiError' in inventory else False

            # get items
            itemsOnMarket = Item.objects.filter(tId__in=inventory.get("bazaar", {})).order_by('tName')
            tTypes = {r["tType"] for r in itemsOnMarket.values("tType").distinct()}
            items = []

            # build item list
            for tType in tTypes:
                item_list = []
                for item in itemsOnMarket.filter(tType=tType):
                    item.stockI = inventory.get("inventory", {}).get(str(item.tId), [0, 0])[0]
                    item.stockB = inventory.get("bazaar", {}).get(str(item.tId), [0, 0])[0]
                    item.stockBP = inventory.get("bazaar", {}).get(str(item.tId), [0, 0])[1]
                    item.stockD = inventory.get("display", {}).get(str(item.tId), [0, 0])[0]
                    item.stock = item.stockI + item.stockB + item.stockD
                    item_list.append(item)
                items.append((tType, item_list))

            context = {
                "player": player,
                "list": json.loads(player.bazaarList),
                "bazaarcat": True,
                "allItemsOnMarket": items,
                "view": {"refreshType": True, "timer": True, "summaryByType": True, "loopType": True},
                "keyLevelRequired": 2
            }
            if error:
                context.update(error)
            page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
            return render(request, page, context)
        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def default(request):
    try:
        player = getPlayer(request.session.get("player", {}).get("tId", -1))

        # get items
        itemsOnMarket = Item.objects.filter(onMarket=True).order_by('tName')
        tTypes = {r["tType"] for r in itemsOnMarket.values("tType").distinct()}
        items = []

        # get/update inventory
        inventory = player.getInventory()
        error = inventory if 'apiError' in inventory else False

        # build item list
        for tType in tTypes:
            item_list = []
            for item in itemsOnMarket.filter(tType=tType):
                item.stockI = inventory.get("inventory", {}).get(str(item.tId), [0, 0])[0]
                item.stockB = inventory.get("bazaar", {}).get(str(item.tId), [0, 0])[0]
                item.stockBP = inventory.get("bazaar", {}).get(str(item.tId), [0, 0])[1]
                item.stockD = inventory.get("display", {}).get(str(item.tId), [0, 0])[0]
                item.stock = item.stockI + item.stockB + item.stockD
                item_list.append(item)
            items.append((tType, item_list))

        context = {
            "player": player,
            'list': json.loads(player.bazaarList),
            "bazaarcat": True,
            "allItemsOnMarket": items,
            "view": {"refreshType": True, "timer": True, "hideType": True, "loopType": True},
            "keyLevelRequired": 2
        }
        if error:
            context.update(error)
        page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
        return render(request, page, context)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def sets(request):
    try:
        player = getPlayer(request.session.get("player", {}).get("tId", -1))

        # get items
        allItems = Item.objects.all().order_by('tName')
        tTypes = ["Flower", "Plushie"]
        sets = {
            "Plushie set": {
                "ids": [186, 187, 215, 258, 261, 266, 268, 269, 273, 274, 281, 384, 618],
                "type": "Plushie",
                "items": [],
                "quantities": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                "points": 10,
                "market_value": 0,
            },
            "Exotic flower set": {
                "ids": [260, 263, 264, 267, 271, 272, 276, 277, 282, 385, 617],
                "type": "Flower",
                "items": [],
                "quantities": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                "points": 10,
                "market_value": 0,
            },
            "Medieval coin set": {
                "ids": [450, 451, 452],
                "type": "Coins",
                "items": [],
                "quantities": [1, 1, 1],
                "points": 100,
                "market_value": 0,
            },
            "Quran Scripts set": {
                "ids": [455, 456, 457],
                "type": "Scripts",
                "items": [],
                "quantities": [1, 1, 1],
                "points": 1000,
                "market_value": 0,
            },
            "Senet game set": {
                "ids": [460, 461, 462],
                "type": "Senet",
                "items": [],
                "quantities": [5, 5, 1],
                "points": 2000,
                "market_value": 0,
            },
            "Vairocana Buddha": {
                "ids": [454],
                "type": "Vairocana",
                "items": [],
                "quantities": [1],
                "points": 100,
                "market_value": 0,
            },
            "Ganesha Sculpture": {
                "ids": [453],
                "type": "Ganesha",
                "items": [],
                "quantities": [1],
                "points": 250,
                "market_value": 0,
            },
            "Shabti Sculpture": {
                "ids": [458],
                "type": "Shabti",
                "items": [],
                "quantities": [1],
                "points": 500,
                "market_value": 0,
            },
            "Egyptian Amulet": {
                "ids": [459],
                "type": "Egyptian",
                "items": [],
                "quantities": [1],
                "points": 10000,
                "market_value": 0,
            },
        }


        # get/update inventory
        inventory = player.getInventory()
        error = inventory if 'apiError' in inventory else False
        point_value = BazaarData.objects.first().pointsValue

        for tType, set in sets.items():
            for item in allItems.filter(tId__in=set.get('ids', [])):
                item.stockI = inventory.get("inventory", {}).get(str(item.tId), [0, 0])[0]
                item.stockB = inventory.get("bazaar", {}).get(str(item.tId), [0, 0])[0]
                item.stockBP = inventory.get("bazaar", {}).get(str(item.tId), [0, 0])[1]
                item.stockD = inventory.get("display", {}).get(str(item.tId), [0, 0])[0]
                item.stock = item.stockI + item.stockB + item.stockD
                set["items"].append(item)
                set["market_value"] += set["quantities"][set["ids"].index(item.tId)] * item.tMarketValue
                # item.save()
            set["points_value"] = point_value * set["points"]
            set["benefits"] = set["points_value"] - set["market_value"]
            set["benefitsps"] = 100 * (set["points_value"] - set["market_value"]) / set["points_value"]


        context = {
            "player": player,
            'list': json.loads(player.bazaarList),
            "bazaarcat": True,
            "sets": sets,
            "view": {"refreshType": True, "timer": True, "loopSets": True},
            "keyLevelRequired": 2
        }
        if error:
            context.update(error)
        page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
        return render(request, page, context)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def all(request):
    try:
        player = getPlayer(request.session.get("player", {}).get("tId", -1))

        # get items
        itemsOnMarket = Item.objects.all().order_by('tName')
        tTypes = {r["tType"] for r in itemsOnMarket.values("tType").distinct()}
        items = []

        # get/update inventory
        inventory = player.getInventory()
        error = inventory if 'apiError' in inventory else False

        # build item list
        for tType in tTypes:
            item_list = []
            for item in itemsOnMarket.filter(tType=tType):
                item.stockI = inventory.get("inventory", {}).get(str(item.tId), [0, 0])[0]
                item.stockB = inventory.get("bazaar", {}).get(str(item.tId), [0, 0])[0]
                item.stockBP = inventory.get("bazaar", {}).get(str(item.tId), [0, 0])[1]
                item.stockD = inventory.get("display", {}).get(str(item.tId), [0, 0])[0]
                item.stock = item.stockI + item.stockB + item.stockD
                item_list.append(item)
            items.append((tType, item_list))

        context = {
            "player": player,
            'list': json.loads(player.bazaarList),
            "bazaarcat": True,
            "allItemsOnMarket": items,
            "view": {"hideType": True, "loopType": True},
            "keyLevelRequired": 2
        }
        if error:
            context.update(error)
        page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
        return render(request, page, context)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def top10(request):
    try:
        player = getPlayer(request.session.get("player", {}).get("tId", -1))

        # get items
        items = []

        # get/update inventory
        inventory = player.getInventory()
        error = inventory if 'apiError' in inventory else False

        # build item list
        item_list = []
        for item in Item.objects.filter(onMarket=True).order_by('weekTendency')[:10]:
            item.stockI = inventory.get("inventory", {}).get(str(item.tId), [0, 0])[0]
            item.stockB = inventory.get("bazaar", {}).get(str(item.tId), [0, 0])[0]
            item.stockBP = inventory.get("bazaar", {}).get(str(item.tId), [0, 0])[1]
            item.stockD = inventory.get("display", {}).get(str(item.tId), [0, 0])[0]
            item.stock = item.stockI + item.stockB + item.stockD
            item_list.append(item)
        items.append(('Buy', item_list))

        item_list = []
        for item in Item.objects.filter(onMarket=True).order_by('-weekTendency')[:10]:
            item.stockI = inventory.get("inventory", {}).get(str(item.tId), [0, 0])[0]
            item.stockB = inventory.get("bazaar", {}).get(str(item.tId), [0, 0])[0]
            item.stockBP = inventory.get("bazaar", {}).get(str(item.tId), [0, 0])[1]
            item.stockD = inventory.get("display", {}).get(str(item.tId), [0, 0])[0]
            item.stock = item.stockI + item.stockB + item.stockD
            item_list.append(item)
        items.append(('Sell', item_list))

        context = {
            "player": player,
            'list': json.loads(player.bazaarList),
            "bazaarcat": True,
            "allItemsOnMarket": items,
            "view": {"refreshType": True, "timer": True, "loopType": True},
            "keyLevelRequired": 2
        }
        if error:
            context.update(error)
        page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
        return render(request, page, context)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def details(request, itemId=168):
    try:
        if request.method == "POST":
            item = Item.objects.filter(tId=itemId).first()

            context = {'item': item}
            return render(request, 'bazaar/details.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def prices(request):
    try:
        if request.method == "POST":
            itemId = request.POST['item_id']
            item = Item.objects.filter(tId=itemId).first()

            # create price histogram
            priceHistory = sorted(json.loads(item.priceHistory).items(), key=lambda x: x[0])
            # plot only last 8 points of the Tendency
            graph = [[t, p, item.weekTendencyA * float(t) + item.weekTendencyB, item.monthTendencyA * float(t) + item.monthTendencyB] for t, p in priceHistory]
            graphLength = 0
            maxTS = priceHistory[-1][0]
            for i, (t, p, wt, mt) in enumerate(graph):
                if not int(p):
                    graph[i][1] = "null"
                    # graph[i][2] = "null"
                    # graph[i][3] = "null"
                else:
                    graphLength += 1
                if int(maxTS) - int(t) > 3600 * 24 * 7 or wt < 0:
                    graph[i][2] = "null"
                if int(maxTS) - int(t) > 3600 * 24 * 31 or mt < 0:
                    graph[i][3] = "null"

                # convert timestamp to date
                graph[i][0] = timestampToDate(int(t))

            context = {'item': item, "graph": graph, "graphLength": graphLength}
            return render(request, 'bazaar/prices.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def update(request, itemId=168):
    try:
        if request.session.get('player') and request.method == "POST":
            player = getPlayer(request.session.get("player", {}).get("tId", -1))
            key = player.getKey()

            item = Item.objects.filter(tId=itemId).first()
            baz = item.update_bazaar(key=key, n=BazaarData.objects.first().nItems)
            error = baz if 'apiError' in baz else False

            # get/update inventory
            inventory = player.getInventory()
            item.stockI = inventory.get("inventory", {}).get(str(item.tId), [0, 0])[0]
            item.stockB = inventory.get("bazaar", {}).get(str(item.tId), [0, 0])[0]
            item.stockBP = inventory.get("bazaar", {}).get(str(item.tId), [0, 0])[1]
            item.stockD = inventory.get("display", {}).get(str(item.tId), [0, 0])[0]
            item.stock = item.stockI + item.stockB + item.stockD

            context = {'player': player, 'list': json.loads(player.bazaarList), 'item': item, "view": {"timer": True}}
            if error:
                context.update(error)
            return render(request, "bazaar/item.html", context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def delete(request, itemId):
    try:
        if request.session.get('player') and request.method == "POST":

            item = Item.objects.filter(tId=itemId).first()
            item.lastUpdateTS = 0
            item.marketdata_set.all().delete()
            item.save()

            context = {'item': item, "view": {"timer": True}}
            return render(request, "bazaar/item.html", context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def toggle(request, itemId):
    try:
        if request.session.get('player') and request.method == "POST":
            player = getPlayer(request.session.get("player", {}).get("tId", -1))
            playerList = json.loads(player.bazaarList)

            item = Item.objects.filter(tId=itemId).first()
            if itemId in playerList:
                playerList.remove(itemId)
            else:
                playerList.append(itemId)
            player.bazaarList = json.dumps(playerList)
            player.bazaarInfo = len(playerList)
            player.save()

            # get/update inventory
            inventory = player.getInventory()
            item.stockI = inventory.get("inventory", {}).get(str(item.tId), [0, 0])[0]
            item.stockB = inventory.get("bazaar", {}).get(str(item.tId), [0, 0])[0]
            item.stockBP = inventory.get("bazaar", {}).get(str(item.tId), [0, 0])[1]
            item.stockD = inventory.get("display", {}).get(str(item.tId), [0, 0])[0]
            item.stock = item.stockI + item.stockB + item.stockD

            context = {'player': player, 'item': item, 'list': json.loads(player.bazaarList), "view": {"timer": True}}
            return render(request, "bazaar/item.html", context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


# @cache_page(60)
def abroad(request):
    try:
        # build up filters list
        from bazaar.countries import countries as country_list
        from bazaar.countries import types as type_list
        country_list["all"] = {"name": "All", "n": 0}
        type_list["all"] = {"name": "All", "n": 0}

        # get player and page
        player = getPlayer(request.session.get("player", {}).get("tId", -1))
        page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"

        # get filters
        filters = request.session.get('stocks-filters', {"countries": "all", "types": ["all"]})
        if not isinstance(filters["types"], list):
            filters["types"] = ["all"]

        # set filters
        if request.POST.get("filter", False) and request.POST.get("key"):
            page = "bazaar/abroad/list.html"
            post_filter = request.POST.get("filter")
            post_key = request.POST.get("key")

            if post_filter in "types" and post_key in type_list:
                if post_key != "all":
                    if "all" in filters[post_filter]:
                        filters[post_filter].remove("all")
                    if post_key in filters[post_filter]:
                        filters[post_filter].remove(post_key)
                    else:
                        filters[post_filter].append(post_key)
                if not len(filters[post_filter]) or post_key == "all":
                    filters[post_filter] = ["all"]

            elif post_filter in "countries" and post_key in country_list:
                filters[post_filter] = post_key if post_key != filters[post_filter] else "all"

        request.session["stocks-filters"] = filters

        # old stocks
        old = tsnow() - 48 * 3600
        AbroadStocks.objects.filter(timestamp__lt=old).delete()
        stocks = AbroadStocks.objects.filter(last=True)
        bd = BazaarData.objects.first()
        if bd is None:
            clients = {}
        else:
            clients = json.loads(bd.clientsStats)

        if filters["countries"] != "all":
            stocks = stocks.filter(country_key=filters["countries"])
        if "all" not in filters["types"]:
            stocks = stocks.filter(item__tType__in=filters["types"])

        # add fields
        for stock in stocks:
            stock.profit = stock.item.tMarketValue - stock.cost
            stock.profitperhour = round(30 * stock.profit / stock.get_country()["fly_time"])
            stock.update = tsnow() - stock.timestamp

        context = {"player": player,
                   "filters": filters,
                   "country_list": country_list,
                   "type_list": type_list,
                   "stocks": stocks,
                   "clients": sorted(clients.items(), key=lambda x: -x[1][0]),
                   "bazaarcat": True,
                   "view": {"abroad": True}}

        return render(request, page, context)

    except Exception as e:
        del request.session["stocks-filters"]
        return returnError(exc=e, session=request.session)


def abroadStocks(request):
    try:
        if request.method == "POST":
            item_id = request.POST.get('item_id', False)
            country_key = request.POST.get('country_key', False)
            old = tsnow() - 48 * 3600
            stocks = AbroadStocks.objects.filter(country_key=country_key, item__tId=item_id, timestamp__gt=old).order_by("-timestamp")

            if stocks is None:
                context = {'item': None, "graph": []}
                return render(request, 'bazaar/abroad/graph.html', context)

            # # get clients statistics
            # clients = dict({})
            # for stock in stocks:
            #     if stock.client == "":
            #         continue
            #     if stock.client not in clients:
            #         clients[stock.client] = 0
            #     clients[stock.client] += 1
            #
            # clients = {c: [i, n] for i, (c, n) in enumerate(sorted(clients.items(), key=lambda x: -x[1]))}

            # graph = [[timestampToDate(s.timestamp), s.quantity, s.cost, s.client, clients.get(s.client)[0], clients.get(s.client)[1]] for s in stocks]

            # # average the prices
            # floatTS = stocks.first().timestamp
            # avg_val = [0, 0, 0]  # ts, quantity, cost
            # n = 0
            # graph = []
            # for s in stocks:
            #     n += 1
            #     avg_val[0] += s.timestamp
            #     avg_val[1] += s.quantity
            #     if (floatTS - s.timestamp) > 5 * 60:
            #         floatTS = s.timestamp
            #         line = [timestampToDate(avg_val[0] // n), avg_val[1] // n, avg_val[2] // n]
            #         graph.append(line)
            #         avg_val = [0, 0, 0]
            #         n = 0
            #
            # # record last point
            # if n > 0:
            #     line = [timestampToDate(avg_val[0] // n), avg_val[1] // n, avg_val[2] // n]
            #     graph.append(line)

            graph = [[timestampToDate(s.timestamp), s.quantity, s.cost] for s in stocks]

            stock = stocks.first()
            context = {'stock': stocks.first(),
                       'graph': graph,
                       'x': [timestampToDate(tsnow() - 48 * 3600),
                             timestampToDate(tsnow() - 24 * 3600),
                             timestampToDate(tsnow())]}
            return render(request, 'bazaar/abroad/graph.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)
