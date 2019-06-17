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
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.http import HttpResponseServerError
from django.template.loader import render_to_string

import json
import traceback
import time

from bazaar.models import Preference
from bazaar.models import Item
from player.models import Player
from yata.handy import apiCall


def index(request):
    try:
        if request.session.get('player'):
            print('[view.bazaar.index] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())

            key = player.key
            bazaarJson = json.loads(player.bazaarJson)

            # update inventory of bazaarJson
            error = False
            invtmp = apiCall("user", "", "inventory", key, sub="inventory")
            if 'apiError' in invtmp:
                error = invtmp
            else:
                bazaarJson["inventory"] = {str(v["ID"]): v["quantity"] for v in invtmp}
                player.bazaarJson = json.dumps(bazaarJson)

            playerList = bazaarJson.get("list", [])
            player.bazaarInfo = "{}".format(len(playerList))
            player.save()

            print('[view.bazaar.default] get all items on market')
            itemsOnMarket = Item.objects.filter(onMarket=True)
            print('[view.bazaar.default] get all tTypes')
            tTypes = [r["tType"] for r in itemsOnMarket.values("tType").distinct()]
            print('[view.bazaar.default] {}'.format(tTypes))
            print('[view.bazaar.default] create output items')
            items = {tType: [] for tType in tTypes}

            inventory = bazaarJson.get("inventory", dict({}))
            for tType in items:
                for item in itemsOnMarket.filter(tType=tType):
                    item.stock = inventory.get(str(item.tId), 0)
                    items[tType].append(item)
                    # item.save()

            context = {"player": player, "bazaarcat": True, "allItemsOnMarket": items, "view": {"refreshType": True, "timer": True, "hideType": True}}
            if error:
                context.update(error)
            return render(request, 'bazaar.html', context)

        else:
            return HttpResponseServerError(render_to_string('403.html', {'exception': "You might want to log in."}))

    except Exception:
        print("[{:%d/%b/%Y %H:%M:%S}] ERROR 500 \n{}".format(timezone.now(), traceback.format_exc()))
        return HttpResponseServerError(render_to_string('500.html', {'exception': traceback.format_exc().strip()}))


def custom(request):
    try:
        if request.session.get('player'):
            print('[view.bazaar.default] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            player.save()

            # key = player.key
            bazaarJson = json.loads(player.bazaarJson)
            inventory = bazaarJson.get("inventory", dict({}))
            playerList = bazaarJson.get("list", [])

            print('[view.bazaar.default] get all items on player\'s list')
            itemsOnMarket = Item.objects.filter(tId__in=playerList)
            print('[view.bazaar.default] create output items')
            items = {"Custom": []}

            for item in itemsOnMarket:
                item.stock = inventory.get(str(item.tId), 0)
                items["Custom"].append(item)
                # item.save()

            context = {"player": player, "bazaarcat": True, "allItemsOnMarket": items, "view": {"refreshType": True, "timer": True}}
            page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
            return render(request, page, context)
        else:
            return HttpResponseServerError(render_to_string('403.html', {'exception': "You might want to log in."}))

    except Exception:
        print("[{:%d/%b/%Y %H:%M:%S}] ERROR 500 \n{}".format(timezone.now(), traceback.format_exc()))
        return HttpResponseServerError(render_to_string('500.html', {'exception': traceback.format_exc().strip()}))


def default(request):
    try:
        if request.session.get('player'):
            print('[view.bazaar.default] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            player.save()

            # key = player.key
            bazaarJson = json.loads(player.bazaarJson)
            # playerList = bazaarJson.get("list", [])

            print('[view.bazaar.default] get all items on market')
            itemsOnMarket = Item.objects.filter(onMarket=True)
            print('[view.bazaar.default] get all tTypes')
            tTypes = [r["tType"] for r in itemsOnMarket.values("tType").distinct()]
            print('[view.bazaar.default] {}'.format(tTypes))
            print('[view.bazaar.default] create output items')
            items = {tType: [] for tType in tTypes}

            inventory = bazaarJson.get("inventory", dict({}))
            for tType in items:
                for item in itemsOnMarket.filter(tType=tType):
                    item.stock = inventory.get(str(item.tId), 0)
                    items[tType].append(item)
                    # item.save()

            context = {"player": player, "bazaarcat": True, "allItemsOnMarket": items, "view": {"refreshType": True, "timer": True, "hideType": True}}
            page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
            return render(request, page, context)
        else:
            return HttpResponseServerError(render_to_string('403.html', {'exception': "You might want to log in."}))

    except Exception:
        print("[{:%d/%b/%Y %H:%M:%S}] ERROR 500 \n{}".format(timezone.now(), traceback.format_exc()))
        return HttpResponseServerError(render_to_string('500.html', {'exception': traceback.format_exc().strip()}))


def sets(request):
    try:
        if request.session.get('player'):
            print('[view.bazaar.default] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            player.save()

            # key = player.key
            bazaarJson = json.loads(player.bazaarJson)
            inventory = bazaarJson.get("inventory", dict({}))
            # playerList = bazaarJson.get("list", [])

            print('[view.bazaar.default] get all items on market')
            itemsOnMarket = Item.objects.filter(onMarket=True)
            print('[view.bazaar.default] get all tTypes')
            tTypes = ["Flower", "Plushie"]
            print('[view.bazaar.default] {}'.format(tTypes))
            print('[view.bazaar.default] create output items')
            items = {tType: [] for tType in tTypes}

            for tType in items:
                for item in itemsOnMarket.filter(tType=tType):
                    print(item)
                    item.stock = inventory.get(str(item.tId), 0)
                    items[tType].append(item)
                    # item.save()

            context = {"player": player, "bazaarcat": True, "allItemsOnMarket": items, "view": {"refreshType": True, "timer": True}}
            page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
            return render(request, page, context)
        else:
            return HttpResponseServerError(render_to_string('403.html', {'exception': "You might want to log in."}))

    except Exception:
        print("[{:%d/%b/%Y %H:%M:%S}] ERROR 500 \n{}".format(timezone.now(), traceback.format_exc()))
        return HttpResponseServerError(render_to_string('500.html', {'exception': traceback.format_exc().strip()}))


def all(request):
    try:
        if request.session.get('player'):
            print('[view.bazaar.default] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            player.save()

            # key = player.key
            bazaarJson = json.loads(player.bazaarJson)
            inventory = bazaarJson.get("inventory", dict({}))
            # playerList = bazaarJson.get("list", [])

            print('[view.bazaar.default] get all items on market')
            itemsOnMarket = Item.objects.all()
            print('[view.bazaar.default] get all tTypes')
            tTypes = [r["tType"] for r in itemsOnMarket.values("tType").distinct()]
            print('[view.bazaar.default] {}'.format(tTypes))
            print('[view.bazaar.default] create output items')
            items = {tType: [] for tType in tTypes}

            for tType in items:
                for item in itemsOnMarket.filter(tType=tType):
                    item.stock = inventory.get(str(item.tId), 0)
                    items[tType].append(item)
                    # item.save()

            context = {"player": player, "bazaarcat": True, "allItemsOnMarket": items, "view": {"hideType": True}}
            page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
            return render(request, page, context)
        else:
            return HttpResponseServerError(render_to_string('403.html', {'exception': "You might want to log in."}))

    except Exception:
        print("[{:%d/%b/%Y %H:%M:%S}] ERROR 500 \n{}".format(timezone.now(), traceback.format_exc()))
        return HttpResponseServerError(render_to_string('500.html', {'exception': traceback.format_exc().strip()}))


def details(request, itemId):
    try:
        if request.session.get('player') and request.method == "POST":
            item = Item.objects.filter(tId=itemId).first()

            context = {'item': item}
            return render(request, 'bazaar/details.html', context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return HttpResponseServerError(render_to_string('403.html', {'exception': message}))

    except Exception:
        print("[{:%d/%b/%Y %H:%M:%S}] ERROR 500 \n{}".format(timezone.now(), traceback.format_exc()))
        return HttpResponseServerError(render_to_string('500.html', {'exception': traceback.format_exc().strip()}))


def update(request, itemId):
    try:
        if request.session.get('player') and request.method == "POST":
            print('[view.bazaar.updateItem] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            key = player.key
            bazaarJson = json.loads(player.bazaarJson)

            print('[view.bazaar.updateItem] get item')
            item = Item.objects.filter(tId=itemId).first()
            print('[view.bazaar.updateItem] {}'.format(item))

            baz = item.update_bazaar(key=key, n=Preference.objects.first().nItems)
            error = False
            if 'apiError' in baz:
                error = baz

            # update inventory of bazaarJson
            error = False
            invtmp = apiCall("user", "", "inventory", key, sub="inventory")
            if 'apiError' in invtmp:
                error = {"apiErrorSub": invtmp["apiError"]}
            else:
                # modify user
                bazaarJson["inventory"] = {str(v["ID"]): v["quantity"] for v in invtmp}
                item.stock = bazaarJson["inventory"].get(str(itemId), 0)
                item.save()

            player.bazaarJson = json.dumps(bazaarJson)
            player.save()

            context = {'item': item, "view": {"timer": True}}
            if error:
                context.update(error)
            return render(request, "bazaar/item.html", context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return HttpResponseServerError(render_to_string('403.html', {'exception': message}))

    except Exception:
        print("[{:%d/%b/%Y %H:%M:%S}] ERROR 500 \n{}".format(timezone.now(), traceback.format_exc()))
        return HttpResponseServerError(render_to_string('500.html', {'exception': traceback.format_exc().strip()}))


def updateType(request, tType):
    try:
        if request.method == "POST":
            print('[view.bazaar.updateItem] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            key = player.key
            nItems = Preference.objects.all()[0].nItems
            bazaarJson = json.loads(player.bazaarJson)
            inventory = bazaarJson.get("inventory", dict({}))
            playerList = bazaarJson.get("list", [])

            if tType == "Custom":
                items = Item.objects.filter(tId__in=playerList)
            else:
                items = Item.objects.filter(onMarket=True).filter(tType=tType)

            itemsAPI = apiCall("torn", "", "items", key, sub='items')
            error = False
            if 'apiError' in itemsAPI:
                error = {"apiErrorSub": itemsAPI["apiError"]}
                for item in items:
                    item.stock = inventory.get(item.tId, 0)
            else:
                for item in items:
                    print("[VIEW updateTypeBazaar]: update ", item)
                    item.update(itemsAPI[str(item.tId)])
                    item.update_bazaar(key=key, n=nItems)
                    item.save()
                    item.stock = inventory.get(item.tId, 0)

            player.bazaarJson = json.dumps(bazaarJson)
            player.save()

            context = {"itemType": tType, "items": items, "view": {"refreshType": True, "timer": True}}
            if error:
                context.update(error)
            return render(request, "bazaar/loop-items.html", context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return HttpResponseServerError(render_to_string('403.html', {'exception': message}))

    except Exception:
        print("[{:%d/%b/%Y %H:%M:%S}] ERROR 500 \n{}".format(timezone.now(), traceback.format_exc()))
        return HttpResponseServerError(render_to_string('500.html', {'exception': traceback.format_exc().strip()}))


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
            return HttpResponseServerError(render_to_string('403.html', {'exception': message}))

    except Exception:
        print("[{:%d/%b/%Y %H:%M:%S}] ERROR 500 \n{}".format(timezone.now(), traceback.format_exc()))
        return HttpResponseServerError(render_to_string('500.html', {'exception': traceback.format_exc().strip()}))


def toggle(request, itemId):
    try:
        if request.session.get('player') and request.method == "POST":
            print('[view.bazaar.updateItem] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            # key = player.key
            # nItems = Preference.objects.all()[0].nItems
            bazaarJson = json.loads(player.bazaarJson)
            playerList = bazaarJson.get("list", [])

            item = Item.objects.filter(tId=itemId).first()
            if itemId in playerList:
                message = "Removed"
                playerList.remove(itemId)
            else:
                message = "Added"
                playerList.append(itemId)

            bazaarJson["list"] = playerList
            player.bazaarJson = json.dumps(bazaarJson)
            player.save()

            context = {'item': item, 'toggleMessage': message, "view": {"timer": True}}
            return render(request, "bazaar/item.html", context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return HttpResponseServerError(render_to_string('403.html', {'exception': message}))

    except Exception:
        print("[{:%d/%b/%Y %H:%M:%S}] ERROR 500 \n{}".format(timezone.now(), traceback.format_exc()))
        return HttpResponseServerError(render_to_string('500.html', {'exception': traceback.format_exc().strip()}))
