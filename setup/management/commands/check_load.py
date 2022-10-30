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
from django.conf import settings
from django.core.cache import cache

import os
import requests
import time
import json
from decouple import config

from setup.models import Disabled
from yata.handy import logdate
from yata.handy import cf_fw_rules

class Command(BaseCommand):
    def handle(self, **options):
        print(f"[CRON {logdate()}] START check load")

        disabled = Disabled.objects.first()
        if disabled == None:
            disabled = Disabled.objects.create()

        load = disabled.get_load()
        print(f'[CRON {logdate()}] {" ".join([f"{k}:{v}" for k, v in load.items()])}')

        rules = disabled.get_rules()
        if not disabled.status: # check disabeling rules
            for k, v in rules["disable"].items():
                if v:
                    print(f"[CRON {logdate()}] Disable rule: {k} > {v}")
                    if load[k] > v:
                        print(f"[CRON {logdate()}] DISABLING ({load[k]} > {v})")
                        disabled.status = True
                        disabled.save()
                        cf_fw_rules(paused=False)
                        break

        else: # check enabling rules
            for k, v in rules["enable"].items():
                if v:
                    print(f"[CRON {logdate()}] Enable rule: {k} < {v}")
                    if load[k] < v:
                        print(f"[CRON {logdate()}] ENABLING ({load[k]} < {v})")
                        disabled.status = False
                        disabled.save()
                        cf_fw_rules(paused=True)
                        break

        # send log to diderot proxy relay
        data = {
            "type": "server-stats",
            "load": load,
            "status": disabled.status,
            "rules": rules,
            "timestamp": time.time(),
            "secret-key": settings.SECRET_KEY
        }
        s = requests.Session()
        e = s.post(
            'https://torn.yata.yt/apiflkmizbkdzmwp',
            json=data,
            headers={
                'Diderot-Relay-Port': "8742"
            }
        )

        print(f"[CRON {logdate()}] END")
