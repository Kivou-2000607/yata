"""
Copyright 2019 kivou.2000607@gmail.com

This file is part of yata.

    yata is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    yata is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with yata. If not, see <https://www.gnu.org/licenses/>.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from chain.models import Crontab

from chain.functions import apiCallAttacks
from chain.functions import fillReport
from chain.functions import updateMembers
from chain.functions import API_CODE_DELETE
from yata.handy import apiCall

import random


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('crontab', type=int)

    def handle(self, *args, **options):
        crontabId = options['crontab']
        print("[command.chain.livereport] open crontab {}".format(crontabId))

        # get crontab
        crontab = Crontab.objects.filter(tabNumber=crontabId).first()
        try:
            factions = [faction for faction in crontab.faction.filter(createLive=True)]
        except BaseException:
            print("[command.chain.livereport] no crontab found")
            return

        n = len(factions)
        factions = random.sample(factions, n)

        # for f in factions:
        #     print("[command.chain.livereport] --> {}".format(f))

        for i, faction in enumerate(factions):
            print("[command.chain.livereport] #{}: {}".format(i + 1, faction))

            # get api key
            if not faction.numberOfKeys:
                faction.createLive = False
                faction.save()
                print("[command.chain.livereport]    --> no api key found")

            else:
                keyHolder, key = faction.getRandomKey()

                # live chains
                liveChain = apiCall("faction", faction.tId, "chain", key, sub="chain")
                if 'apiError' in liveChain:
                    print('[command.chain.livereport] api key error: {}'.format((liveChain['apiError'])))
                    if liveChain['apiErrorCode'] in API_CODE_DELETE:
                        print("[command.chain.livereport]    --> deleting {}'s key'".format(keyHolder))
                        faction.delKey(keyHolder)

                elif int(liveChain["current"]) < 10:
                    print('[command.chain.livereport]    --> no live report')
                    faction.activeChain = False
                    faction.createLive = False
                    faction.chain_set.filter(tId=0).delete()
                    faction.save()

                elif not faction.createLive:
                    print('[command.chain.livereport]    --> creation of live report off')
                    faction.chain_set.filter(tId=0).delete()
                    faction.activeChain = True
                    faction.save()

                else:
                    # get chain
                    print('[command.chain.livereport]    --> live report')
                    faction.activeChain = True
                    faction.save()
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
                        chain.hasReport = True
                        print('[command.chain.livereport]    --> new report created')
                    else:
                        print('[command.chain.livereport]    --> report found')

                    # update members
                    print("[command.chain.livereport]    --> udpate members")
                    members = updateMembers(faction, key=key, force=False)
                    # members = faction.member_set.all()
                    if 'apiError' in members:
                        print("[command.chain.livereport]    --> error in API continue to next chain: {}".format(members['apiError']))
                        if members['apiErrorCode'] in API_CODE_DELETE:
                            print("[command.chain.livereport]    --> deleting {}'s key'".format(keyHolder))
                            faction.delKey(keyHolder)
                        continue

                    attacks = apiCallAttacks(faction, chain)

                    if "apiError" in attacks:
                        print("[command.chain.livereport]    --> error apiCallAttacks: {}".format(attacks["apiError"]))
                        if attacks['apiErrorCode'] in API_CODE_DELETE:
                            print("[command.chain.livereport]    --> deleting {}'s key'".format(keyHolder))
                            faction.delKey(keyHolder)

                    elif "error" in attacks:
                        print("[command.chain.livereport]    --> error apiCallAttacks: {}".format(attacks["error"]))
                        print("[command.chain.livereport]    --> deleting report")
                        faction.chain_set.filter(tId=0).delete()

                    else:
                        fillReport(faction, members, chain, report, attacks)

                    chain.save()

                    print("[command.chain.livereport] end after report")
                    return
                    # break  # do just one chain report / call

        print("[command.chain.livereport] end after nothing")
