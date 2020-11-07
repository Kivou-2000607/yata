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

import json
import glob
import datetime

from setup.models import Analytics

class Command(BaseCommand):
    def handle(self, **options):

        # list all json reports
        for report_file in glob.glob('analytics/reports/*.json'):
            # get name and type
            report_section, report_period = [r.replace('-', ' ') for r in report_file.replace('.json', '').split('/')[-1].split('_')]
            print(report_section, "/", report_period)

            # open report
            report = json.load(open(report_file, 'r'))

            # get date
            date_string = report["general"]["date_time"]
            date = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S %z")
            report_timestamp = int(datetime.datetime.timestamp(date))

            # get data for db
            defaults = {}

            # general information
            for k in ['total_requests', 'valid_requests', 'failed_requests', 'unique_visitors', 'bandwidth']:
                defaults[k] = report["general"][k]

            # visitors
            defaults["visitors_metadata"] = report["visitors"]["metadata"]
            defaults["visitors_data"] = report["visitors"]["data"]

            # requests
            defaults["requests_metadata"] = report["requests"]["metadata"]
            defaults["requests_data"] = report["requests"]["data"]

            Analytics.objects.update_or_create(report_section=report_section, report_period=report_period, report_timestamp=report_timestamp, defaults=defaults)

            # for k, v in report_for_db.items():
            #     print(k, v)

        # # get date
        # for k, v in data["general"].items():
        #     print(k, v)
