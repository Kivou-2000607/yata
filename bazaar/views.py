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

import json

from bazaar.models import Item
from bazaar.models import BazaarData
from player.models import Player
from yata.handy import apiCall
from yata.handy import returnError
from yata.handy import timestampToDate


def index(request):
    try:
        if request.session.get('player'):
            print('[view.bazaar.index] get player id from session')
            tId = request.session["player"].get("tId")
        else:
            print('[view.bazaar.index] anon session')
            tId = -1

        player = Player.objects.filter(tId=tId).first()
        player.lastActionTS = int(timezone.now().timestamp())
        player.active = True
        key = player.getKey()
        bazaarJson = json.loads(player.bazaarJson)
        playerList = bazaarJson.get("list", [])
        player.bazaarInfo = "{}".format(len(playerList))

        # update inventory of bazaarJson
        error = False
        if tId > 0:
            invtmp = apiCall("user", "", "inventory,display,bazaar", key)
            for k, v in invtmp.items():
                if v is None:
                    invtmp[k] = dict({})
            if 'apiError' in invtmp:
                error = invtmp
            else:
                bazaarJson["inventory"] = {str(v["ID"]): v["quantity"] for v in invtmp.get("inventory", dict({}))}
                bazaarJson["bazaar"] = {str(v["ID"]): v["quantity"] for v in invtmp.get("bazaar", dict({}))}
                bazaarJson["display"] = {str(v["ID"]): v["quantity"] for v in invtmp.get("display", dict({}))}
                player.bazaarJson = json.dumps(bazaarJson)

        player.save()

        print('[view.bazaar.default] get all items on market')
        itemsOnMarket = Item.objects.filter(onMarket=True).order_by('tName')
        print('[view.bazaar.default] get all tTypes')
        tTypes = [r["tType"] for r in itemsOnMarket.values("tType").distinct()]
        # print('[view.bazaar.default] {}'.format(tTypes))
        print('[view.bazaar.default] create output items')
        items = {tType: [] for tType in tTypes}

        inventory = bazaarJson.get("inventory", dict({}))
        bazaar = bazaarJson.get("bazaar", dict({}))
        display = bazaarJson.get("display", dict({}))
        for tType in items:
            for item in itemsOnMarket.filter(tType=tType):
                item.stockI = inventory.get(str(item.tId), 0)
                item.stockB = bazaar.get(str(item.tId), 0)
                item.stockD = display.get(str(item.tId), 0)
                item.stock = item.stockI + item.stockB + item.stockD
                items[tType].append(item)
                # item.save()

        context = {"player": player, 'list': playerList, "bazaarcat": True, "allItemsOnMarket": items, "view": {"refreshType": True, "timer": True, "hideType": True}}
        if error:
            context.update(error)
        return render(request, 'bazaar.html', context)

        # else:
        #     return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


