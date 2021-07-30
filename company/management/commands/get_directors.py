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

from player.models import Player
from company.models import *
from setup.functions import randomKey
from yata.handy import apiCall
import json

class Command(BaseCommand):
    def handle(self, **options):

        companies = {}

        directors = Player.objects.filter(companyDi=True)
        for i, director in enumerate(directors):
            key = director.getKey()
            if key:

                company = apiCall("company", "", "profile,detailed", key)
                if "apiError" in company:
                    print(i + 1, directors.count(), company)
                    continue

                print(i + 1, directors.count(), key, "ok")

                if company["company"]["company_type"] not in companies:
                    companies[company["company"]["company_type"]] = []

                companies[company["company"]["company_type"]].append(
                    {
                        "company_type": company["company"]["company_type"],
                        "rating": company["company"]["rating"],
                        "upgrades": company["company_detailed"]["upgrades"],
                        "company_funds": company["company_detailed"]["company_funds"],
                        "value": company["company_detailed"]["value"],
                    }
                )

            json.dump(companies, open("yata_companies_details.json", "w"), indent=4)
