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

from chain.models import Crontab
from chain.models import Faction


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("[command.chain.crontab] start")
        openCrontab = Crontab.objects.filter(open=True).all()

        for crontab in openCrontab:
            print("[command.chain.crontab] {} cleared".format(crontab))
            crontab.faction.clear()

        for faction in Faction.objects.all().exclude(apiString="{}"):
            checkCrontab = faction.crontab_set.first()
            if checkCrontab is not None:
                print("[command.chain.crontab] faction {}: already on {}".format(faction, checkCrontab))
            elif faction.numberOfKeys:
                minBusy = min([c.nFactions() for c in openCrontab])
                for crontab in openCrontab:
                    if crontab.nFactions() == minBusy:
                        crontab.faction.add(faction)
                        crontab.save()
                        break
                print("[command.chain.crontab] faction {}: added to {}".format(faction, crontab))
                faction.createReport = bool(faction.numberOfReportsToCreate())
                faction.save()
                print("[command.chain.crontab] faction {}: createReport {}".format(faction, faction.createReport))
            else:
                print("[command.chain.crontab] faction {}: ignored (no keys)".format(faction))

        print("[command.chain.crontab] end")
