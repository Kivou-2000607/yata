from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone

import requests
import json
from .models import Config
from .models import Item
from .models import ItemUpdate
from .models import Player
from .handy import apiCall


# out["view"] = {"byType": True,
#                "refreshAll": False,
#                "refreshType": True,
#                "hideType": False,
#                "lastScan": Config.objects.all()[0].lastScan,
#                "stock": False,
#                "help": True}


def index(request):
    if request.session.get("user") is not None:
        return HttpResponseRedirect(reverse('bazaar:custom'))
    else:
        return HttpResponseRedirect(reverse('bazaar:default'))


def custom(request):
    try:
        playerId = request.session["user"].get("playerId")
        user = Player.objects.filter(playerId=playerId)[0]
        out = dict({"allItemsOnMarket": dict()})
        allItems = Item.objects
        try:
            out["allItemsOnMarket"]["Custom"] = []
            # get dictionary of stocks
            inventory = apiCall("user", "", "inventory", request.session["user"].get("keyValue"), sub="inventory")
            id_stock = {id: 0 for id in user.get_items_id()}
            for inv in inventory:
                if str(inv["ID"]) in id_stock:
                    id_stock[str(inv["ID"])] = inv["quantity"]
            print(id_stock)
            for item in [allItems.filter(tId=int(id))[0] for id in id_stock]:
                item.stock = id_stock[str(item.tId)]
                out["allItemsOnMarket"]["Custom"].append(item)
        except:
            out["allItemsOnMarket"]["Custom"] = []
        out["view"] = {"byType": True, "refreshType": True, "help": True, "stock": True}
        out["nUpdate"] = ItemUpdate.objects.filter(date__gte=timezone.now() - timezone.timedelta(days=1)).count()

        return render(request, 'bazaar.html', out)

    except:

        return HttpResponseRedirect(reverse('bazaar:default'))


def default(request):
    # allItems = Item.objects.filter( onMarket=True ).exclude( tType="Flower" ).exclude( tType="Plushie" )
    allItems = Item.objects.filter(onMarket=True)
    out = dict({"allItemsOnMarket": dict()})
    for tType in [r["tType"] for r in allItems.values("tType").distinct()]:
        out["allItemsOnMarket"][tType] = [i for i in allItems.filter(tType=tType)]
    out["view"] = {"byType": True, "refreshType": True, "hideType": True, "help": True}
    out["nUpdate"] = ItemUpdate.objects.filter(date__gte=timezone.now() - timezone.timedelta(days=1)).count()

    return render(request, 'bazaar.html', out)


def fullList(request):
    allItems = Item.objects
    out = dict({"allItemsOnMarket": dict()})
    for tType in [r["tType"] for r in allItems.values("tType").distinct()]:
        out["allItemsOnMarket"][tType] = [i for i in allItems.filter(tType=tType)]
    out["view"] = {"byType": True, "hideType": True, "lastScan": Config.objects.all()[0].lastScan}
    out["nUpdate"] = ItemUpdate.objects.filter(date__gte=timezone.now() - timezone.timedelta(days=1)).count()

    return render(request, 'bazaar.html', out)


def sets(request):
    allItems = Item.objects.filter(onMarket=True)
    out = dict({"allItemsOnMarket": dict()})
    acceptedTypes = ["Flower", "Plushie"]
    for tType in [r["tType"] for r in allItems.values("tType").distinct()]:
        if tType in acceptedTypes:
            out["allItemsOnMarket"][tType] = [i for i in allItems.filter(tType=tType)]
    out["view"] = {"byType": True, "refreshAll": False, "refreshType": True, "hideType": False, "help": True}
    out["nUpdate"] = ItemUpdate.objects.filter(date__gte=timezone.now() - timezone.timedelta(days=1)).count()

    return render(request, 'bazaar.html', out)


# UPDATE ON THE FLY
def logout(request):
    try:
        del request.session["user"]
    except:
        pass
    return HttpResponseRedirect(reverse('bazaar:index'))


