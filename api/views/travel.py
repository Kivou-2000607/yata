"""
Copyright 2020 kivou.2000607@gmail.com

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

# standards
import json

from django.core.cache import cache

# django
from django.http import JsonResponse

# cache and rate limit
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from bazaar.countries import countries
from bazaar.models import AbroadStocks, Item, VerifiedClient
from yata.decorators import never_ever_cache

# yata
from yata.handy import tsnow

items_table = {
    "mex": [8, 11, 20, 26, 31, 50, 63, 99, 107, 108, 110, 111, 159, 175, 177, 178, 229, 230, 231, 258, 259, 260, 327, 399, 409, 426, 432, 640, 1125, 1429],
    "cay": [612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 1482],
    "can": [196, 197, 201, 205, 206, 252, 253, 261, 262, 263, 328, 402, 410, 413, 645, 1348, 1361, 1483, 1484],
    "haw": [240, 241, 242, 243, 264, 265, 419, 420, 421, 430, 1485, 1486],
    "uni": [196, 197, 198, 201, 203, 205, 206, 217, 218, 219, 220, 221, 266, 267, 268, 397, 408, 411, 415, 416, 418, 431, 438, 439, 641, 1246, 1361],
    "arg": [196, 198, 199, 203, 204, 255, 256, 257, 269, 270, 271, 333, 391, 407, 1466, 1487],
    "swi": [196, 198, 199, 201, 203, 204, 222, 223, 224, 272, 273, 361, 398, 435, 436],
    "jap": [197, 198, 200, 203, 204, 205, 206, 233, 234, 235, 236, 237, 238, 239, 277, 278, 279, 294, 334, 395, 427, 429, 433, 434, 437, 1249, 1333],
    "chi": [197, 199, 200, 201, 204, 244, 245, 246, 247, 248, 249, 250, 251, 274, 275, 276, 326, 335, 400, 1462],
    "uae": [381, 382, 383, 384, 385, 386, 387, 388, 412, 414, 440, 1264],
    "sou": [4, 199, 200, 201, 203, 206, 225, 226, 227, 228, 280, 281, 282, 332, 358, 406, 651, 652, 653, 654],
}


@method_decorator(never_ever_cache)
def exportStocks(request):
    try:

        c = cache.get("foreign_stocks_payload", False)
        if c:
            # print("[api.travel.export] get stocks (cache)")
            return JsonResponse(c, status=200)

        print("[api.travel.export] get stocks (db) start")

        # if getattr(request, 'limited', False):
        #     return JsonResponse({"error": {"code": 3, "error": "Too many requests (10 calls / hour)"}}, status=429)

        stocks = AbroadStocks.objects.filter(last=True)
        countries = {
            "mex": {},
            "cay": {},
            "can": {},
            "haw": {},
            "uni": {},
            "arg": {},
            "swi": {},
            "jap": {},
            "chi": {},
            "uae": {},
            "sou": {},
        }

        for k in countries:
            c_stocks = stocks.filter(country_key=k)
            if len(c_stocks):
                countries[k] = {"update": c_stocks.order_by("-timestamp").first().timestamp, "stocks": [s.payloadLight() for s in c_stocks]}
            else:
                countries[k] = {"update": 0, "stocks": []}

        payload = {"stocks": countries, "timestamp": tsnow()}

        cache.set("foreign_stocks_payload", payload, 3600)
        # print("[api.travel.export] get stocks (db) cache set")
        return JsonResponse(payload, status=200)

    except BaseException as e:
        return JsonResponse({"error": {"code": 1, "error": str(e)}}, status=500)


@csrf_exempt
def importStocks(request):
    try:
        if request.method != "POST":
            return JsonResponse({"error": {"code": 2, "error": "POST request needed"}}, status=400)

        try:
            payload = json.loads(request.body)
        except BaseException:
            return JsonResponse({"error": {"code": 2, "error": "wrong body format"}}, status=400)

        # check mandatory keys
        for key in ["country", "items"]:
            if key not in payload:
                return JsonResponse({"error": {"code": 2, "error": f"Missing '{key}' key in payload\""}}, status=400)

        # check items length
        if not len(payload["items"]):
            return JsonResponse({"error": {"code": 2, "error": "Empty items list"}}, status=400)

        # check country:
        country_key = str(payload["country"]).lower().strip()[:3]
        if country_key not in countries:
            return JsonResponse({"error": {"code": 2, "error": f"Unknown country key '{country_key}'"}}, status=400)

        if cache.get(f"foreign_stocks_lock_{country_key}", False):
            print("[api.travel.import] ignore update", country_key)
            return JsonResponse({"message": "The stocks have been updated less than 60s ago"}, status=200)
        else:
            cache.set(f"foreign_stocks_lock_{country_key}", True, 60)
            print("[api.travel.import] update stocks", country_key)

        country = countries[country_key]["name"]
        items = payload["items"]
        # uid = int(payload.get("uid", 0)) if str(payload.get("uid", 0)).isdigit() else 0
        client_name = payload.get("client", "unknown").strip()
        client_version = payload.get("version", "0.0")
        timestamp = tsnow()

        # convert list to dict and check keys
        # for all keys to be int
        if isinstance(items, list):
            items_list = items
            items = dict({})
            for item in items_list:
                for key in ["id", "quantity", "cost"]:
                    if not str(item.get(key)).isdigit():
                        return JsonResponse({"error": {"code": 2, "error": f"Wrong {key} for item object: {item.get(key)}"}}, status=400)

                items[int(item["id"])] = {"cost": int(item["cost"]), "quantity": int(item["quantity"])}

        elif isinstance(items, dict):
            # cast to int the keys
            cast_to_int = []
            for item_id, item in items.items():
                if not str(item_id).isdigit():
                    return JsonResponse({"error": {"code": 2, "error": f"Wrong item id {item_id}"}}, status=400)

                for key in ["quantity", "cost"]:
                    if not str(item.get(key)).isdigit():
                        return JsonResponse({"error": {"code": 2, "error": f"Wrong item {key} for item {item_id}"}}, status=400)

                item = {"cost": int(item["cost"]), "quantity": int(item["quantity"])}
                if not isinstance(item_id, int):
                    cast_to_int.append(item_id)

            # cast to int the keys
            for k in cast_to_int:
                items[int(k)] = items[k]
                del items[k]

        else:
            return JsonResponse({"error": {"code": 2, "error": "Expecting a POST request"}}, status=400)

        # get all unique items from this country
        distinct_items = [k["item_id"] for k in AbroadStocks.objects.filter(country_key=country_key).values("item_id").distinct()]

        # add items not in db
        # for all keys and values to be int
        for k in items:
            if k not in distinct_items:
                distinct_items.append(k)

        stocks = dict({})
        for item_id in distinct_items:
            if int(item_id) not in items_table[country_key]:
                continue
            item = items.get(item_id, False)
            cost = 0
            quantity = 0
            if item:
                cost = item["cost"]
                quantity = item["quantity"]
            else:
                lastItem = AbroadStocks.objects.filter(item_id=item_id, country_key=country_key).order_by("-timestamp").first()
                cost = 0 if lastItem is None else lastItem.cost
                quantity = 0

            stocks[item_id] = {"country": country, "country_key": country_key, "client": "{} [{}]".format(client_name, client_version), "timestamp": timestamp, "cost": cost, "quantity": quantity}

        client, _ = VerifiedClient.objects.get_or_create(name=client_name, version=client_version)
        client.update_author(payload)
        if client.verified:
            for k, v in stocks.items():
                item = Item.objects.filter(tId=k).first()
                if item is None:
                    return JsonResponse({"error": {"code": 2, "error": f"Item {k} not found in database"}}, status=400)

                AbroadStocks.objects.filter(item=item, country_key=v["country_key"], last=True).update(last=False)
                v["last"] = True
                item.abroadstocks_set.create(**v)

            # clear cloudflare cache
            # r = clear_cf_cache(["https://yata.yt/api/v1/travel/export/*"])
            # print("[api.travel.import] clear cloudflare cache", r)
            # print("[api.travel.import] clear droplet cache")
            cache.delete("foreign_stocks_payload")
            return JsonResponse({"message": f"The stocks have been updated with {client}"}, status=200)

        else:
            msg = f"Your client '{client_name} [{client_name}]' made a successful request but has not been added to the official API list. If you feel confident it's working correctly contact Kivou [2000607] to start updating the database."
            return JsonResponse({"message": msg, "stocks": stocks}, status=200)

    except BaseException as e:
        return JsonResponse({"error": {"code": 1, "error": str(e)}}, status=500)
