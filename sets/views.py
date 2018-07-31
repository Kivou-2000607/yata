from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone

import requests
from .models import config
from .models import Item
from .models import login


def index(request):
    # allItems = Item.objects.filter( onMarket=True ).exclude( tType="Flower" ).exclude( tType="Plushie" )
    allItems = Item.objects.filter(onMarket=True)
    out = dict({"allItemsOnMarket": dict()})
    for tType in [r["tType"] for r in allItems.values("tType").distinct()]:
        out["allItemsOnMarket"][tType] = [i for i in allItems.filter(tType=tType)]
    if not request.session.get("key"):
        key = False
    else:
        key = request.session["key"]["value"]
    out["view"] = {"byType": True, "refreshAll": False, "refreshType": True, "key": key}
    return render(request, 'index.html', out)


def fullList(request):
    allItems = Item.objects
    out = dict({"allItemsOnMarket": dict()})
    for tType in [r["tType"] for r in allItems.values("tType").distinct()]:
        out["allItemsOnMarket"][tType] = [i for i in allItems.filter(tType=tType)]
    out["view"] = {"byType": True, "refreshAll": False, "refreshType": False}
    return render(request, 'index.html', out)


def sets(request):
    allItems = Item.objects.filter(onMarket=True)
    out = dict({"allItemsOnMarket": dict()})
    acceptedTypes = ["Flower", "Plushie"]
    for tType in [r["tType"] for r in allItems.values("tType").distinct()]:
        if tType in acceptedTypes:
            out["allItemsOnMarket"][tType] = [i for i in allItems.filter(tType=tType)]
    out["view"] = {"byType": True, "refreshAll": False, "refreshType": True}
    return render(request, 'index.html', out)


def scan(request):
    apiKey = ""
    try:
        apiKey = request.session["user"]["keyValue"]
    except:
        pass

    request_url = "https://api.torn.com/torn/?selections=items&key={}".format(apiKey)
    items = requests.get(request_url).json()['items']
    for k, v in items.items():
        req = Item.objects.filter(tId=int(k))
        if len(req) == 0:
            item = Item.create(k, v)
            item.save()
        elif len(req) == 1:
            item = req[0]
            item.update(k, v)
            item.save()
        else:
            print("[VIEW scan]: request found more than one item id", len(req))
            return None

        # if item.onMarket:
            # item.updateBazaar(n=c.nItems)
            # item.save()

    return HttpResponseRedirect(reverse('index'))


# UPDATE ON THE FLY
def logout(request):
    try:
        del request.session["user"]
    except:
        pass
    return HttpResponseRedirect(reverse('index'))


def updateKey(request):
    if request.method == "POST":
        p = request.POST
        user = requests.get("https://api.torn.com/user/?selections=basic&key={}".format(p["keyValue"])).json()
        try:
            name = "{} [{}]".format(user["name"], user["player_id"])
            request.session["user"] = {'keyValue': p["keyValue"], 'name': name}
            request.session.set_expiry(1800)
            # log
            find_log = login.objects.filter(user_id=user["player_id"])
            if len(find_log):
                log = find_log[0]
                log.n_log = log.n_log+1
                log.date = timezone.now()
            else:
                log = login.objects.create(user_name=user["name"], user_id=user["player_id"])
            log.logindate_set.create()
            log.save()
        except:
            try:
                del request.session["user"]
            except:
                pass
            try:
                out = dict({"apiError": "API error code {}: {}.".format(user["error"]["code"], user["error"]["error"])})
                return render(request, "sub/{}.html".format(p["html"]), out)
            except:
                pass
            pass
        return render(request, "sub/{}.html".format(p["html"]))

    else:
        return HttpResponse("Don't try to be a smart ass, you need to post.")


def updateItemBazaar(request):
    if request.method == "POST":
        p = request.POST
        item = Item.objects.filter(tId=p["tId"])[0]

        apiKey = ""
        try:
            apiKey = request.session["user"]["keyValue"]
        except:
            pass

        req = item.updateBazaar(key=apiKey, n=config.objects.all()[0].nItems)

        if "error" in req:
            return render(request, "sub/{}.html".format(p["html"]), {'item': item, "apiError": "API error code {}: {}.".format(req["error"]["code"], req["error"]["error"])})
        else:
            return render(request, "sub/{}.html".format(p["html"]), {'item': item})

    else:
        return HttpResponse("Don't try to be a smart ass, you need to post.")


