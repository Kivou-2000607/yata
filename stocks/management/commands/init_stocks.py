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

from setup.functions import randomKey
from yata.handy import logdate
from yata.handy import apiCall
from stocks.models import Stock
from stocks.models import History

import json
import numpy
from scipy import stats


def lin_reg(stocks):
    xy = numpy.array([[s.timestamp, s.current_price] for s in stocks])
    slope, intercept, r_value, p_value, std_err = stats.linregress(xy[:, 0], xy[:, 1])
    a = slope * 3600  # $ / s * s / hours
    b = intercept

    return a, b


class Command(BaseCommand):
    def handle(self, **options):
        print(f'[CRON {logdate()}] START stocks')
        api_stocks = apiCall("torn", "", "stocks,timestamp", randomKey(), verbose=False)

        # init bulk manager
        batch_stocks = Stock.objects.bulk_operation()
        batch_history = History.objects.bulk_operation()

        # set rounded timestamp and period
        timestamp = api_stocks["timestamp"] - api_stocks["timestamp"] % 60
        periods = {
            "h": timestamp - 3600,
            "d": timestamp - 3600 * 24,
            "w": timestamp - 3600 * 24 * 7,
            "m": timestamp - 3600 * 24 * 7 * 31
        }

        # get all stocks and history
        stocks = Stock.objects.all()
        for api_stock in api_stocks.get("stocks"):
            acronym = api_stock["acronym"]

            # init defaults
            defaults = {
                "name": api_stock["name"],
                "current_price": api_stock["current_price"],
                "requirement": api_stock["benefit"]["requirement"],
                "description": api_stock["benefit"]["description"],
                "timestamp": timestamp
            }

            batch_stocks.update_or_create(acronym=acronym, defaults=defaults)

        if batch_stocks.count():
            batch_stocks.run()


        print(f'[CRON {logdate()}] END')


        # response = apiCall()
