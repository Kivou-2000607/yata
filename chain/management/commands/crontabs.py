from django.core.management.base import BaseCommand

from chain.models import Crontab
from chain.models import Faction


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("[command.chain.crontab] start")

        for crontab in Crontab.objects.all():
            print("[command.chain.crontab] {} cleared".format(crontab))
            crontab.faction.clear()

        for faction in Faction.objects.exclude(apiString="{}"):
            minBusy = min([c.nFactions() for c in Crontab.objects.all()])
            for crontab in Crontab.objects.all():
                if crontab.nFactions() == minBusy:
                    crontab.faction.add(faction)
                    crontab.save()
                    break
            print("[command.chain.crontab] faction {} added to {}".format(faction, crontab))

        print("[command.chain.crontab] end")
