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

from chain.models import FactionData
from yata.handy import apiCall
from setup.functions import randomKey

import json
import re


class Command(BaseCommand):
    def handle(self, **options):
        print("[command.chain.updateUpgradeTree] start")
        upgradeTree = apiCall("torn", "", "factiontree", randomKey(), sub="factiontree")
        for k1, v1 in upgradeTree.items():
            for k2, v2 in v1.items():
                ch = v2["challenge"].replace(",", "").replace("$", "")

                # no challenge
                if ch in ["No challenge"]:
                    upgradeTree[k1][k2]["challengeprogress"] = [None, None]

                # Escape
                elif re.match(r'Run away \b(\d{1,4})\b times', ch):
                    key = "attacksrunaway"
                    val = int(ch.split(" ")[2])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Maximum Life
                elif re.match(r'Win \b(\d{1,6})\b damage receiving attacks or defends', ch):
                    key = "attacksdamaging"
                    val = int(ch.split(" ")[1])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Accuracy
                elif re.match(r'Achieve \b(\d{1,6})\b damaging hits', ch):
                    key = "attacksdamagehits"
                    val = int(ch.split(" ")[1])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Damage
                elif re.match(r'Deal \b(\d{1,10})\b damage', ch):
                    key = "attacksdamage"
                    val = int(ch.split(" ")[1])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Hospitalization
                elif re.match(r'Put opponents in hospital for \b(\d{1,10})\b hours', ch):
                    key = "hosptimegiven"
                    val = int(ch.split(" ")[5])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Training
                elif re.match(r'Spend \b(\d{1,9})\b energy on (\w{5,}) training', ch):
                    key = "gym" + ch.split(" ")[4]
                    val = int(ch.split(" ")[1])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Rehab cost
                elif re.match(r'Rehab \b(\d{1,9})\b times', ch):
                    key = "rehabs"
                    val = int(ch.split(" ")[1])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Travel cost
                elif re.match(r'Achieve \b(\d{1,9})\b hours of flight', ch):
                    key = "traveltime"
                    val = int(ch.split(" ")[1])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Oversea banking
                elif re.match(r'Receive \b(\d{1,9})\b in Cayman interest', ch):
                    key = "caymaninterest"
                    val = int(ch.split(" ")[1])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Hunting
                elif re.match(r'Hunt \b(\d{1,9})\b times', ch):
                    key = "hunting"
                    val = int(ch.split(" ")[1])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Overdosing
                elif re.match(r'Overdose \b(\d{1,9})\b times', ch):
                    key = "drugoverdoses"
                    val = int(ch.split(" ")[1])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Side Effect
                elif re.match(r'Take \b(\d{1,9})\b drugs', ch):
                    key = "drugsused"
                    val = int(ch.split(" ")[1])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Alcohol effect
                elif re.match(r'Use \b(\d{1,9})\b bottles of alcohol', ch):
                    key = "alcoholused"
                    val = int(ch.split(" ")[1])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Energy drink effect
                elif re.match(r'Use \b(\d{1,9})\b cans of energy drink', ch):
                    key = "energydrinkused"
                    val = int(ch.split(" ")[1])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Candy effect
                elif re.match(r'Use \b(\d{1,9})\b bags of candy', ch):
                    key = "candyused"
                    val = int(ch.split(" ")[1])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Medical effectiveness
                elif re.match(r'Receive \b(\d{1,9})\b hours of hospital time', ch):
                    key = "hosptimereceived"
                    val = int(ch.split(" ")[1])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Life regeneration
                elif re.match(r'Recover \b(\d{1,9})\b life using medical items', ch):
                    key = "medicalitemrecovery"
                    val = int(ch.split(" ")[1])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Reviving
                elif re.match(r'Revive \b(\d{1,9})\b people', ch):
                    key = "revives"
                    val = int(ch.split(" ")[1])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Medical cooldown
                elif re.match(r'Utilize \b(\d{1,9})\b hours of medical cooldown', ch):
                    key = "medicalcooldownused"
                    val = int(ch.split(" ")[1])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Bust skill/nerve
                elif re.match(r'Bust \b(\d{1,9})\b people from jail', ch):
                    key = "busts"
                    val = int(ch.split(" ")[1])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Jail time
                elif re.match(r'Receive \b(\d{1,9})\b(\s{1,2})jail sentences', ch):
                    key = "jails"
                    val = int(ch.split(" ")[1])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Nerve
                elif re.match(r'Commit \b(\d{1,9})\b offences', ch):
                    key = "criminaloffences"
                    val = int(ch.split(" ")[1])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Territory
                elif re.match(r'Hold \b([a-z\-]{1,})\b territor', ch):
                    key = "highestterritories"
                    val = int(v2["ability"].split(" ")[4]) - 1
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Capacity
                elif re.match(r'Achieve a faction age of \b(\d{1,9})\b days', ch):
                    key = "age"
                    val = int(ch.split(" ")[5])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Chaining
                elif re.match(r'Achieve a chain of \b(\d{1,9})', ch):
                    key = "best_chain"
                    val = int(ch.split(" ")[4])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                # Laboratory
                elif re.match(r'Acquire \b(\d{1,9}) faction members', ch):
                    key = "members"
                    val = int(ch.split(" ")[1])
                    upgradeTree[k1][k2]["challengeprogress"] = [key, val]

                else:
                    print(k2, v2)

        # for k1, v1 in upgradeTree.items():
        #     print(k1)
        #     for k2, v2 in v1.items():
        #         print(k2, v2)

        factionData = FactionData.objects.first()
        factionData.upgradeTree = json.dumps(upgradeTree)
        factionData.save()

        # upgradeTree = json.loads(FactionData.objects.first().upgradeTree)

        # for k1, v1 in upgradeTree.items():
        #     print(k1)
        #     for k2, v2 in v1.items():
        #         print("\t", k2, v2)

        print("[command.chain.updateUpgradeTree] end")
