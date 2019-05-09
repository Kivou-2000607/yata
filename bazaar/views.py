from django.shortcuts import render
from django.core.exceptions import PermissionDenied
# from django.utils import timezone


import json
import time

from bazaar.models import Preference
from bazaar.models import Item
from player.models import Player
from yata.handy import apiCall


def index(request):
    if request.session.get('player'):
        print('[view.bazaar.index] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        key = player.key
        bazaarJson = json.loads(player.bazaarJson)

        # update inventory of bazaarJson
        error = False
        invtmp = apiCall("user", "", "inventory", key, sub="inventory")
        if 'apiError' in invtmp:
            error = invtmp
        else:
            bazaarJson["inventory"] = {v["ID"]: v["quantity"] for v in invtmp}
            player.bazaarJson = json.dumps(bazaarJson)

        playerList = bazaarJson.get("list", [])
        inventory = bazaarJson.get("inventory", [])
        player.bazaarInfo = "{} items".format(len(playerList))
        player.save()

        print('[view.bazaar.default] get all items on market')
        itemsOnMarket = Item.objects.filter(onMarket=True)
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

        context = {"player": player, "bazaarcat": True, "allItemsOnMarket": items, "view": {"refreshType": True, "timer": True}}
        if error:
            context.update(error)
        return render(request, 'bazaar.html', context)

    else:
        raise PermissionDenied("You might want to log in.")


def custom(request):
    if request.session.get('player'):
        print('[view.bazaar.default] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        # key = player.key
        bazaarJson = json.loads(player.bazaarJson)
        inventory = bazaarJson.get("inventory", dict({}))
        playerList = bazaarJson.get("list", [])

        print('[view.bazaar.default] get all items on player\'s list')
        itemsOnMarket = Item.objects.filter(tId__in=playerList)
        print('[view.bazaar.default] create output items')
        items = {"Custom": []}

        for item in itemsOnMarket:
            print(item)
            item.stock = inventory.get(str(item.tId), 0)
            items["Custom"].append(item)
            # item.save()

        context = {"player": player, "bazaarcat": True, "allItemsOnMarket": items, "view": {"refreshType": True, "timer": True}}
        page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
        return render(request, page, context)
    else:
        raise PermissionDenied("You might want to log in.")


def default(request):
    if request.session.get('player'):
        print('[view.bazaar.default] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        # key = player.key
        bazaarJson = json.loads(player.bazaarJson)
        inventory = bazaarJson.get("inventory", dict({}))
        # playerList = bazaarJson.get("list", [])

        print('[view.bazaar.default] get all items on market')
        itemsOnMarket = Item.objects.filter(onMarket=True)
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

        context = {"player": player, "bazaarcat": True, "allItemsOnMarket": items, "view": {"refreshType": True, "timer": True}}
        page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
        return render(request, page, context)
    else:
        raise PermissionDenied("You might want to log in.")


def sets(request):
    if request.session.get('player'):
        print('[view.bazaar.default] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
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
        raise PermissionDenied("You might want to log in.")


def all(request):
    if request.session.get('player'):
        print('[view.bazaar.default] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
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

        context = {"player": player, "bazaarcat": True, "allItemsOnMarket": items, "view": {"refreshType": True, "timer": False}}
        page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
        return render(request, page, context)
    else:
        raise PermissionDenied("You might want to log in.")


def details(request, itemId):
    if request.session.get('player') and request.method == "POST":
        item = Item.objects.filter(tId=itemId).first()

        context = {'item': item}
        return render(request, 'bazaar/details.html', context)

    else:
        message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
        raise PermissionDenied(message)


def update(request, itemId):
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
        if "apiError" in baz:
            error = baz

        # update inventory of bazaarJson
        error = False
        invtmp = apiCall("user", "", "inventory", key, sub="inventory")
        if 'apiError' in invtmp:
            error = {"apiErrorSub": invtmp["apiError"]}
        else:
            # modify user
            for i in invtmp:
                if i["ID"] == int(itemId):
                    print('[view.bazaar.updateItem] personal stock: {}'.format(i["quantity"]))
                    bazaarJson["inventory"][itemId] = i["quantity"]

                    # modify item for display
                    item.stock = i["quantity"]
                    saveSuccess = False
                    while saveSuccess is False:
                        try:
                            print("[view.bazaar.updateItem] save item")
                            item.save()
                            saveSuccess = True
                        except:
                            print("[view.bazaar.updateItem] db locked sleep 1s before saving item")
                            time.sleep(1)
                    break

        player.bazaarJson = json.dumps(bazaarJson)
        saveSuccess = False
        while saveSuccess is False:
            try:
                print("[view.bazaar.updateItem] save player")
                player.save()
                saveSuccess = True
            except:
                print("[view.bazaar.updateItem] db locked sleep 1s before saving player")
                time.sleep(1)

        context = {'item': item, "view": {"timer": True}}
        if error:
            context.update(error)
        return render(request, "bazaar/item.html", context)

    else:
        message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
        raise PermissionDenied(message)


def updateType(request, tType):
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
        raise PermissionDenied(message)


def delete(request, itemId):
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
        raise PermissionDenied(message)


def toggle(request, itemId):
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
        raise PermissionDenied(message)
