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
import re

from setup.functions import randomKey
from faction.models import *
from yata.handy import apiCall


class Command(BaseCommand):
    def handle(self, **options):

        # api call
        upgrades = apiCall('torn', '', 'factiontree', key=randomKey(), sub="factiontree")
        if 'apiError' in upgrades:
            print("upgrades {}".format(upgrades))
            return False

        # get max level
        maxlevel = dict()
        for tId, upgrade in upgrades.items():
            maxlevel[tId] = 0
            for level, v in upgrade.items():
                # compute max level
                maxlevel[tId] = max(maxlevel[tId], int(level))

                # get short name
                splt = v["name"].split(" ")
                v["shortname"] = " ".join(splt[:-1]) if re.match(r"([IVX]{1,5})", splt[-1]) else v["name"]
                v["shortname"] = v["shortname"].strip()

                # update database
                print(FactionTree.objects.update_or_create(tId=tId, level=level, defaults=v))

        # update database with max level
        for tId, level in maxlevel.items():
            FactionTree.objects.filter(tId=tId).update(maxlevel=level)
