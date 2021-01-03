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
from setup.functions import randomKey
from yata.handy import apiCall
from yata.handy import logdate


class Command(BaseCommand):
    def handle(self, **options):
        print(f"[CRON {logdate()}] START stocks")

        stocks = apiCall("torn", "", "stocks,timestamp", randomKey())
        for k, v in stocks["stocks"].items():
            stock = Stock.objects.filter(tId=int(k)).first()
            if stock is None:
                stock = Stock.create(k, v, stocks["timestamp"])
            else:
                stock.update(k, v, stocks["timestamp"])
            stock.save()

        print(f"[CRON {logdate()}] END")