def deleteItemBazaar(request):
    if request.method == "POST":
        # c = config.objects.all()[0]
        p = request.POST
        item = Item.objects.filter(tId=p["tId"])[0]
        item.date = timezone.now()
        item.marketdata_set.all().delete()
        item.userstock_set.all().delete()
        item.save()
        return render(request, "sub/{}.html".format(p["html"]), {'item': item})
    else:
        return HttpResponse("Don't try to be a smart ass, you need to post.")


def updateTypeBazaar(request):
    if request.method == "POST":
        p = request.POST
        c = config.objects.all()[0]

        apiKey = ""
        try:
            apiKey = request.session["user"]["keyValue"]
        except:
            pass

        req = requests.get("https://api.torn.com/torn/?selections=items&key={}".format(apiKey)).json()
        try:
            itemsAPI = req['items']
        except:
            if "error" in req:
                out = dict({"apiError": "API error code {}: {}.".format(req["error"]["code"], req["error"]["error"])})
                return render(request, "sub/{}.html".format(p["html"]), out)
            else:
                return render(request, "sub/{}.html".format(p["html"]), {"apiError": "something went wrong from out side..."})

        items = Item.objects.filter(onMarket=True).filter(tType=p["tType"])

        # get users/keys
        # userInventory = dict({})
        # for u, key in c.listOfStockKeys():
        # userInventory[u] = requests.get( "https://api.torn.com/user/?selections=inventory&key={}".format( key ) ).json()['inventory']

        for item in items:
            print("[VIEW updateTypeBazaar]: update ", item)
            uq = []
            # for u in userInventory:
            # try:    q = next((i for i in userInventory[u] if int(i["ID"]) == int(item.tId)),{'quantity':0})['quantity']
            # except: q = -1
            # uq.append( [u,q] )
            item.update(item.tId, itemsAPI[str(item.tId)], uq=uq)
            try:
                item.updateBazaar(key=request.session["user"]["keyValue"], n=c.nItems)
            except:
                print("wrong api key")
                pass
            item.save()

        out = dict({"items": items})
        out["view"] = {"byType": True, "refreshType": True}
        return render(request, "sub/{}.html".format(p["html"]), out)
    else:
        return HttpResponse("Don't try to be a smart ass, you need to post.")


def updateAll(request):
    if request.method == "POST":
        p = request.POST
        c = config.objects.all()[0]

        try:
            itemsAPI = requests.get("https://api.torn.com/torn/?selections=items&key={}".format(request.session["user"]["keyValue"])).json()['items']
        except:
            out = dict({"view": {"apiError": True}})
            return render(request, "sub/{}.html".format(p["html"]), out)

        allItems = Item.objects.filter(onMarket=True).exclude(tType="Flower").exclude(tType="Plushie")

        # get users/keys
        # userInventory = dict({})
        # for u, key in c.listOfStockKeys():
        # userInventory[u] = requests.get( "https://api.torn.com/user/?selections=inventory&key={}".format( key ) ).json()['inventory']

        for item in allItems:
            print("[VIEW updateAll]: update ", item)
            uq = []
            # for u in userInventory:
            # try:    q = next((i for i in userInventory[u] if int(i["ID"]) == int(item.tId)),{'quantity':0})['quantity']
            # except: q = -1
            # uq.append( [u,q] )
            item.update(item.tId, itemsAPI[str(item.tId)], uq=uq)
            try:
                item.updateBazaar(key=request.session["user"]["keyValue"], n=c.nItems)
            except:
                print("wrong api key")
                pass

            item.save()
        out = dict({"allItemsOnMarket": dict()})
        for tType in [r["tType"] for r in allItems.values("tType").distinct()]:
            out["allItemsOnMarket"][tType] = [i for i in allItems.filter(tType=tType)]

        byType = True if p["viewByType"] == "True" else False
        out["view"] = {"byType": byType, "refreshAll": True}
        return render(request, "sub/{}.html".format(p["html"]), out)
    else:
        return HttpResponse("Don't try to be a smart ass, you need to post.")


def details(request, tId):
    item = Item.objects.filter(tId=tId)[0]
    return render(request, 'details.html', {'item': item})
