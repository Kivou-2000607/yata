from django.core.management.base import BaseCommand
from django.utils import timezone

from chain.models import Crontab

from chain.functions import apiCallAttacks
from chain.functions import fillReport
from chain.functions import updateMembers
from yata.handy import apiCall

import random


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('crontab', type=int)

    def handle(self, *args, **options):
        crontabId = options['crontab']
        print("[command.chain.livereport] open crontab {}".format(crontabId))

        # get crontab
        crontab = Crontab.objects.filter(id=crontabId).first()
        factions = [faction for faction in crontab.faction.all()]

        n = len(factions)
        factions = random.sample(factions, n)

        for f in factions:
            print("[command.chain.livereport] --> {}".format(f))

        for i, faction in enumerate(factions):
            print("[command.chain.livereport] #{}: {}".format(i + 1, faction))

            # get api key
            if faction.apiString == "0":
                print("[command.chain.livereport]    --> no api key found")

            else:
                keyHolder, key = faction.getRadomKey()

                # live chains
                liveChain = apiCall("faction", faction.tId, "chain", key, sub="chain")
                if 'apiError' in liveChain:
                    print('[command.chain.livereport] api key error: {}'.format((liveChain['apiError'])))

                elif int(liveChain["current"]) < 10:
                    print('[command.chain.livereport]    --> no live report')
                    faction.chain_set.filter(tId=0).delete()

                else:
                    # get chain
                    print('[command.chain.livereport]    --> live report')
                    chain = faction.chain_set.filter(tId=0).first()
                    if chain is None:
                        print('[command.chain.livereport]   --> create chain 0')
                        chain = faction.chain_set.create(tId=0)

                    chain.status = True
                    chain.end = int(timezone.now().timestamp())
                    chain.start = int(liveChain.get("start"))
                    chain.nHits = int(liveChain.get("current"))
                    # chain.createReport = True
                    chain.save()

                    # delete old report and create new
                    report = chain.report_set.first()
                    if report is None:
                        report = chain.report_set.create()
                        print('[command.chain.livereport]    --> new report created')
                    else:
                        print('[command.chain.livereport]    --> report found')

                    # update members
                    print("[command.chain.livereport]    --> udpate members")
                    members = updateMembers(faction, key=key)
                    if 'apiError' in members:
                        print("[command.chain.livereport]    --> error in API continue to next chain: {}".format(members['apiError']))
                        if members['apiError'].split(":")[0] == "API error code 2":
                            print("[command.chain.livereport]    --> deleting {}'s key'".format(keyHolder))
                            faction.delKey()
                        continue

                    print(chain)
                    attacks = apiCallAttacks(faction, chain)

                    if "error" in attacks:
                        print("[command.chain.livereport]    --> error apiCallAttacks: {}".format(attacks["error"]))
                    else:
                        fillReport(faction, members, chain, report, attacks)

                    chain.save()

                    print("[command.chain.livereport] end after report")
                    return
                    # break  # do just one chain report / call

        print("[command.chain.livereport] end after nothing")
