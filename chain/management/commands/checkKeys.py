from django.core.management.base import BaseCommand

from chain.models import Faction
from yata.handy import apiCall


class Command(BaseCommand):
    def handle(self, **options):
        print("[COMMAND checkKeys] start")

        for faction in Faction.objects.all():
            print("[COMMAND checkKeys] faction {}".format(faction))
            factionId = faction.tId

            # loop over keys
            for name, key in faction.get_all_pairs():
                call = apiCall("faction", factionId, "chain", key, sub="chain")
                if 'apiError' in call:
                    faction.toggle_key(name, key)
                    print('[COMMAND checkKeys] api key error: {}'.format((call['apiError'])))
                    print("[COMMAND checkKeys] {} key deleted".format(name))

                print("[COMMAND checkKeys] {} key ok".format(name))

            print("[COMMAND checkKeys] end")
