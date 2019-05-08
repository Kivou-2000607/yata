from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied

from django.utils import timezone

import json
from .models import Config
from .models import Item
from .models import ItemUpdate
from .models import Player
from .models import Stat
from yata.handy import apiCall
from yata.handy import None2EmptyDict

from player.models import Player

# out["view"] = {"byType": True,
#                "refreshAll": False,
#                "refreshType": True,
#                "hideType": False,
#                "lastScan": Config.objects.all()[0].lastScan,
#                "stock": False,
#                "help": True}


def index(request):
    if request.session.get('player'):
        print('[view.bazaar.index] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        key = player.key
        bazaarJson = json.loads(player.bazaarJson)

        # update inventory of bazaarJson
        error=False
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
        items = {tType:[] for tType in tTypes}

        for tType in items:
            for item in itemsOnMarket.filter(tType=tType):
                item.stock = inventory.get(str(item.tId), 0)
                items[tType].append(item)
                # item.save()


        context = {"player": player, "bazaarcat": True, "allItemsOnMarket": items, "view": {"byType": True, "refreshType": True, "timer": True} }
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
        key = player.key
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

        context = {"player": player, "bazaarcat": True, "allItemsOnMarket": items, "view": {"byType": True, "refreshType": True, "timer": True}}
        page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
        return render(request, page, context)
    else:
        raise PermissionDenied("You might want to log in.")

    raise PermissionDenied("You might want to log in.")

def default(request):
    if request.session.get('player'):
        print('[view.bazaar.default] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        key = player.key
        bazaarJson = json.loads(player.bazaarJson)
        inventory = bazaarJson.get("inventory", dict({}))
        playerList = bazaarJson.get("list", [])

        print('[view.bazaar.default] get all items on market')
        itemsOnMarket = Item.objects.filter(onMarket=True)
        print('[view.bazaar.default] get all tTypes')
        tTypes = [r["tType"] for r in itemsOnMarket.values("tType").distinct()]
        print('[view.bazaar.default] {}'.format(tTypes))
        print('[view.bazaar.default] create output items')
        items = {tType:[] for tType in tTypes}

        for tType in items:
            for item in itemsOnMarket.filter(tType=tType):
                item.stock = inventory.get(str(item.tId), 0)
                items[tType].append(item)
                # item.save()

        context = {"player": player, "bazaarcat": True, "allItemsOnMarket": items, "view": {"byType": True, "refreshType": True, "timer": True}}
        page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
        return render(request, page, context)
    else:
        raise PermissionDenied("You might want to log in.")

def sets(request):
    if request.session.get('player'):
        print('[view.bazaar.default] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        key = player.key
        bazaarJson = json.loads(player.bazaarJson)
        inventory = bazaarJson.get("inventory", dict({}))
        playerList = bazaarJson.get("list", [])

        print('[view.bazaar.default] get all items on market')
        itemsOnMarket = Item.objects.filter(onMarket=True)
        print('[view.bazaar.default] get all tTypes')
        tTypes = ["Flower", "Plushie"]
        print('[view.bazaar.default] {}'.format(tTypes))
        print('[view.bazaar.default] create output items')
        items = {tType:[] for tType in tTypes}

        for tType in items:
            for item in itemsOnMarket.filter(tType=tType):
                print(item)
                item.stock = inventory.get(str(item.tId), 0)
                items[tType].append(item)
                # item.save()

        context = {"player": player, "bazaarcat": True, "allItemsOnMarket": items, "view": {"byType": True, "refreshType": True, "timer": True}}
        page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
        return render(request, page, context)
    else:
        raise PermissionDenied("You might want to log in.")


def all(request):
    if request.session.get('player'):
        print('[view.bazaar.default] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        key = player.key
        bazaarJson = json.loads(player.bazaarJson)
        inventory = bazaarJson.get("inventory", dict({}))
        playerList = bazaarJson.get("list", [])

        print('[view.bazaar.default] get all items on market')
        itemsOnMarket = Item.objects.all()
        print('[view.bazaar.default] get all tTypes')
        tTypes = [r["tType"] for r in itemsOnMarket.values("tType").distinct()]
        print('[view.bazaar.default] {}'.format(tTypes))
        print('[view.bazaar.default] create output items')
        items = {tType:[] for tType in tTypes}

        for tType in items:
            for item in itemsOnMarket.filter(tType=tType):
                item.stock = inventory.get(str(item.tId), 0)
                items[tType].append(item)
                # item.save()

        context = {"player": player, "bazaarcat": True, "allItemsOnMarket": items, "view": {"byType": True}}
        page = 'bazaar/content-reload.html' if request.method == 'POST' else "bazaar.html"
        return render(request, page, context)
    else:
        raise PermissionDenied("You might want to log in.")


def updateItem(request, itemId):
    if request.session.get('player') and request.method == "POST":
        print('[view.bazaar.updateItem] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        key = player.key
        bazaarJson = json.loads(player.bazaarJson)

        print('[view.bazaar.updateItem] get item')
        item = Item.objects.filter(tId=itemId).first()
        print('[view.bazaar.updateItem] {}'.format(item))

        baz = item.update_bazaar(key=key, n=Config.objects.first().nItems)
        error = False
        if "apiError" in baz:
            error = baz

        # update inventory of bazaarJson
        error=False
        invtmp = apiCall("user", "", "inventory", key, sub="inventory")
        if 'apiError' in invtmp:
            error = invtmp
        else:
            # modify user
            for i in invtmp:
                if i["ID"] == int(itemId):
                    print('[view.bazaar.updateItem] personal stock: {}'.format(i["quantity"]))
                    bazaarJson["inventory"][itemId] = i["quantity"]

                    # modify item for display
                    item.stock = i["quantity"]
                    item.save()
                    break

        player.bazaarJson = json.dumps(bazaarJson)
        player.save()


        context = {'item': item, "view": {"timer": True}}
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
        nItems = Config.objects.all()[0].nItems
        bazaarJson = json.loads(player.bazaarJson)
        inventory = bazaarJson.get("inventory", dict({}))
        playerList = bazaarJson.get("list", [])

        itemsAPI = apiCall("torn", "", "items", key, sub='items')
        error = False
        if "apiError" in itemsAPI:
            error = itemAPI

        if tType == "Custom":
            items = Item.objects.filter(tId__in=playerList)
        else:
            items = Item.objects.filter(onMarket=True).filter(tType=tType)

        for item in items:
            print("[VIEW updateTypeBazaar]: update ", item)
            item.update(itemsAPI[str(item.tId)])
            item.update_bazaar(key=key, n=nItems)
            item.save()
            item.stock = inventory.get(item.tId, 0)

        # player.bazaarJson = json.dumps(bazaarJson)
        # player.save()

        context = {"itemType": tType, "items": items, "view": {"byType": True, "refreshType": True, "timer": True}}
        return render(request, "bazaar/loop-items.html", context)

    else:
        message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
        raise PermissionDenied(message)


def deleteItem(request, itemId):
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


def toggleItem(request, itemId):
    if request.session.get('player') and request.method == "POST":
        print('[view.bazaar.updateItem] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        key = player.key
        nItems = Config.objects.all()[0].nItems
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

        context = {'item': item, 'toggleMessage': message, "view": {"timer": True} }
        return render(request, "bazaar/item.html", context)

    else:
        message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
        raise PermissionDenied(message)



#
# def custom(request):
#     try:
#         playerId = request.session["user"].get("playerId")
#         user = Player.objects.filter(playerId=playerId)[0]
#         out = dict({"allItemsOnMarket": dict()})
#         allItems = Item.objects
#         try:
#             out["allItemsOnMarket"]["Custom"] = []
#             # get dictionary of stocks
#             inventory = apiCall("user", "", "inventory", request.session["user"].get("keyValue"), sub="inventory")
#             id_stock = {id: 0 for id in user.get_items_id()}
#             for inv in inventory:
#                 if str(inv["ID"]) in id_stock:
#                     id_stock[str(inv["ID"])] = inv["quantity"]
#             for item in [allItems.filter(tId=int(id))[0] for id in id_stock]:
#                 item.stock = id_stock[str(item.tId)]
#                 out["allItemsOnMarket"]["Custom"].append(item)
#         except:
#             out["allItemsOnMarket"]["Custom"] = []
#         out["view"] = {"byType": True, "refreshType": True, "help": True, "stock": True}
#         out["nUpdate"] = Stat.objects.all()[0].getStats()
#
#         return render(request, 'bazaar.html', out)
#
#     except:
#
#         return HttpResponseRedirect(reverse('bazaar:default'))
#
#
# def default(request):
    # # allItems = Item.objects.filter( onMarket=True ).exclude( tType="Flower" ).exclude( tType="Plushie" )
    # allItems = Item.objects.filter(onMarket=True)
    #
    # if request.session.get("user"):  # if log
    #     inventory = apiCall("user", "", "inventory", request.session["user"].get("keyValue"), sub="inventory")
    #     if "apiError" in inventory:
    #         id_stock = dict({})
    #     else:
    #         id_stock = {inv["ID"]: inv["quantity"] for inv in inventory}
    # else:
    #     id_stock = dict({})
    #
    # out = dict({"allItemsOnMarket": dict()})
    # for tType in [r["tType"] for r in allItems.values("tType").distinct()]:
    #     out["allItemsOnMarket"][tType] = []
    #     for item in allItems.filter(tType=tType):
    #         item.stock = id_stock.get(item.tId, 0)
    #         out["allItemsOnMarket"][tType].append(item)
    #
    # out["view"] = {"byType": True, "refreshType": True, "hideType": True, "help": True}
    # out["nUpdate"] = Stat.objects.all()[0].getStats()
    #
    # return render(request, 'bazaar.html', out)
#
#
# def fullList(request):
#     allItems = Item.objects
#
#     if request.session.get("user"):  # if log
#         inventory = apiCall("user", "", "inventory", request.session["user"].get("keyValue"), sub="inventory")
#         if "apiError" in inventory:
#             id_stock = dict({})
#         else:
#             id_stock = {inv["ID"]: inv["quantity"] for inv in inventory}
#     else:
#         id_stock = dict({})
#
#     out = dict({"allItemsOnMarket": dict()})
#     for tType in [r["tType"] for r in allItems.values("tType").distinct()]:
#         out["allItemsOnMarket"][tType] = []
#         for item in allItems.filter(tType=tType):
#             item.stock = id_stock.get(item.tId, 0)
#             out["allItemsOnMarket"][tType].append(item)
#
#     out["view"] = {"byType": True, "hideType": True, "lastScan": Config.objects.all()[0].lastScan}
#     out["nUpdate"] = Stat.objects.all()[0].getStats()
#
#     return render(request, 'bazaar.html', out)
#
#
# def sets(request):
#     allItems = Item.objects.filter(onMarket=True)
#
#     if request.session.get("user"):  # if log
#         inventory = apiCall("user", "", "inventory", request.session["user"].get("keyValue"), sub="inventory")
#         if "apiError" in inventory:
#             id_stock = dict({})
#         else:
#             id_stock = {inv["ID"]: inv["quantity"] for inv in inventory}
#     else:
#         id_stock = dict({})
#
#     out = dict({"allItemsOnMarket": dict()})
#     acceptedTypes = ["Flower", "Plushie"]
#     for tType in [r["tType"] for r in allItems.values("tType").distinct()]:
#         if tType in acceptedTypes:
#             out["allItemsOnMarket"][tType] = []
#             for item in allItems.filter(tType=tType):
#                 item.stock = id_stock.get(item.tId, 0)
#                 out["allItemsOnMarket"][tType].append(item)
#
#     out["view"] = {"byType": True, "refreshAll": False, "refreshType": True, "hideType": False, "help": True}
#     out["nUpdate"] = Stat.objects.all()[0].getStats()
#
#     return render(request, 'bazaar.html', out)
#
#
# # UPDATE ON THE FLY
# def logout(request):
#     try:
#         del request.session["user"]
#     except:
#         pass
#     return HttpResponseRedirect(reverse('bazaar:index'))
#
#
# def updateKey(request):
#
#     # request.session["user"] = {'keyValue': "myKeyForDebug",
#     #                            'name': "Kivou",
#     #                            'playerId': 2000607,
#     #                            }
#     # request.session.set_expiry(0)  # logout when close browser
#     # return render(request, "sub/intro.html")
#
#     if request.method == "POST":
#         p = request.POST
#
#         user = apiCall("user", "", "basic", p.get("keyValue"))
#         if "apiError" in user:
#             return render(request, "sub/{}.html".format(p["html"]), user)
#
#         name = "{} [{}]".format(user["name"], user["player_id"])
#         request.session["user"] = {'keyValue': p["keyValue"], 'name': name, 'playerId': user["player_id"]}
#         check = json.loads(p.get("rememberSession"))
#         if check:
#             print("[Login]: log for 1 year")
#             request.session.set_expiry(31536000)  # 1 year
#         else:
#             print("[Login]: log for the session")
#             request.session.set_expiry(0)  # logout when close browser
#         # log
#         findLog = Player.objects.filter(playerId=user["player_id"])
#         if len(findLog):
#             log = findLog[0]
#             log.nLog += 1
#         else:
#             log = Player.objects.create(name=user["name"], playerId=user["player_id"])
#         log.save()
#         return render(request, "sub/{}.html".format(p["html"]))
#
#     else:
#         return HttpResponse("Don't try to be a smart ass, you need to post.")


#

#
##
#
# def updateTypeBazaar(request):
#     if request.method == "POST":
#         p = request.POST
#         nItems = Config.objects.all()[0].nItems
#         apiKey = ""
#         try:
#             apiKey = request.session["user"]["keyValue"]
#         except:
#             pass
#
#         itemsAPI = apiCall("torn", "", "items", apiKey, sub='items')
#         if "apiError" in itemsAPI:
#             return render(request, "sub/{}.html".format(p["html"]), itemsAPI)
#
#         inventory = apiCall("user", "", "inventory", request.session["user"].get("keyValue"), sub="inventory")
#         if "apiError" in inventory:
#             return render(request, "sub/{}.html".format(p["html"]), inventory)
#         id_stock = {inv["ID"]: inv["quantity"] for inv in inventory}
#
#         if tType == "Custom":
#             playerId = request.session["user"].get("playerId")
#             user = Player.objects.filter(playerId=playerId)[0]
#             items = Item.objects.filter(tId__in=user.get_items_id())
#         else:
#             items = Item.objects.filter(onMarket=True).filter(tType=p["tType"])
#
#         for item in items:
#             print("[VIEW updateTypeBazaar]: update ", item)
#             item.update(item.tId, itemsAPI[str(item.tId)])
#             item.update_bazaar(key=request.session["user"]["keyValue"], n=nItems)
#             item.save()
#             item.stock = id_stock.get(item.tId, 0)
#
#         out = dict({"itemType": p["tType"], "items": items})
#         out["view"] = {"byType": True, "refreshType": True}
#
#         user = Player.objects.filter(playerId=request.session["user"].get("playerId"))[0]
#         user.date = timezone.now()
#         user.save()
#
#         return render(request, "sub/{}.html".format(p["html"]), out)
#     else:
#         return HttpResponse("Don't try to be a smart ass, you need to post.")
#
#
# def details(request):
#     if request.method == "POST":
#         p = request.POST
#         item = Item.objects.filter(tId=p["tId"])[0]
#         return render(request, 'sub/details.html', {'item': item})
#     else:
#         return HttpResponse("Don't try to be a smart ass, you need to post.")
