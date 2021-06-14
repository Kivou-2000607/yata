"""
Copyright 2020 kivou.2000607@gmail.com

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

from django.core import serializers
from stocks.models import History

import json

class Command(BaseCommand):
    def handle(self, **options):

        stocks = {}
        for stock in History.objects.filter(timestamp__gt=1619740800):
            if stock.stock.acronym not in stocks:
                stocks[stock.stock.acronym] = []

            stocks[stock.stock.acronym].append([stock.timestamp, stock.current_price, stock.market_cap])


        json.dump(stocks, open("stocks.json", "w"))
