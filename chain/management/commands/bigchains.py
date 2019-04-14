from django.core.management.base import BaseCommand

from chain.models import Faction

from chain.functions import apiCallAttacks
from chain.functions import fillReport
from chain.functions import updateMembers


class Command(BaseCommand):
    def handle(self, **options):
        print("[COMMAND bigChains] start")

        for faction in Faction.objects.all():
            print("[COMMAND bigChains] faction {}".format(faction))

            # get api key
            if faction.apiString == "0":
                print("[COMMAND bigChains] no api key found")
                continue
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
                # members = faction.member_set.all()

                # update members
                members = updateMembers(faction)
                if 'apiError' in members:
                    print("[COMMAND bigChains] error in API continue to next chain: {}", members['apiError'])
                    continue

                attacks = apiCallAttacks(faction, chain, chain.start, chain.end)

                fillReport(faction, members, chain, report, attacks)

                chain.createReport = False
                chain.save()

                break  # do just one chain report / call

            print("[COMMAND bigChains] end")
