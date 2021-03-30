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
import os

from bazaar.models import AbroadStocks
from bazaar.models import BazaarData
from bazaar.models import VerifiedClient
from yata.handy import logdate

class Command(BaseCommand):
    def handle(self, **options):
        print(f"[CRON {logdate()}] START fstocks_client")

        bd = BazaarData.objects.first()

        stocks = AbroadStocks.objects.all()
        clients = {}
        for stock in stocks:
            client_name = stock.client.split("[")[0].strip()
            if client_name not in clients:
                client = VerifiedClient.objects.filter(name=client_name).first()
                if client is not None:
                    clients[client_name] = [0.0, client.author_id, client.author_name]
                else:
                    clients[client_name] = [0.0, 0, "Player"]
            clients[client_name][0] += 1.0 / float(max(1, len(stocks)))



        bd.clientsStats = json.dumps(clients)
        bd.save()

        print(f"[CRON {logdate()}] END")
