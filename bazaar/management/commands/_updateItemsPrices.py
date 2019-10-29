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

from bazaar.models import Item


class Command(BaseCommand):
    def handle(self, **options):
        print("[command.bazaar.resetPrices] start")

        for item in Item.objects.all():
            print("[command.bazaar.resetPrices] reset prices of {} to {}".format(item, item.tMarketValue))
            now = int(timezone.now().timestamp())
            priceHistory = dict({})
            for i in range(31):
                t = now - i * 3600 * 24
                priceHistory[t] = item.tMarketValue
            item.priceHistory = json.dumps(priceHistory)
            item.save()

        print("[command.bazaar.resetPrices] end")