def updateKey(request):
    if request.method == "POST":
        p = request.POST

        user = apiCall("user", "", "basic", p.get("keyValue"))
        if "apiError" in user:
            return render(request, "sub/{}.html".format(p["html"]), user)

        name = "{} [{}]".format(user["name"], user["player_id"])
        request.session["user"] = {'keyValue': p["keyValue"], 'name': name, 'playerId': user["player_id"]}
        check = json.loads(p.get("rememberSession"))
        if check:
            print("[Login]: log for 1 year")
            request.session.set_expiry(31536000)  # 1 year
        else:
            print("[Login]: log for the session")
            request.session.set_expiry(0)  # logout when close browser
        # log
        findLog = Player.objects.filter(playerId=user["player_id"])
        if len(findLog):
            log = findLog[0]
            log.nLog += 1
            log.date = timezone.now()
        else:
            log = Player.objects.create(name=user["name"], playerId=user["player_id"])
        log.save()
        return render(request, "sub/{}.html".format(p["html"]))

    else:
        return HttpResponse("Don't try to be a smart ass, you need to post.")


def updateItemBazaar(request):
    if request.method == "POST":
        p = request.POST
        item = Item.objects.filter(tId=p["tId"])[0]
        nItems = Config.objects.all()[0].nItems
        try:
            apiKey = request.session["user"]["keyValue"]
        except:
            apiKey = ""

        baz = item.update_bazaar(key=apiKey, n=nItems)

        if "apiError" in baz:
            return render(request, "sub/{}.html".format(p["html"]), {'item': item, "apiError": baz["apiError"]})
        else:
            return render(request, "sub/{}.html".format(p["html"]), {'item': item})

    else:
        return HttpResponse("Don't try to be a smart ass, you need to post.")


def toggleItem(request):
    if request.method == "POST":
        p = request.POST
        itemId = p["tId"]
        item = Item.objects.filter(tId=itemId)[0]
        playerId = request.session["user"].get("playerId")
        user = Player.objects.filter(playerId=playerId)[0]
        add = user.toggle_item(itemId)

        if add:
            message = "Added"
        else:
            message = "Removed"

        return render(request, "sub/{}.html".format(p["html"]), {'item': item, 'toggleMessage': message})

    else:
        return HttpResponse("Don't try to be a smart ass, you need to post.")


def deleteItemBazaar(request):
    if request.method == "POST":
        p = request.POST
        item = Item.objects.filter(tId=p["tId"])[0]
        item.date = timezone.now()
        item.marketdata_set.all().delete()
        item.save()
        return render(request, "sub/{}.html".format(p["html"]), {'item': item})
    else:
        return HttpResponse("Don't try to be a smart ass, you need to post.")


def updateTypeBazaar(request):
    if request.method == "POST":
        p = request.POST
        nItems = Config.objects.all()[0].nItems
        apiKey = ""
        try:
            apiKey = request.session["user"]["keyValue"]
        except:
            pass

        itemsAPI = apiCall("torn", "", "items", apiKey, sub='items')

        if "apiError" in itemsAPI:
            return render(request, "sub/{}.html".format(p["html"]), itemsAPI)

        if p["tType"] == "Custom":
            playerId = request.session["user"].get("playerId")
            user = Player.objects.filter(playerId=playerId)[0]
            items = Item.objects.filter(tId__in=user.get_items_id())
        else:
            items = Item.objects.filter(onMarket=True).filter(tType=p["tType"])

        for item in items:
            print("[VIEW updateTypeBazaar]: update ", item)
            item.update(item.tId, itemsAPI[str(item.tId)])
            try:
                item.update_bazaar(key=request.session["user"]["keyValue"], n=nItems)
            except:
                print("wrong api key")
                pass
            item.save()

        out = dict({"itemType": p["tType"], "items": items})
        out["view"] = {"byType": True, "refreshType": True}
        return render(request, "sub/{}.html".format(p["html"]), out)
    else:
        return HttpResponse("Don't try to be a smart ass, you need to post.")


def details(request):
    if request.method == "POST":
        p = request.POST
        item = Item.objects.filter(tId=p["tId"])[0]
        return render(request, 'sub/details.html', {'item': item})
    else:
        return HttpResponse("Don't try to be a smart ass, you need to post.")
