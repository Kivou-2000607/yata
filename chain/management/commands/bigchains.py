from django.core.management.base import BaseCommand
from django.utils import timezone

from chain.models import Faction
from yata.handy import apiCall
from yata.handy import apiCallAttacks
from yata.handy import timestampToDate

from yata.handy import fillReport


class Command(BaseCommand):
    def handle(self, **options):
        print("[COMMAND bigChains] start")

        for faction in Faction.objects.all():
            print("[COMMAND bigChains] faction {}".format(faction))

            # get api key
            if faction.apiString == "0":
                print("[COMMAND bigChains] no api key found")
                break
            factionId = faction.tId
            keyHolder, key = faction.get_random_key()

            # get all chain
            print('[COMMAND bigChains] get big chains')
            chains = faction.chain_set.filter(createReport=True).all()
            for chain in chains:
                # delete old report and create new
                print('[COMMAND bigChains] create big chain report: {}'.format(chain))
                chain.report_set.all().delete()
                report = chain.report_set.create()
                print('[COMMAND bigChains] new report created')

                # get members (no refresh)
                membersDB = faction.member_set.all()

                attacks = apiCallAttacks(factionId, chain.start, chain.end, key)

                fillReport(faction, membersDB, chain, report, attacks)

                chain.createReport = False
                chain.save()

                break  # do just one chain report / call

            print("[COMMAND bigChains] end")
