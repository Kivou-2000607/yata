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
from django.conf import settings

import json
import os

from setup.functions import randomKey
from faction.models import *
from yata.handy import apiCall
from yata.handy import logdate


class Command(BaseCommand):
    def handle(self, **options):
        print(f"[CRON {logdate()}] START territories")

        territories = apiCall("torn", "", "territory,rackets", randomKey(), verbose=False)
        #
        allTerr = territories.get("territory", dict({}))
        allRack = territories.get("rackets", dict({}))
        n = len(allTerr)
        for i, (k, v) in enumerate(allTerr.items()):
            v["racket"] = json.dumps(allRack.get(k, dict({})))
            terr, _ = Territory.objects.update_or_create(tId=k, defaults=v)
            print(f"[CRON {logdate()}] {i + 1}/{n} {terr}")

        # delete old racket
        for r in Racket.objects.only("tId").all():
            if r.tId not in allRack:
                print(f"[CRON {logdate()}] Delete {r}")
                r.delete()

        n = len(allRack)
        for i, (k, v) in enumerate(allRack.items()):
            if v.get("war", False):
                v["assaulting_faction"] = v["war"]["assaulting_faction"]
                v["defending_faction"] = v["war"]["defending_faction"]
                v["started"] = v["war"]["started"]
                v["ends"] = v["war"]["ends"]
                v["war"] = True
            else:
                v["war"] = False
                v["assaulting_faction"] = 0
                v["defending_faction"] = 0
                v["started"] = 0
                v["ends"] = 0

            r, _ = Racket.objects.update_or_create(tId=k, defaults=v)
            print(f"[CRON {logdate()}] {i + 1}/{n} {r}")

        fd = FactionData.objects.first()
        fd.territoryUpda = tsnow()
        fd.save()

        print(f"[CRON {logdate()}] END")
