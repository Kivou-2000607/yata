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

from chain.functions import apiCallRevives
from chain.models import Faction
from chain.models import ReviveContract
# from chain.functions import fillReport
# from chain.functions import updateMembers
# from chain.functions import API_CODE_DELETE
# from yata.handy import apiCall

import random


class Command(BaseCommand):
    def handle(self, **options):
        print("[command.faction.revives]")

        # get all contracts
        contracts = [c for c in ReviveContract.objects.filter(computing=True)]

        # no contract to compute
        if not len(contracts):
            print("[command.faction.revives] no contracts to compute")
            return

        # get a single contract
        contract = random.choice(contracts)
        print("[command.faction.revives] {}".format(contract))

        # compute revives
        result, message = apiCallRevives(contract)

        if result:
            print("[command.chain.revives] end with success")
        else:
            print("[command.chain.revives] end badly: {}".format(message))
