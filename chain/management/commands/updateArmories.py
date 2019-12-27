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

from chain.models import Faction
from yata.handy import apiCall

import json


class Command(BaseCommand):
    def handle(self, **options):
        print("[command.chain.armory] start")
        for faction in Faction.objects.filter(armoryRecord=True).only("armoryString", "armoryRecord"):
            print("[command.chain.armory] faction {}".format(faction))
            # armoryRecord(faction)

            keyHolder, key = faction.getRandomKey()

            if key:
                factionInfo = apiCall('faction', faction.tId, 'armorynewsfull,fundsnewsfull,donations,currency,basic', key, verbose=False)

                # handle error
                if 'apiError' in factionInfo:
                    print("[command.chain.armory] {}".format(factionInfo['apiError']))
                    if factionInfo['apiErrorCode'] in [1, 2, 7, 10]:
                        faction.delKey(keyHolder)
                    continue

                if faction.armoryRecord:

                    armoryInfo = factionInfo.get("armorynews")
                    fundsInfo = factionInfo.get("fundsnews")

                    # record armory
                    for k, v in json.loads(faction.armoryString).items():
                        if k not in armoryInfo:
                            armoryInfo[k] = v
                    faction.armoryString = json.dumps(armoryInfo)

                    # record funds
                    for k, v in json.loads(faction.fundsString).items():
                        if k not in fundsInfo:
                            fundsInfo[k] = v
                    faction.fundsString = json.dumps(fundsInfo)

                    # record networth and respect
                    totalDonations = 0
                    totalVault = factionInfo.get("money", 0)
                    for k, v in factionInfo.get("donations", dict({})).items():
                        totalDonations += int(v["money_balance"])

                    ts = int(timezone.now().timestamp())
                    ts = int(ts) - int(ts) % (3600 * 24)  # round to the day

                    tmp = json.loads(faction.networthString)
                    for k, v in tmp.items():
                        if len(v) == 2:
                            v.append(factionInfo.get("respect", 0))
                    tmp[str(ts)] = [totalVault, totalDonations, factionInfo.get("respect", 0)]
                    faction.networthString = json.dumps(tmp)

                else:
                    faction.networthString = "{}"
                    faction.armoryString = "{}"
                    faction.fundsString = "{}"

                faction.save()
            else:
                print("[command.chain.armory] No key")
                faction.armoryRecord = False
                faction.save()

        print("[command.chain.armory] end")
