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

import requests
from stocks.models import History
from stocks.models import Stock
import json

class Command(BaseCommand):
    def handle(self, **options):

        api_stocks = json.load(open("airport_stocks.json", "r"))

        history = History.objects.all()
        n = len(api_stocks)
        for i, s in enumerate(api_stocks):
            ts = s["fields"]["timestamp"]

            # record history
            defaults = {
                "current_price": s["fields"]["current_price"],
                "market_cap": s["fields"]["market_cap"],
                "total_shares": s["fields"]["total_shares"],
            }
            print(i, n, History.objects.update_or_create(stock_id=s["fields"]["stock"], timestamp=s["fields"]["timestamp"], defaults=defaults))

        # if batch_history.count():
        #     print("batch run")
        #     batch_history.run(batch_size=100)
        #     print("batch done")
