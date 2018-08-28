from django.core.management.base import BaseCommand
from django.utils import timezone

from bazaar.models import Item
from bazaar.models import ItemUpdate


class Command(BaseCommand):
    def handle(self, **options):
        print("[COMMAND cleandb] start")

        # delete update items older than 24h
        for update in ItemUpdate.objects.filter(date__lt=timezone.now() - timezone.timedelta(days=1)):
            print("[COMMAND cleandb] deleting update {}".format(update))
            update.delete()

        # delete bazaar info for custom items refreshed more than 24h ago
        for item in Item.objects.filter(onMarket=False).filter(date__lt=timezone.now() - timezone.timedelta(days=1)):
            bazaar = item.marketdata_set.all()
            if len(bazaar):
                print("[COMMAND cleandb] deleting bazaar{}".format(item))
                bazaar.delete()

        print("[COMMAND cleandb] end")
