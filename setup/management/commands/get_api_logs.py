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
import json

from setup.models import ApiCallLog

class Command(BaseCommand):
    def handle(self, *args, **options):
        print("get logs")
        logs = ApiCallLog.objects.all()
        print("format logs")
        logs_dict = [[log.timestamp, log.url.split("=")[-1], log.error] for log in logs]
        print("write logs")
        json.dump(logs_dict, open("./zzz/yata_api_call_logs.json", "w"))
