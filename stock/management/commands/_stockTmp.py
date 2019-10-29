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

from stock.models import Stock
from stock.models import History


class Command(BaseCommand):
    def handle(self, **options):
        print("[command.stock.tmp] start")

        for stock in Stock.objects.all():
            prices = json.loads(stock.priceHistory)
            quanti = json.loads(stock.quantityHistory)
            for k, v in prices.items():
                if len(stock.history_set.filter(timestamp=int(k))) == 0:
                    print("create", k, v)
                    stock.history_set.create(tCurrentPrice=float(v),
                                             tAvailableShares=int(quanti.get(k, 0)),
                                             timestamp=int(k))

        print("[command.stock.tmp] end")
