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

from faction.models import Faction
from yata.handy import logdate


class Command(BaseCommand):
    def handle(self, **options):
        print(f"[CRON {logdate()}] START factions")
        for faction in Faction.objects.filter(nKeys__gt=0):
            print(f"[CRON {logdate()}] faction {faction}")
            try:
                # print(f"[CRON {logdate()}] faction {faction}: clean history")
                faction.cleanHistory()
                # print(f"[CRON {logdate()}] faction {faction}: check keys")
                faction.checkKeys()
                if faction.nKeys:
                    # print(f"[CRON {logdate()}] faction {faction}: update logs")
                    faction.updateLog()

                    # print(f"[CRON {logdate()}] faction {faction}: update crimes")
                    if faction.useOC2:
                        faction.updateCrimesv2()
                    else:
                        faction.updateCrimes()

                    # print(f"[CRON {logdate()}] faction {faction}: update members")
                    faction.updateMembers()

                    # print(f"[CRON {logdate()}] faction {faction}: update upgrades")
                    # faction.updateUpgrades()
                    # faction.resetSimuUpgrades(update=True)
                    # faction.getFactionTree()
                # else:
                #     print(f"[CRON {logdate()}] faction {faction}: no more keys")
            except BaseException as e:
                print(f"[CRON {logdate()}] {e}")

        print(f"[CRON {logdate()}] END")
