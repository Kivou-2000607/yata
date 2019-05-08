from django.core.management.base import BaseCommand

import requests
from bazaar.models import Item
from bazaar.models import Config

class Command(BaseCommand):
    def handle(self, **options):
        print("[command.bazaar.scan] start")

        conf = Config.objects.fisrt()

        request_url = "https://api.torn.com/torn/?selections=items&key={}".format(conf.apiKey)
        items = requests.get(request_url).json().get('items')

        if items is None:
            print("[command.bazaar.scan] api key error: {}".format(items["apiError"]))
            return 0
        else:
            for k, v in items.items():
                req = Item.objects.filter(tId=int(k))
                if len(req) == 0:
                    item = Item.create(k, v)
                    item.save()
                elif len(req) == 1:
                    item = req[0]
                    item.update(k, v)
                    if item.onMarket:
                        item.update_bazaar(key=conf.apiKey)
                    item.save()
                else:
                    print("[Ccommand.bazaar.scan]: request found more than one item id", len(req))
                    exit()

            lastScan = conf.update_last_scan()

            print("[Ccommand.bazaar.scan] end")
            return 1
