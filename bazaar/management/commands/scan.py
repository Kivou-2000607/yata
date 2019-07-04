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

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

import json
import os

from bazaar.models import Item
from bazaar.models import Preference
from yata.handy import apiCall


class Command(BaseCommand):
    def handle(self, **options):
        print("[command.bazaar.scan] start")

        preference = Preference.objects.all()[0]

        key = preference.get_random_key()[1]
        items = apiCall("torn", "", "items", key, sub="items")

        itemType = dict({})

        if items is None:
            print("[command.bazaar.scan] item is None")
        elif 'apiError' in items:
            print("[command.bazaar.scan] api error: {}".format(items["apiError"]))
        else:
            for k, v in items.items():
                print(k, v)
                type = v["type"]
                name = v["name"].split(":")[0].strip()
                if type in itemType:
                    if name not in itemType[type]:
                        itemType[type].append(name)
                else:
                    itemType[type] = [name]
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
                    print("[command.bazaar.scan]: request found more than one item id", len(req))
                    return 0

            preference.lastScanTS = int(timezone.now().timestamp())
            preference.save()

        # delete bazaar info for custom items refreshed more than 24h ago
        items = Item.objects.filter(onMarket=False).filter(lastUpdateTS__lt=(int(timezone.now().timestamp()) - 86400))
        for item in items:
            item.marketdata_set.all().delete()

        file = os.path.join(settings.PROJECT_ROOT, 'static/items/itemTypes.json')
        with open(file, 'w') as fp:
            json.dump(itemType, fp)

        print("[command.bazaar.scan] end")
