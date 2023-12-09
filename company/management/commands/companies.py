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

import time

from django.core.management.base import BaseCommand

from company.models import Company, CompanyData, CompanyStock
from yata.handy import logdate

# import json


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-r", "--rebuild-past", action="store_true")

    def handle(self, **options):
        rebuild_past = options.get("rebuild_past", False)
        print(f"[CRON {logdate()}] start companies: rebuild past = {rebuild_past}")
        for company in Company.objects.all():

            if rebuild_past:
                # compute company_data.daily_stockcost
                for company_data in company.companydata_set.all():
                    id_ts = company_data.id_ts
                    stock = company.companystock_set.filter(id_ts=id_ts)
                    company_data.daily_stockcost = 0
                    for s in stock:
                        company_data.daily_stockcost += s.sold_amount * s.cost

                    # create weekly_profit
                    id_ts_lastw = id_ts - (7 * 24 * 3600)
                    # contains 7 days before for the last week daily comparison and 1 to 6 days before for the weekly
                    # company_datas.count() should be 8 if all data are found
                    company_datas = company.companydata_set.filter(id_ts__gte=id_ts_lastw).order_by("id_ts")

                    # get last week data
                    cd = company_datas.filter(id_ts=id_ts_lastw).first()
                    if cd is None:
                        # didn't find last week entry
                        company_data.lastw_profit = 0
                        company_data.lastw_customers = 0
                        company_data.lastw_income = 0
                    else:
                        # found last week entry
                        company_data.lastw_profit = cd.daily_profit
                        company_data.lastw_customers = cd.daily_customers
                        company_data.lastw_income = cd.daily_income
                        # remove from query_set
                        company_datas = company_datas.exclude(id_ts=id_ts - (7 * 24 * 3600))

                    money_spent = 0
                    n_data = company_datas.count()  # should be 7 if all data are found (8-1 for removing last week)
                    for i, cd in enumerate(company_datas):
                        money_spent += (cd.advertising_budget + cd.total_wage + cd.daily_stockcost) * 7 / float(n_data)  # in case less than 7 data (missing data)

                    company_data.daily_profit = company_data.daily_income - company_data.advertising_budget - company_data.total_wage - company_data.daily_stockcost
                    company_data.weekly_profit = company_data.weekly_income - money_spent

                    # create effectiveness
                    #                     defaults = {}
                    #                     for emp_id, values in json.loads(company_data.employees).items():
                    #                         for k, v in values.items():
                    #                             if k[:13] == "effectiveness":
                    #                                 defaults[k] = defaults[k] + v if k in defaults else v
                    #
                    #                     # set company updates
                    #                     for attr, value in defaults.items():
                    #                         setattr(company_data, attr, value)
                    company_data.save()

            company.update_info(rebuildPast=rebuild_past)
        print(f"[CRON {logdate()}] clean old data")
        one_year_ago = int(time.time() - 3600 * 24 * 365)
        n, _ = CompanyData.objects.filter(id_ts__lt=one_year_ago).delete()
        print(f"[CRON {logdate()}] {n} company data rows deleted")
        n, _ = CompanyStock.objects.filter(id_ts__lt=one_year_ago).delete()
        print(f"[CRON {logdate()}] {n} company stock rows deleted")
        print(f"[CRON {logdate()}] end")
