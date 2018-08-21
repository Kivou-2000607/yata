from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone

import requests
from .models import Config
from .models import Item
from .models import Player

def allow_scan(request):
    try:
        playerId = request.session["user"].get("playerId")
        if playerId in Config.objects.all()[0].list_autorised_id():
            return True
    except:
        pass
    return False

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
            out["allItemsOnMarket"]["My Items"] = [allItems.filter(tId=id)[0] for id in user.get_items_id()]
        except:
            out["allItemsOnMarket"]["My Items"] = []
        out["view"] = {"byType": True, "refreshAll": False, "refreshType": False, "hideType": False, "help": True}
        return render(request, 'bazaar.html', out)
    except:
        return HttpResponseRedirect(reverse('bazaar:default'))

def default(request):
    # allItems = Item.objects.filter( onMarket=True ).exclude( tType="Flower" ).exclude( tType="Plushie" )
    allItems = Item.objects.filter(onMarket=True)
    out = dict({"allItemsOnMarket": dict()})
    for tType in [r["tType"] for r in allItems.values("tType").distinct()]:
        out["allItemsOnMarket"][tType] = [i for i in allItems.filter(tType=tType)]
    out["view"] = {"byType": True, "refreshAll": False, "refreshType": True, "hideType": True, "help": True}

    return render(request, 'bazaar.html', out)

def fullList(request):
    allItems = Item.objects
    out = dict({"allItemsOnMarket": dict()})
    for tType in [r["tType"] for r in allItems.values("tType").distinct()]:
        out["allItemsOnMarket"][tType] = [i for i in allItems.filter(tType=tType)]
    lastScan = Config.objects.all()[0].lastScan
    out["view"] = {"byType": True, "refreshAll": False, "refreshType": False, "hideType": True, "lastScan": lastScan}

    if allow_scan(request):
        out["view"]["scan"] = True

    return render(request, 'bazaar.html', out)


def sets(request):
    allItems = Item.objects.filter(onMarket=True)
    out = dict({"allItemsOnMarket": dict()})
    acceptedTypes = ["Flower", "Plushie"]
    for tType in [r["tType"] for r in allItems.values("tType").distinct()]:
        if tType in acceptedTypes:
            out["allItemsOnMarket"][tType] = [i for i in allItems.filter(tType=tType)]
    out["view"] = {"byType": True, "refreshAll": False, "refreshType": True, "hideType": False, "help": True}
    return render(request, 'bazaar.html', out)


def scan(request):
    if request.method == "POST":
        p = request.POST

        apiKey = ""
        userId = ""
        try:
            apiKey = request.session["user"].get("keyValue")
            userId = int(request.session["user"].get("playerId"))
        except:
            pass

        autorisedIds = Config.objects.all()[0].list_autorised_id()

        if userId in autorisedIds:
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

                break

            lastScan = Config.objects.all()[0].update_last_scan()
            out = {"view": {"scan": True, "lastScan": lastScan}}
            return render(request, "sub/{}.html".format(p["html"]), out)

        else:
            return HttpResponse("You don't have the right to do that. Torn id \"{}\" not in autorised list.".format(userId))

    else:
        return HttpResponse("Don't try to be a smart ass, you need to post.")


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
        user = requests.get("https://api.torn.com/user/?selections=basic&key={}".format(p["keyValue"])).json()
        try:
            name = "{} [{}]".format(user["name"], user["player_id"])
            request.session["user"] = {'keyValue': p["keyValue"], 'name': name, 'playerId': user["player_id"]}
            request.session.set_expiry(1800)
            # log
            findLog = Player.objects.filter(playerId=user["player_id"])
            if len(findLog):
                log = findLog[0]
                log.nLog += 1
                log.date = timezone.now()
            else:
                log = Player.objects.create(name=user["name"], playerId=user["player_id"])
            log.login_set.create()
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
            print("updateKey: fail log")
            pass
        return render(request, "sub/{}.html".format(p["html"]))

    else:
        return HttpResponse("Don't try to be a smart ass, you need to post.")


def updateItemBazaar(request):
    if request.method == "POST":
        p = request.POST
        item = Item.objects.filter(tId=p["tId"])[0]
        nItems = Config.objects.all()[0].nItems
        apiKey = ""
        try:
            apiKey = request.session["user"]["keyValue"]
        except:
            pass

        req = item.update_bazaar(key=apiKey, n=nItems)

        if "error" in req:
            return render(request, "sub/{}.html".format(p["html"]), {'item': item, "apiError": "API error code {}: {}.".format(req["error"]["code"], req["error"]["error"])})
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

        for item in items:
            print("[VIEW updateTypeBazaar]: update ", item)
            item.update(item.tId, itemsAPI[str(item.tId)])
            try:
                item.update_bazaar(key=request.session["user"]["keyValue"], n=nItems)
            except:
                print("wrong api key")
                pass
            item.save()

        out = dict({"items": items})
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
