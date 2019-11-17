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
                armoryRaw = apiCall('faction', faction.tId, 'armorynewsfull', key, sub="armorynews", verbose=False)
                if 'apiError' in armoryRaw:
                    print(f"[command.chain.armory] {armoryRaw['apiError']}")
                    if armoryRaw['apiErrorCode'] in [1, 2, 7, 10]:
                        faction.delKey(keyHolder)
                    continue

                if faction.armoryRecord:
                    for k, v in json.loads(faction.armoryString).items():
                        if k not in armoryRaw:
                            armoryRaw[k] = v
                    faction.armoryString = json.dumps(armoryRaw)
                else:
                    faction.armoryString = "{}"
                faction.save()
            else:
                print("[command.chain.armory] No key")
                faction.armoryRecord = False
                faction.save()

        print("[command.chain.armory] end")
