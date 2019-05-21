"""
Copyright 2019 Kivou-2000607@gmail.com

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
        print("[command.chain.chainreport] open crontab {}".format(crontabId))

        # get crontab
        crontab = Crontab.objects.filter(tabNumber=crontabId).first()
        try:
            factions = [faction for faction in crontab.faction.all()]
        except:
            print("[command.chain.chainreport] no crontab found")
            return

        n = len(factions)
        factions = random.sample(factions, n)

        for f in factions:
            print("[command.chain.chainreport] --> {}".format(f))

        for i, faction in enumerate(factions):
            print("[command.chain.chainreport] #{}: {}".format(i + 1, faction))

            # get api key
            if faction.apiString == "0":
                print("[command.chain.chainreport]    --> no api key found")

            else:
                keyHolder, key = faction.getRadomKey()

                # get all chain
                chains = faction.chain_set.filter(createReport=True).all()
                print('[command.chain.chainreport]    --> {} reports to create'.format(len(chains)))
                for chain in chains:
                    # delete old report and create new
                    print('[command.chain.chainreport]    --> report {}'.format(chain))
                    report = chain.report_set.first()
                    if report is None:
                        report = chain.report_set.create()
                        chain.hasReport = True
                        print('[command.chain.chainreport]    --> new report')
                    else:
                        print('[command.chain.chainreport]    --> report found')

                    # update members
                    print("[command.chain.chainreport]    --> udpate members")
                    members = updateMembers(faction, key=key)
                    if 'apiError' in members:
                        print("[command.chain.chainreport]    --> error in API continue to next chain: {}".format(members['apiError']))
                        if members['apiError'].split(":")[0] == "API error code 2":
                            print("[command.chain.chainreport]    --> deleting {}'s key'".format(keyHolder))
                            faction.delKey()
                        continue

                    attacks = apiCallAttacks(faction, chain)

                    if "error" in attacks:
                        print("[command.chain.chainreport]    --> error apiCallAttacks: {}".format(attacks["error"]))
                    else:
                        _, _, _, finished = fillReport(faction, members, chain, report, attacks)
                        print("[command.chain.chainreport]    --> report finished: {}".format(finished))
                        chain.createReport = not finished

                    chain.save()

                    print("[command.chain.chainreport] end after report")
                    return
                    # break  # do just one chain report / call

        print("[command.chain.chainreport] end after nothing")
