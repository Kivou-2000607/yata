# Copyright 2020 kivou.2000607@gmail.com
#
# This file is part of yata.
#
#     yata is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     any later version.
#
#     yata is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with yata. If not, see <https://www.gnu.org/licenses/>.

import time

import requests
from django.core.management.base import BaseCommand

from company.models import CompanyDescription, CompanyListing
from player.models import Player
from yata.handy import logdate, tsnow


class Command(BaseCommand):
    def handle(self, **options):
        print(f"[CRON {logdate()}] start companies_browse")

        player = Player.objects.filter(key_level__gte=1).first()
        if not player:
            print(f"[CRON {logdate()}] no valid API key found, aborting")
            return

        key = player.getKey()
        run_start = tsnow()
        total_companies = 0
        company_descriptions = list(CompanyDescription.objects.all())
        print(f"[CRON {logdate()}] processing {len(company_descriptions)} company types")

        for idx, cd in enumerate(company_descriptions, 1):
            print(f"[CRON {logdate()}] [{idx}/{len(company_descriptions)}] fetching {cd.name}...")
            offset = 0
            batch_count = 0
            while True:
                url = f"https://api.torn.com/v2/company/{cd.tId}/companies?limit=100&offset={offset}&key={key}&comment=yata"

                try:
                    r = requests.get(url, timeout=10).json()
                except Exception as e:
                    print(f"[CRON {logdate()}] error fetching {cd.name}: {e}")
                    break

                companies = r.get("companies", [])
                if not companies:
                    break

                batch_count += 1
                # Collect companies for bulk upsert
                to_update = []
                for c in companies:
                    obj, _ = CompanyListing.objects.get_or_create(
                        tId=c["id"],
                        defaults={
                            "company_type": cd,
                            "name": c["name"],
                            "rating": c["rating"],
                            "director": c["director"]["id"],
                            "employees_hired": c["employees"]["hired"],
                            "employees_capacity": c["employees"]["capacity"],
                            "daily_income": c["income"]["daily"],
                            "weekly_income": c["income"]["weekly"],
                            "daily_customers": c["customers"]["daily"],
                            "weekly_customers": c["customers"]["weekly"],
                            "days_old": c["days_old"],
                            "appsclosed": not c["applications_allowed"],
                            "updated": run_start,
                        },
                    )
                    if not _:
                        # Update existing
                        obj.company_type = cd
                        obj.name = c["name"]
                        obj.rating = c["rating"]
                        obj.director = c["director"]["id"]
                        obj.employees_hired = c["employees"]["hired"]
                        obj.employees_capacity = c["employees"]["capacity"]
                        obj.daily_income = c["income"]["daily"]
                        obj.weekly_income = c["income"]["weekly"]
                        obj.daily_customers = c["customers"]["daily"]
                        obj.weekly_customers = c["customers"]["weekly"]
                        obj.days_old = c["days_old"]
                        obj.appsclosed = not c["applications_allowed"]
                        obj.updated = run_start
                        to_update.append(obj)
                    total_companies += 1

                if to_update:
                    CompanyListing.objects.bulk_update(
                        to_update,
                        [
                            "company_type",
                            "name",
                            "rating",
                            "director",
                            "employees_hired",
                            "employees_capacity",
                            "daily_income",
                            "weekly_income",
                            "daily_customers",
                            "weekly_customers",
                            "days_old",
                            "appsclosed",
                            "updated",
                        ],
                        batch_size=100,
                    )

                print(f"[CRON {logdate()}]   batch {batch_count}: {len(companies)} companies ({total_companies} total so far)")

                if r.get("_metadata", {}).get("links", {}).get("next") is None:
                    break

                offset += 100
                time.sleep(0.5)

            print(f"[CRON {logdate()}] finished {cd.name}: {batch_count} batches")
            time.sleep(0.5)

        # Remove companies that no longer exist in the API
        deleted_count = CompanyListing.objects.filter(updated__lt=run_start).count()
        CompanyListing.objects.filter(updated__lt=run_start).delete()

        print(f"[CRON {logdate()}] end companies_browse: {total_companies} companies loaded, {deleted_count} deleted")
