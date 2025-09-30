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

import json

from django.core.management.base import BaseCommand
from django.utils import timezone

from bazaar.models import BazaarData, Item
from setup.functions import randomKey
from yata.handy import apiCall, logdate


class Command(BaseCommand):
    def handle(self, **options):
        print(f"[CRON {logdate()}] START items")

        points = apiCall("market", "", "pointsmarket", randomKey(), sub="pointsmarket")
        items = apiCall("torn", "", "items,timestamp", randomKey(), sub="items")

        typeItem = dict({})
        itemType = dict({})

        if items is None:
            print(f"[CRON {logdate()}] item is None")
        elif "apiError" in items:
            print(f"[CRON {logdate()}] api error: {items['apiError']}")
        else:

            bd = BazaarData.objects.first()

            total_price = 0
            total_points = 0
            for k, v in points.items():
                total_price += v["total_cost"]
                total_points += v["quantity"]
            bd.pointsValue = total_price // float(total_points)
            bd.save()

            for k, v in items.items():
                print(f'[CRON {logdate()}] Update {k} {v["name"]}')
                type = v["type"]
                name = v["name"].split(":")[0].strip()
                if type in typeItem:
                    if name not in typeItem[type]:
                        typeItem[type].append(name)
                else:
                    typeItem[type] = [name]
                itemType[name] = type
                req = Item.objects.filter(tId=int(k))
                if len(req) == 0:
                    item = Item.create(k, v)
                    item.save()
                elif len(req) == 1:
                    item = req[0]
                    item.update(v)
                    # if item.onMarket:
                    #     key = preference.get_random_key()[1]
                    #     item.update_bazaar(key=key, n=preference.nItems)
                    item.save()
                else:
                    print(f"[CRON {logdate()}]: request found more than one item id {len(req)}")
                    return 0

            bd.lastScanTS = int(timezone.now().timestamp())
            bd.save()

        # delete bazaar info for custom items refreshed more than 24h ago
        items = Item.objects.filter(onMarket=False).filter(lastUpdateTS__lt=(int(timezone.now().timestamp()) - 86400))
        for item in items:
            item.marketdata_set.all().delete()

        bd = BazaarData.objects.first()
        bd.typeItem = json.dumps(typeItem)
        bd.itemType = json.dumps(itemType)
        bd.save()

        # delete abroad stock that isnt the last entry
        for item in Item.objects.all():
            print(f"[CRON {logdate()}] Deleting old abroad stock for {item.tId} {item.tName}")
            item.abroadstocks_set.filter(last=False).delete()

        print(f"[CRON {logdate()}] END")
