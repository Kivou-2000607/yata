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

import json
import math
from scipy import stats

from yata.handy import apiCall


class Item(models.Model):
    # torn ID of the item
    # object description from: https://api.torn.com/torn/{id}?selections=items&key=
    tId = models.IntegerField(unique=True)
    tName = models.CharField(max_length=200)
    tType = models.CharField(max_length=200)
    tDescription = models.TextField(default="")
    tEffect = models.TextField(default="")
    tRequirement = models.TextField(default="")
    tMarketValue = models.BigIntegerField(default=0)
    tSellPrice = models.BigIntegerField(default=0)
    tBuyPrice = models.BigIntegerField(default=0)
    tCirculation = models.BigIntegerField(default=0)
    tImage = models.URLField(max_length=500)
    onMarket = models.BooleanField(default=False)
    lastUpdateTS = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
    stockI = models.IntegerField(default=0)
    stockD = models.IntegerField(default=0)
    stockB = models.IntegerField(default=0)
    priceHistory = models.TextField(default={})  # dictionary {timestamp: marketValue}
    weekTendency = models.FloatField(default=0.0)
    weekTendencyA = models.FloatField(default=0.0)
    weekTendencyB = models.FloatField(default=0.0)
    monthTendency = models.FloatField(default=0.0)
    monthTendencyA = models.FloatField(default=0.0)
    monthTendencyB = models.FloatField(default=0.0)

    def __str__(self):
        return "[{}] {}".format(self.tId, self.tName)

    @classmethod
    def create(cls, k, v):
        print("[model.bazaar.item] create: ", k, v['name'], v['type'], v['market_value'])
        item = cls(tId=int(k),
                   tName=v['name'],
                   tType=v['type'].replace(" ", ""),
                   tMarketValue=int(v['market_value']),
                   tSellPrice=int(v['sell_price']),
                   tBuyPrice=int(v['buy_price']),
                   tCirculation=int(v['circulation']),
                   tDescription=v['description'],
                   tEffect=v['effect'],
                   tRequirement=v['requirement'],
                   tImage=v['image'])
        return item

    def updateTendencies(self):
        priceHistory = json.loads(self.priceHistory)
        ts = 0
        for t, p in priceHistory.items():
            ts = max(ts, int(t))

        # week Tendency
        try:
            x = []
            y = []
            for t, p in priceHistory.items():
                if ts - int(t) < 3600 * 24 * 7 + 30 and int(p):
                    x.append(int(t))
                    y.append(int(p))
            # print(len(x), x)
            if(len(x) > 1):
                a, b, _, _, _ = stats.linregress(x, y)
                if math.isnan(a) or math.isnan(b):
                    self.weekTendencyA = 0.0
                    self.weekTendencyB = 0.0
                    self.weekTendency = 0.0
                else:
                    self.weekTendencyA = a  # a is in $/s
                    self.weekTendencyB = b
                    # time = abs(x[0] - x[-1])
                    # mean = abs(0.5 * a * (x[0] + x[-1]) + b)
                    # self.weekTendency = a * time / float(mean)
                    self.weekTendency = a * 3600 * 24 * 7 / float(y[-1])
            else:
                self.weekTendencyA = 0.0
                self.weekTendencyB = 0.0
                self.weekTendency = 0.0
        except BaseException as e:
            self.weekTendencyA = 0.0
            self.weekTendencyB = 0.0
            self.weekTendency = 0.0
        print("[model.bazaar.item] week tendancy:", self.weekTendencyA, self.weekTendencyB, self.weekTendency)

        # month Tendency
        try:
            x = []
            y = []
            for t, p in priceHistory.items():
                if ts - int(t) < 3600 * 24 * 31 + 30 and int(p):
                    x.append(int(t))
                    y.append(int(p))
            if(len(x) > 1):
                a, b, _, _, _ = stats.linregress(x, y)
                # print(a, b)
                if math.isnan(a) or math.isnan(b):
                    self.monthTendencyA = 0.0
                    self.monthTendencyB = 0.0
                    self.monthTendency = 0.0
                else:
                    self.monthTendencyA = a  # a is in $/s
                    self.monthTendencyB = b
                    # time = abs(x[0] - x[-1])
                    # mean = abs(0.5 * a * (x[0] + x[-1]) + b)
                    # self.monthTendency = a * time / float(mean)
                    self.monthTendency = a * 3600 * 24 * 7 / float(y[-1])
            else:
                self.monthTendencyA = 0.0
                self.monthTendencyB = 0.0
                self.monthTendency = 0.0
        except BaseException as e:
            self.monthTendencyA = 0.0
            self.monthTendencyB = 0.0
            self.monthTendency = 0.0
        print("[model.bazaar.item] month tendancy:", self.monthTendencyA, self.monthTendencyB, self.monthTendency)

        # print(self.monthTendency, self.monthTendencyA, self.monthTendencyB)
        # self.lastUpdateTS =
        # self.date = timezone.now() # don't update time since bazaar are not updated
        self.save()

    def update(self, v):
        # v = {'name': 'Kitchen Knife',
        #      'description': 'Do your attempts to prepare food like your favourite TV chef end up more like hack and saw than slice and dice? If so, a sharp new knife could be your saviour.',
        #      'type': 'Melee',
        #      'buy_price': 1500,
        #      'sell_price': 1000,
        #      'market_value': 2094,
        #      'circulation': 68911,
        #      'image': 'http://www.torn.com/images/items/6/large.png'}
        print("[model.bazaar.item] update:", self.tId, v['name'], v['type'], v['market_value'])
        self.tName = v['name']
        self.tType = v['type'].replace(" ", "")
        self.tMarketValue = int(v['market_value'])
        self.tSellPrice = int(v['sell_price'])
        self.tBuyPrice = int(v['buy_price'])
        self.tCirculation = int(v['circulation'])
        self.tDescription = v['description']
        self.tEffect = v['effect'],
        self.tRequirement = v['requirement'],
        self.tImage = v['image']
        priceHistory = json.loads(self.priceHistory)
        ts = int(v.get('timestamp', timezone.now().timestamp()))
        ts = int(ts) - int(ts) % 3600  # get the hour rounding
        to_del = []
        for t, p in priceHistory.items():
            if ts - int(t) > 3600 * 24 * 31:
                to_del.append(t)

        for t in to_del:
            print("[model.bazaar.item] remove history entry {}: {}".format(t, priceHistory[t]))
            del priceHistory[t]

        priceHistory[ts] = int(v["market_value"])
        self.priceHistory = json.dumps(priceHistory)
        self.updateTendencies()
        self.save()

    def display_small(self):
        from django.utils.html import format_html
        # from urllib.parse import urlparse
        # from django.contrib.staticfiles.templatetags.staticfiles import static
        # return format_html("<img src=\"{}\" alt=\"{} [{}]\" />".format(static(urlparse(self.tImage)[2][1:]), self.tId, self.tName))
        return format_html("<img src='https://www.torn.com/images/items/{id}/small.png' alt='{name} [{id}]' />".format(id=self.tId, name=self.tName))

    def display_large(self):
        from django.utils.html import format_html
        # from urllib.parse import urlparse
        # from django.contrib.staticfiles.templatetags.staticfiles import static
        # return format_html("<img src=\"{}\" alt=\"{} [{}]\" />".format(static(urlparse(self.tImage)[2][1:]), self.tId, self.tName))
        return format_html("<img src='https://www.torn.com/images/items/{id}/large.png' alt='{name} [{id}]' />".format(id=self.tId, name=self.tName))

    # def display_thumb(self):
    #     from django.utils.html import format_html
    #     # from urllib.parse import urlparse
    #     # from django.contrib.staticfiles.templatetags.staticfiles import static
    #     # return format_html("<img src=\"{}\" alt=\"{} [{}]\" class=\"thumb\" />".format(static(urlparse(self.tImage)[2][1:]), self.tId, self.tName))
    #     return format_html("<img src='https://www.torn.com/images/items/{id}/small.png' alt='{name} [{id}]' class='thumb' />".format(id=self.tId, name=self.tName))

    def get_bazaar(self, n=10):
        bData = self.marketdata_set.all().order_by('cost')
        try:
            cData = []
            tmp = 0
            for i in range(len(bData)):
                cData.append({'cost': bData[i].cost,
                              'quantity': bData[i].quantity,
                              'itemmarket': bData[i].itemmarket,
                              'cumulative': int(float(bData[i].quantity) * float(bData[i].cost)) + tmp}
                             )
                tmp = cData[i]["cumulative"]
        except BaseException:
            cData = []
        return cData

    def update_bazaar(self, key="", n=10):
        # API Call
        req = apiCall("market", self.tId, "bazaar,itemmarket,timestamp", key)
        bazaar = req.get("bazaar") if req.get("bazaar") else dict({})
        itemmarket = req.get("itemmarket") if req.get("itemmarket") else dict({})

        if 'apiError' in bazaar:
            return bazaar
        if 'apiError' in itemmarket:
            return itemmarket
        else:
            # fuse both
            marketData = []
            for v in bazaar:
                marketData.append({"cost": v["cost"], "quantity": v["quantity"], "itemmarket": False})

            pp = 0  # previews price
            q = 0  # quantity
            for i, v in enumerate(itemmarket):
                pp = v["cost"] if i == 0 else pp
                if v["cost"] == pp:
                    q += 1
                else:
                    marketData.append({"cost": pp, "quantity": q, "itemmarket": True})
                    q = 1
                    pp = v["cost"]
            if len(itemmarket):
                marketData.append({"cost": pp, "quantity": q, "itemmarket": True})

            marketData = sorted(marketData, key=lambda x: x['cost'], reverse=False)
            self.marketdata_set.all().delete()
            for i, (v) in enumerate(marketData):
                # print("[model.bazaar.update_bazaar] update_bazaar: (q:{}, c:{})".format(v["quantity"], v["cost"]))
                self.marketdata_set.create(quantity=v["quantity"], cost=v["cost"], itemmarket=v["itemmarket"])
                if i >= n - 1:
                    break
            self.lastUpdateTS = int(req.get('timestamp', timezone.now().timestamp()))
            self.save()
            return marketData


class MarketData(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.BigIntegerField(default=1)
    cost = models.BigIntegerField(default=0)
    itemmarket = models.BooleanField(default=False)

    def __str__(self):
        return "{}: {} x {}".format(self.item, self.quantity, self.cost)


class BazaarData(models.Model):
    nItems = models.IntegerField(default=10)
    lastScanTS = models.IntegerField(default=0)
    itemType = models.TextField(default="{}")
