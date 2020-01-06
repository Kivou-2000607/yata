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
from chain.functions import factionTree

import json


class Command(BaseCommand):
    def handle(self, **options):
        print("[command.chain.tree] start")
        for faction in Faction.objects.filter(poster=True).exclude(posterHold=True):
            print("[command.chain.tree] faction {}".format(faction))
            factionTree(faction)

        print("[command.chain.tree] end")
