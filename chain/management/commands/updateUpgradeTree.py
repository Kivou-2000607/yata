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


class Command(BaseCommand):
    def handle(self, **options):
        print("[command.chain.updateUpgradeTree] start")
        upgradeTree = apiCall("torn", "", "factiontree", randomKey(), sub="factiontree")
        factionData = FactionData.objects.first()
        factionData.upgradeTree = json.dumps(upgradeTree)
        factionData.save()

        # upgradeTree = json.loads(FactionData.objects.first().upgradeTree)

        # for k1, v1 in upgradeTree.items():
        #     print(k1)
        #     for k2, v2 in v1.items():
        #         print("\t", k2, v2)

        print("[command.chain.updateUpgradeTree] end")