def custom(request):
    try:
        if request.session.get('player'):
            print('[view.bazaar.default] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            player.save()

            bazaarJson = json.loads(player.bazaarJson)
            playerList = bazaarJson.get("list", [])

            print('[view.bazaar.default] get all items on player\'s list')
            itemsOnMarket = Item.objects.filter(tId__in=playerList).order_by('tName')
            print('[view.bazaar.default] create output items')
            items = {"Custom": []}

            inventory = bazaarJson.get("inventory", dict({}))
            bazaar = bazaarJson.get("bazaar", dict({}))
            display = bazaarJson.get("display", dict({}))
            for item in itemsOnMarket:
                item.stockI = inventory.get(str(item.tId), 0)
                item.stockB = bazaar.get(str(item.tId), 0)
                item.stockD = display.get(str(item.tId), 0)
                item.stock = item.stockI + item.stockB + item.stockD
                items["Custom"].append(item)
                # item.save()

            context = {"player": player, 'list': playerList, "bazaarcat": True, "allItemsOnMarket": items, "view": {"refreshType": True, "timer": True}}
            page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
            return render(request, page, context)
        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


def default(request):
    try:
        if request.session.get('player'):
            print('[view.bazaar.default] get player id from session')
            tId = request.session["player"].get("tId")
        else:
            print('[view.bazaar.default] anon session')
            tId = -1

        player = Player.objects.filter(tId=tId).first()
        player.lastActionTS = int(timezone.now().timestamp())
        player.save()

        bazaarJson = json.loads(player.bazaarJson)
        playerList = bazaarJson.get("list", [])

        print('[view.bazaar.default] get all items on market')
        itemsOnMarket = Item.objects.filter(onMarket=True).order_by('tName')
        print('[view.bazaar.default] get all tTypes')
        tTypes = [r["tType"] for r in itemsOnMarket.values("tType").distinct()]
        # print('[view.bazaar.default] {}'.format(tTypes))
        print('[view.bazaar.default] create output items')
        items = {tType: [] for tType in tTypes}

        inventory = bazaarJson.get("inventory", dict({}))
        bazaar = bazaarJson.get("bazaar", dict({}))
        display = bazaarJson.get("display", dict({}))
        for tType in items:
            for item in itemsOnMarket.filter(tType=tType):
                item.stockI = inventory.get(str(item.tId), 0)
                item.stockB = bazaar.get(str(item.tId), 0)
                item.stockD = display.get(str(item.tId), 0)
                item.stock = item.stockI + item.stockB + item.stockD
                items[tType].append(item)
                # item.save()

        context = {"player": player, 'list': playerList, "bazaarcat": True, "allItemsOnMarket": items, "view": {"refreshType": True, "timer": True, "hideType": True}}
        page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
        return render(request, page, context)

    except Exception:
        return returnError()


def sets(request):
    try:
        if request.session.get('player'):
            print('[view.bazaar.sets] get player id from session')
            tId = request.session["player"].get("tId")
        else:
            print('[view.bazaar.sets] anon session')
            tId = -1

        player = Player.objects.filter(tId=tId).first()
        player.lastActionTS = int(timezone.now().timestamp())
        player.save()

        bazaarJson = json.loads(player.bazaarJson)
        playerList = bazaarJson.get("list", [])

        print('[view.bazaar.default] get all items on market')
        itemsOnMarket = Item.objects.filter(onMarket=True).order_by('tName')
        print('[view.bazaar.default] get all tTypes')
        tTypes = ["Flower", "Plushie"]
        # print('[view.bazaar.default] {}'.format(tTypes))
        print('[view.bazaar.default] create output items')
        items = {tType: [] for tType in tTypes}

        inventory = bazaarJson.get("inventory", dict({}))
        bazaar = bazaarJson.get("bazaar", dict({}))
        display = bazaarJson.get("display", dict({}))
        for tType in items:
            for item in itemsOnMarket.filter(tType=tType):
                item.stockI = inventory.get(str(item.tId), 0)
                item.stockB = bazaar.get(str(item.tId), 0)
                item.stockD = display.get(str(item.tId), 0)
                item.stock = item.stockI + item.stockB + item.stockD
                items[tType].append(item)
                # item.save()

        context = {"player": player, 'list': playerList, "bazaarcat": True, "allItemsOnMarket": items, "view": {"refreshType": True, "timer": True}}
        page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
        return render(request, page, context)

    except Exception:
        return returnError()


def all(request):
    try:
        if request.session.get('player'):
            print('[view.bazaar.all] get player id from session')
            tId = request.session["player"].get("tId")
        else:
            print('[view.bazaar.all] anon session')
            tId = -1

        player = Player.objects.filter(tId=tId).first()
        player.lastActionTS = int(timezone.now().timestamp())
        player.save()

        bazaarJson = json.loads(player.bazaarJson)
        playerList = bazaarJson.get("list", [])

        print('[view.bazaar.default] get all items on market')
        itemsOnMarket = Item.objects.all().order_by('tName')
        print('[view.bazaar.default] get all tTypes')
        tTypes = [r["tType"] for r in itemsOnMarket.values("tType").distinct()]
        # print('[view.bazaar.default] {}'.format(tTypes))
        print('[view.bazaar.default] create output items')
        items = {tType: [] for tType in tTypes}

        inventory = bazaarJson.get("inventory", dict({}))
        bazaar = bazaarJson.get("bazaar", dict({}))
        display = bazaarJson.get("display", dict({}))
        for tType in items:
            for item in itemsOnMarket.filter(tType=tType):
                item.stockI = inventory.get(str(item.tId), 0)
                item.stockB = bazaar.get(str(item.tId), 0)
                item.stockD = display.get(str(item.tId), 0)
                item.stock = item.stockI + item.stockB + item.stockD
                items[tType].append(item)
                # item.save()

        context = {"player": player, 'list': playerList, "bazaarcat": True, "allItemsOnMarket": items, "view": {"hideType": True}}
        page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
        return render(request, page, context)

    except Exception:
        return returnError()


def top10(request):
    try:
        if request.session.get('player'):
            print('[view.bazaar.top10] get player id from session')
            tId = request.session["player"].get("tId")
        else:
            print('[view.bazaar.top10] anon session')
            tId = -1

        player = Player.objects.filter(tId=tId).first()
        player.lastActionTS = int(timezone.now().timestamp())
        player.save()

        bazaarJson = json.loads(player.bazaarJson)
        playerList = bazaarJson.get("list", [])

        print('[view.bazaar.default] create output items')
        items = {"Sell": [], "Buy": []}

        inventory = bazaarJson.get("inventory", dict({}))
        bazaar = bazaarJson.get("bazaar", dict({}))
        display = bazaarJson.get("display", dict({}))
        for item in Item.objects.all().order_by('weekTendency')[:10]:
            item.stockI = inventory.get(str(item.tId), 0)
            item.stockB = bazaar.get(str(item.tId), 0)
            item.stockD = display.get(str(item.tId), 0)
            item.stock = item.stockI + item.stockB + item.stockD
            items["Buy"].append(item)
            # item.save()
        for item in Item.objects.all().order_by('-weekTendency')[:10]:
            item.stockI = inventory.get(str(item.tId), 0)
            item.stockB = bazaar.get(str(item.tId), 0)
            item.stockD = display.get(str(item.tId), 0)
            item.stock = item.stockI + item.stockB + item.stockD
            items["Sell"].append(item)
            # item.save()

        context = {"player": player, 'list': playerList, "bazaarcat": True, "allItemsOnMarket": items, "view": {"refreshType": True, "timer": True}}
        page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
        return render(request, page, context)

    except Exception:
        return returnError()


def details(request, itemId):
    try:
        if request.method == "POST":
            item = Item.objects.filter(tId=itemId).first()

            context = {'item': item}
            return render(request, 'bazaar/details.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


def prices(request, itemId):
    try:
        if request.method == "POST":
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

    except Exception:
        return returnError()


def update(request, itemId):
    try:
        if request.session.get('player') and request.method == "POST":
            print('[view.bazaar.updateItem] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            key = player.getKey()
            bazaarJson = json.loads(player.bazaarJson)
            playerList = bazaarJson.get("list", [])

            print('[view.bazaar.updateItem] get item')
            item = Item.objects.filter(tId=itemId).first()
            print('[view.bazaar.updateItem] {}'.format(item))

            baz = item.update_bazaar(key=key, n=BazaarData.objects.first().nItems)
            error = False
            if 'apiError' in baz:
                error = baz

            # update inventory of bazaarJson
            error = False
            invtmp = apiCall("user", "", "inventory,display,bazaar", key)
            for k, v in invtmp.items():
                if v is None:
                    invtmp[k] = dict({})
            if 'apiError' in invtmp:
                error = {"apiErrorSub": invtmp["apiError"]}
            else:
                # modify user
                bazaarJson["inventory"] = {str(v["ID"]): v["quantity"] for v in invtmp.get("inventory", dict({}))}
                bazaarJson["bazaar"] = {str(v["ID"]): v["quantity"] for v in invtmp.get("bazaar", dict({}))}
                bazaarJson["display"] = {str(v["ID"]): v["quantity"] for v in invtmp.get("display", dict({}))}
                item.stockI = bazaarJson["inventory"].get(str(item.tId), 0)
                item.stockB = bazaarJson["bazaar"].get(str(item.tId), 0)
                item.stockD = bazaarJson["display"].get(str(item.tId), 0)
                item.stock = item.stockI + item.stockB + item.stockD
                # item.save()

            player.bazaarJson = json.dumps(bazaarJson)
            player.save()

            context = {'player': player, 'list': playerList, 'item': item, "view": {"timer": True}}
            if error:
                context.update(error)
            return render(request, "bazaar/item.html", context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


def delete(request, itemId):
    try:
        if request.session.get('player') and request.method == "POST":

            print('[view.bazaar.deleteItem] delete item')
            item = Item.objects.filter(tId=itemId).first()
            item.lastUpdateTS = 0
            item.marketdata_set.all().delete()
            item.save()

            context = {'item': item, "view": {"timer": True}}
            return render(request, "bazaar/item.html", context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


def toggle(request, itemId):
    try:
        if request.session.get('player') and request.method == "POST":
            print('[view.bazaar.updateItem] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            bazaarJson = json.loads(player.bazaarJson)
            playerList = bazaarJson.get("list", [])

            item = Item.objects.filter(tId=itemId).first()
            if itemId in playerList:
                playerList.remove(itemId)
            else:
                playerList.append(itemId)

            item.stockI = bazaarJson["inventory"].get(str(item.tId), 0)
            item.stockB = bazaarJson["bazaar"].get(str(item.tId), 0)
            item.stockD = bazaarJson["display"].get(str(item.tId), 0)
            item.stock = item.stockI + item.stockB + item.stockD

            bazaarJson["list"] = playerList
            player.bazaarJson = json.dumps(bazaarJson)
            player.save()

            context = {'player': player, 'item': item, 'list': playerList, "view": {"timer": True}}
            return render(request, "bazaar/item.html", context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()
