from django.core.management.base import BaseCommand
from django.utils import timezone

from bazaar.models import Item
from bazaar.models import Preference
from yata.handy import apiCall


class Command(BaseCommand):
    def handle(self, **options):
        print("[command.bazaar.scan] start")

        preference = Preference.objects.all()[0]

        items = apiCall("torn", "", "items", preference.key, sub="items")

        if items is None:
            print("[command.bazaar.scan] item is None")
        elif 'apiError' in items:
            print("[command.bazaar.scan] api error: {}".format(items["apiError"]))
        else:
            for k, v in items.items():
                # req = Item.objects.filter(tId=int(k))
                # if len(req) == 0:
                #     item = Item.create(k, v)
                #     item.save()
                # elif len(req) == 1:
                #     item = req[0]
                #     item.update(v)
                #     if item.onMarket:
                #         item.update_bazaar(key=preference.key)
                #     item.save()
                # else:
                #     print("[command.bazaar.scan]: request found more than one item id", len(req))
                #     return 0

            preference.lastScanTS = int(timezone.now().timestamp())
            preference.save()

        # delete bazaar info for custom items refreshed more than 24h ago
        for item in Item.objects.filter(onMarket=False).filter(lastUpdateTS__lt=(int(timezone.now().timestamp()) - 3600*24)):
            item.marketdata_set.all().delete()

        print("[command.bazaar.scan] end")
