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

from company.models import *
from setup.functions import randomKey
from yata.handy import apiCall

class Command(BaseCommand):
    def handle(self, **options):
        print(randomKey())
        companies = apiCall("torn", "", "companies", randomKey())
        # print(companies)
        for k, v in companies["companies"].items():
            positions = v["positions"]
            specials = v["specials"]
            for k1, v1 in v["stock"].items():
                v1["cost"] = 0 if v1["cost"] == "" else v1["cost"]
            stocks = v["stock"]
            del v["positions"]
            del v["specials"]
            del v["stock"]
            # print(k, v)
            # print(stock)
            # print(positions)
            # print(specials)

            company, create = CompanyDescription.objects.update_or_create(tId=k, defaults=v)
            print(company, create)
            for k1, v1 in positions.items():
                position, create = company.position_set.update_or_create(name=k1, defaults=v1)
                print("\t", position, create)
            for k1, v1 in stocks.items():
                stocks, create = company.stock_set.update_or_create(name=k1, defaults=v1)
                print("\t", stocks, create)
            for k1, v1 in specials.items():
                special, create = company.special_set.update_or_create(name=k1, defaults=v1)
                print("\t", special, create)
