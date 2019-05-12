from django.core.management.base import BaseCommand

from chain.models import Crontab

from chain.functions import apiCallAttacks
from chain.functions import fillReport
from chain.functions import updateMembers

import random


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('crontab', type=int)

    def handle(self, *args, **options):
        crontabId = options['crontab']
        print("[COMMAND updatechains] open crontab {}".format(crontabId))

        # get crontab
        crontab = Crontab.objects.filter(id=crontabId).first()
        factions = [faction for faction in crontab.faction.all()]

        n = len(factions)
        factions = random.sample(factions, n)

        for f in factions:
            print("[COMMAND updatechains] --> {}".format(f))

        for i, faction in enumerate(factions):
            print("[COMMAND updatechains] #{}: {}".format(i + 1, faction))

            # get api key
            if faction.apiString == "0":
                print("[COMMAND updatechains]     --> no api key found")

            else:
                keyHolder, key = faction.getRadomKey()

                # get all chain
                chains = faction.chain_set.filter(createReport=True).all()
                print('[COMMAND updatechains]     --> {} reports to create'.format(len(chains)))
                for chain in chains:
                    # delete old report and create new
                    print('[COMMAND updatechains]     --> report {}'.format(chain))
                    report = chain.report_set.first()
                    if report is None:
                        report = chain.report_set.create()
                        print('[COMMAND updatechains]     --> new report')
                    else:
                        print('[COMMAND updatechains]     --> report found')

                    # update members
                    print("[COMMAND updatechains]     --> udpate members")
                    members = updateMembers(faction, key=key)
                    if 'apiError' in members:
                        print("[COMMAND updatechains]     --> error in API continue to next chain: {}".format(members['apiError']))
                        if members['apiError'].split(":")[0] == "API error code 2":
                            print("[COMMAND updatechains]     --> deleting {}'s key'".format(keyHolder))
                            faction.delKey()
                        continue

                    attacks = apiCallAttacks(faction, chain)

                    if "error" in attacks:
                        print("[COMMAND updatechains]     --> error apiCallAttacks: {}".format(attacks["error"]))
                    else:
                        _, _, _, finished = fillReport(faction, members, chain, report, attacks)
                        print("[COMMAND updatechains]     --> report finished: {}".format(finished))
                        chain.createReport = not finished

                    chain.save()

                    print("[COMMAND updatechains] end after report")
                    return
                    # break  # do just one chain report / call

        print("[COMMAND updatechains] end after nothing")
