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

from bot.models import Bot
from yata.handy import apiCall
from yata.handy import logdate
from yata.handy import timestampToDate
from yata.settings import LOG_KEY

import json

class Command(BaseCommand):
    # def add_arguments(self, parser):
    #     parser.add_argument('-r', '--rebuild-past', action='store_true')

    def handle(self, **options):
        print(f'[CRON {logdate()}] start legacy')

        response = apiCall(
            "user",
            "",
            "log",
            LOG_KEY,
            kv={"cat": "85"},
        )
        if 'error' in response:
            print(f'[CRON {logdate()}] API error {response}')



        for b in Bot.objects.all():
            for s in b.server_set.all():
                print(f'[CRON {logdate()}] Server: {s.name} ({s.bot})')
                print(f'[CRON {logdate()}]         Start: {timestampToDate(s.start)}')
                admins = {str(a.tId): a.name for a in s.server_admin.all()}

                for k, v in admins.items():
                    print(f'[CRON {logdate()}]         Admin: {v} [{k}]')
                if s.start:
                    # check server subscription
                    donations = json.loads(s.donations)
                    for log_id, log in response['log'].items():

                        # skip if item sent by me
                        if "sender" not in log["data"]:
                            continue

                        item = log["data"]["item"]
                        timestamp = log["timestamp"]
                        sender = str(log["data"]["sender"])
                        quantity = int(log["data"]["quantity"])

                        if sender in admins:
                            if log_id in donations:
                                print(f'[CRON {logdate()}]         Log: {log_id} already in donation')
                                break

                            if item in [329, 330, 331, 106]:
                                print(f'[CRON {logdate()}]         Log: {log_id} new donation')
                                donations[log_id] = {
                                    "quantity": int(quantity),
                                    "timestamp": timestamp,
                                    "item": item,
                                    "sender": sender,
                                }

                    s.donations = json.dumps(donations)

                    # compute end ts
                    s.n_donations = 0
                    for k, v in donations.items():
                        s.n_donations += v["quantity"]

                    print(f'[CRON {logdate()}]         Donations: {s.n_donations}')

                    s.end = s.start + 2678400 * s.n_donations
                    s.save()

                    print(f'[CRON {logdate()}]         End  : {timestampToDate(s.end)}')


                else:
                    print(f'[CRON {logdate()}]         UNLIMITED')

        # for company in Company.objects.all():
        #     company.update_info(rebuildPast=rebuild_past)
        # print(f'[CRON {logdate()}] clean old data')
        # one_year_ago = int(time.time() - 3600 * 24 * 365)
        # n, _ = CompanyData.objects.filter(id_ts__lt=one_year_ago).delete()
        # print(f'[CRON {logdate()}] {n} company data rows deleted')
        # n, _ = CompanyStock.objects.filter(id_ts__lt=one_year_ago).delete()
        # print(f'[CRON {logdate()}] {n} company stock rows deleted')
        # print(f'[CRON {logdate()}] end')
