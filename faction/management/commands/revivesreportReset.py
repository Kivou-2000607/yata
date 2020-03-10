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

import time

from faction.models import RevivesReport
from faction.models import REPORT_REVIVES_STATUS


class Command(BaseCommand):
    def handle(self, *args, **options):
        for report in RevivesReport.objects.all():
            report.revive_set.all().delete()
            report.revivesfaction_set.all().delete()
            report.revivesplayer_set.all().delete()
            report.last = 0
            report.update = 0
            report.computing = True
            report.state = 0
            report.assignCrontab()
            print(report)
