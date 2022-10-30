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

from django.db import models
from django.utils import timezone

import requests
import json
import urllib
import datetime

from yata.handy import tsnow

class APIKey(models.Model):
    tId = models.IntegerField(default=0)
    tName = models.CharField(max_length=16, blank=True)
    key = models.CharField(max_length=32, blank=True)
    lastCheckTS = models.IntegerField(default=0)
    status = models.BooleanField(default=True)
    error = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return "API key of {} [{}]".format(self.tName, self.tId)

    def checkKey(self):
        from yata.handy import apiCall

        req = apiCall("user", "", "", self.key, verbose=False)
        if 'apiError' in req:
            self.status = False
            self.error = req['apiError']
            print("[setup.models.checkKey] {} {}".format(self, self.error))
        else:
            self.status = True
            self.tName = req.get("name", "?")
            self.tId = req.get("player_id", "0")
            self.error = ""
            print("[setup.models.checkKey] {} checked".format(self))

        self.lastCheckTS = int(timezone.now().timestamp())
        self.save()


class Analytics(models.Model):
    report_section = models.CharField(max_length=32)
    report_period = models.CharField(max_length=32)
    report_timestamp = models.BigIntegerField(default=0)

    total_requests = models.BigIntegerField(default=0)
    valid_requests = models.BigIntegerField(default=0)
    failed_requests = models.BigIntegerField(default=0)
    unique_visitors = models.BigIntegerField(default=0)
    bandwidth = models.BigIntegerField(default=0)

    visitors_metadata = models.TextField(default="{}")
    visitors_data = models.TextField(default="[]")

    requests_metadata = models.TextField(default="{}")
    requests_data = models.TextField(default="[]")

    last_update = models.IntegerField(default=0)


class PayPal(models.Model):
    endpoint = models.CharField(max_length=64)
    user = models.CharField(max_length=64)
    pwd = models.CharField(max_length=64)
    signature = models.CharField(max_length=64)

    def __str__(self):
        return f'{self.endpoint} {self.user}'

    def get_balance(self):
        endpoint = "https://api-3t.paypal.com/nvp/"

        payload = {
            "USER": self.user,
            "PWD": self.pwd,
            "SIGNATURE": self.signature,
            "VERSION": "200",
            "METHOD": "GetBalance",
            "RETURNALLCURRENCIES": "0"
        }

        client = requests.session()
        client.headers.update({"X-PAYPAL-RESPONSE-DATA-FORMAT": "JSON-RPC"})
        response = client.post(self.endpoint, data=payload)
        d = urllib.parse.parse_qs(response.content.decode())

        timestamp = d.get("TIMESTAMP", [0])[0].replace("Z", "").replace("T", " ")
        timestamp = datetime.datetime.fromisoformat(timestamp)
        timestamp = int(datetime.datetime.timestamp(timestamp))

        currency = d.get("L_CURRENCYCODE0", [0])[0]
        balance = d.get("L_AMT0", [0])[0]

        return {"balance": balance, "currency": currency, "timestamp": timestamp}


class Droplet(models.Model):
    endpoint = models.CharField(max_length=64)
    token = models.CharField(max_length=64)

    def __str__(self):
        return f'{self.endpoint}'

    def update_specs(self):
        client = requests.session()
        client.headers.update({"Authorization": f"Bearer {self.token}", 'Content-Type': 'application/json'})
        response = client.get(f'{self.endpoint}/v2/droplets')
        payload = json.loads(response.content.decode('utf-8'))["droplets"]
        timestamp = int(tsnow() / 86400) * 86400

        total_price = 0
        for droplet in payload:
            droplet_id = droplet["id"]
            defaults = {
                "name": droplet["name"],
                "vpc_uuid": droplet["vpc_uuid"],
                "vcpus": droplet["vcpus"],
                "memory": droplet["memory"],
                "disk": droplet["disk"],
                "transfer": droplet["size"]["transfer"],
                "size": json.dumps(droplet["size"]),
                "image": json.dumps(droplet["image"])
            }
            self.dropletspec_set.update_or_create(dropletid=droplet_id, timestamp=timestamp, defaults=defaults)
            total_price += droplet["size"]["price_monthly"]

        return total_price

    def get_balance(self):
        client = requests.session()
        client.headers.update({"Authorization": f"Bearer {self.token}", 'Content-Type': 'application/json'})
        response = client.get(f'{self.endpoint}/v2/customers/my/balance')
        d = json.loads(response.content.decode('utf-8'))
        timestamp = d.get("generated_at", "").replace("Z", "").replace("T", " ")
        timestamp = datetime.datetime.fromisoformat(timestamp)
        timestamp = int(datetime.datetime.timestamp(timestamp))
        d["currency"] = "EUR"
        d["timestamp"] = timestamp

        return d

class DropletSpec(models.Model):
    droplet = models.ForeignKey(Droplet, on_delete=models.CASCADE)

    timestamp = models.IntegerField(default=0)

    dropletid = models.IntegerField(default=0)
    name = models.CharField(default="name", max_length=64)
    vpc_uuid = models.CharField(default="vpc_uuid", max_length=64)
    vcpus = models.CharField(default="vcpus", max_length=64)
    memory = models.CharField(default="memory", max_length=64)
    disk = models.CharField(default="disk", max_length=64)
    transfer = models.CharField(default="transfer", max_length=64)

    image = models.TextField(default="{}")
    size = models.TextField(default="{}")

    def __str__(self):
        return f'Droplet {self.dropletid} specs'

    def get_size(self):
        return json.loads(self.size)

    def get_image(self):
        return json.loads(self.image)

class Balance(models.Model):
    timestamp = models.IntegerField(default=0)
    paypal_balance = models.CharField(default="0", max_length=16)
    paypal_currency = models.CharField(default="0", max_length=16)
    droplet_account_balance = models.CharField(default="0", max_length=16)
    droplet_month_to_date_usage = models.CharField(default="0", max_length=16)
    droplet_month_to_date_balance = models.CharField(default="0", max_length=16)
    droplet_month_cost = models.CharField(default="0", max_length=16)


class ApiCallLog(models.Model):
    timestamp = models.IntegerField(default=0)
    url = models.CharField(default="", max_length=256, blank=True)
    error = models.IntegerField(default=-1)


class Disabled(models.Model):
    disable_load1_threshold = models.IntegerField(default=0)
    disable_load5_threshold = models.IntegerField(default=0)
    disable_load15_threshold = models.IntegerField(default=0)
    enable_load1_threshold = models.IntegerField(default=0)
    enable_load5_threshold = models.IntegerField(default=0)
    enable_load15_threshold = models.IntegerField(default=0)

    targets = models.BooleanField(default=False)

    def __str__(self):
        attrs = [f'enable_load{m}_threshold' for m in [1, 5, 15]] + \
                [f'disable_load{m}_threshold' for m in [1, 5, 15]]
        return f'Auto disable [{self.id}]: ' + \
                '/'.join([f'{getattr(self, attr)}' for attr in attrs])

    def get_rules(self):
        rules = {
            "enable": {
                "load1": 0,
                "load5": 0,
                "load15": 0
            },
            "disable": {
                "load1": 0,
                "load5": 0,
                "load15": 0
            }
        }
        for k1, v1 in rules.items():
            for k2 in v1.keys():
                rules[k1][k2] =  getattr(self, f'{k1}_{k2}_threshold')
        return rules

    def get_load(self):
        import os
        load1, load5, load15 = os.getloadavg()
        return {
            'load1': load1,
            'load5': load5,
            'load15': load15
        }
