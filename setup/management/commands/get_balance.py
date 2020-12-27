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

import json
import glob
import datetime
import re

from setup.models import PayPal
from setup.models import Droplet
from setup.models import Balance
from yata.handy import tsnow

class Command(BaseCommand):
    def handle(self, **options):

        paypal = PayPal.objects.last().get_balance()
        droplet = Droplet.objects.first()
        droplet.update_specs()
        droplet = droplet.get_balance()
        # timestamp = int(tsnow() / 86400) * 86400
        timestamp = int(tsnow() / 3600) * 3600
        d = {
            "paypal_balance": paypal["balance"],
            "paypal_currency": paypal["currency"],
            "droplet_account_balance": droplet["account_balance"],
            "droplet_month_to_date_usage": droplet["month_to_date_usage"],
            "droplet_month_to_date_balance": droplet["month_to_date_balance"],
        }

        Balance.objects.get_or_create(timestamp=timestamp, defaults=d)
