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

from chain.functions import apiCallAttacksV2
from chain.models import Faction
from chain.models import AttacksBreakdown
# from chain.functions import fillReport
# from chain.functions import updateMembers
# from chain.functions import API_CODE_DELETE
# from yata.handy import apiCall

import random


class Command(BaseCommand):
    def handle(self, **options):
        print("[command.faction.revives]")

        # get all breakdowns
        breakdowns = [c for c in AttacksBreakdown.objects.filter(computing=True)]

        # no contract to compute
        if not len(breakdowns):
            print("[command.faction.revives] no breakdowns to compute")
            return

        # get a single contract
        breakdown = random.choice(breakdowns)
        print("[command.faction.revives] {}".format(breakdown))

        # compute revives
        result, message = apiCallAttacksV2(breakdown)

        if result:
            print("[command.chain.revives] end with success")
        else:
            print("[command.chain.revives] end badly: {}".format(message))
