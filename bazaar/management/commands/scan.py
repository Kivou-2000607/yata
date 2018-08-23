from django.core.management.base import BaseCommand

import requests
from bazaar.models import Item
from bazaar.models import Config

class Command(BaseCommand):
    def handle(self, **options):
        print("[COMMAND scan] start")

        conf = Config.objects.all()[0]

        request_url = "https://api.torn.com/torn/?selections=items&key={}".format(conf.apiKey)
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
                print("[COMMAND scan]: request found more than one item id", len(req))
                exit()

        lastScan = conf.update_last_scan()

        print("[COMMAND scan] end")
