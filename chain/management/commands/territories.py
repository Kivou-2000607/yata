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
from chain.models import Territory
from chain.models import Racket
from chain.models import FactionData
from yata.handy import apiCall


class Command(BaseCommand):
    def handle(self, **options):
        print("[command.chain.territories] start")

        territories = apiCall("torn", "", "territory,rackets", randomKey(), verbose=False)

        print("[command.chain.territories] update territories")
        allTerr = territories.get("territory", dict({}))
        allRack = territories.get("rackets", dict({}))
        n = len(allTerr)
        for i, (k, v) in enumerate(allTerr.items()):
            terr = Territory.objects.filter(tId=k).first()
            if terr is None:
                print(f"{i+1} / {n}: create territory {k}")
                terr = Territory.objects.create(tId=k, **v)
            else:
                print(f"{i+1} / {n}: update territory {k}")
                terr.faction = v.get("faction", 0)

            racket = allRack.get(k)
            if racket is None:
                terr.racket = json.dumps(dict({}))
            else:
                terr.racket = json.dumps(racket)

            terr.save()

        Racket.objects.all().delete()
        n = len(allRack)
        for i, (k, v) in enumerate(allRack.items()):
            print(f"{i+1} / {n}: create racket {k}")
            terr = Racket.objects.create(tId=k, **v)

        fd = FactionData.objects.first()
        fd.territoryTS = int(timezone.now().timestamp())
        fd.save()

        print("[command.chain.territories] end")
