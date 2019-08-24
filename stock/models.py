from django.db import models
from django.utils import timezone

import json
import math
from scipy import stats

from yata.handy import timestampToDate


class Stock(models.Model):
    tId = models.IntegerField(default=0, unique=True)
    tName = models.CharField(default="tName", max_length=200)
    tAcronym = models.CharField(default="tAcronym", max_length=10)
    tDirector = models.CharField(default="tDirector", max_length=200)
    tCurrentPrice = models.FloatField(default=0.0)
    tMarketCap = models.BigIntegerField(default=0)
    tTotalShares = models.BigIntegerField(default=0)
    tAvailableShares = models.BigIntegerField(default=0)
    tForecast = models.CharField(default="Average", max_length=200)
    tDemand = models.CharField(default="Average", max_length=200)
    tRequirement = models.BigIntegerField(default=0)
    tDescription = models.CharField(default="tDescription", blank=True, max_length=200)
    priceHistory = models.TextField(default="{}")  # dictionary {timestamp: price}
    quantityHistory = models.TextField(default="{}")  # dictionary {timestamp: quantity}
    dayTendency = models.FloatField(default=0.0)
    dayTendencyA = models.FloatField(default=0.0)
    dayTendencyB = models.FloatField(default=0.0)
    weekTendency = models.FloatField(default=0.0)
    weekTendencyA = models.FloatField(default=0.0)
    weekTendencyB = models.FloatField(default=0.0)
    timestamp = models.IntegerField(default=0)

    def __str__(self):
        return "{} ({}) [{}]".format(self.tName, self.tAcronym, self.tId)

    @classmethod
    def create(cls, k, v, ts):
        print("[model.stock.create] create: ", k, v['acronym'])
        stock = cls(tId=int(k),
                    tName=v['name'],
                    tAcronym=v['acronym'],
                    tDirector=v['director'],
                    tCurrentPrice=float(v['current_price']),
                    tMarketCap=int(v['market_cap']),
                    tTotalShares=int(v['total_shares']),
                    tAvailableShares=int(v['available_shares']),
                    tForecast=v['forecast'],
                    tDemand=v['demand'],
                    tRequirement=int(v.get('benefit', dict({'requirement': 0}))['requirement']),
                    tDescription=v.get('benefit', dict({'description': ""}))['description'],
                    timestamp=int(ts))
        return stock

    def update(self, k, v, ts):
        print("[model.stock.update] update: ", k, v['acronym'])
        self.tName = v['name']
        self.tAcronym = v['acronym']
        self.tDirector = v['director']
        self.tCurrentPrice = float(v['current_price'])
        self.tMarketCap = int(v['market_cap'])
        self.tTotalShares = int(v['total_shares'])
        self.tAvailableShares = int(v['available_shares'])
        self.tForecast = v['forecast']
        self.tDemand = v['demand']
        self.tRequirement = int(v.get('benefit', dict({'requirement': 0}))['requirement'])
        self.tDescription = v.get('benefit', dict({'description': ""}))['description']
        self.timestamp = int(ts) - int(ts) % 3600  # get the hour rounding

        # update price history/quantity
        priceHistory = json.loads(self.priceHistory)
        quantityHistory = json.loads(self.quantityHistory)
        ts = int(ts) - int(ts) % 3600  # get the hour rounding
        to_del = []
        for t, p in priceHistory.items():
            if ts - int(t) > 3600 * 24 * 7:  # remove older than 1 week data
                to_del.append(t)

        for t in to_del:
            print(f"[model.stock.update] remove history entry {t}: {priceHistory[t]}")
            del priceHistory[t]
            try:
                del quantityHistory[t]
            except BaseException:
                pass

        priceHistory[str(ts)] = float(v['current_price'])
        self.priceHistory = json.dumps(priceHistory)
        quantityHistory[str(ts)] = int(v['available_shares'])
        self.quantityHistory = json.dumps(quantityHistory)

        # update tendency
        ts = 0
        for t, p in priceHistory.items():
            ts = max(ts, int(t))

        # 24h Tendency
        try:
            x = []
            y = []
            for t, p in priceHistory.items():
                if ts - int(t) < 3600 * 24 + 30 and int(p):
                    x.append(int(t))
                    y.append(float(p))
            # print(len(x), x)
            if(len(x) > 1):
                a, b, _, _, _ = stats.linregress(x, y)
                if math.isnan(a) or math.isnan(b):
                    self.dayTendencyA = 0.0
                    self.dayTendencyB = 0.0
                    self.dayTendency = 0.0
                else:
                    self.dayTendencyA = a  # a is in $/s
                    self.dayTendencyB = b
                    # time = abs(x[0] - x[-1])
                    # mean = abs(0.5 * a * (x[0] + x[-1]) + b)
                    # self.dayTendency = a * time / float(mean)
                    self.dayTendency = a * 3600 * 24 / float(y[-1])
            else:
                self.dayTendencyA = 0.0
                self.dayTendencyB = 0.0
                self.dayTendency = 0.0
        except BaseException as e:
            self.dayTendencyA = 0.0
            self.dayTendencyB = 0.0
            self.dayTendency = 0.0
        print("[model.stock.update] day tendancy:", self.dayTendencyA, self.dayTendencyB, self.dayTendency)

        # 24h Tendency
        try:
            x = []
            y = []
            for t, p in priceHistory.items():
                if ts - int(t) < 3600 * 24 * 7 + 30 and int(p):
                    x.append(int(t))
                    y.append(float(p))
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
                    self.weekTendency = a * 3600 * 24 / float(y[-1])
            else:
                self.weekTendencyA = 0.0
                self.weekTendencyB = 0.0
                self.weekTendency = 0.0
        except BaseException as e:
            self.weekTendencyA = 0.0
            self.weekTendencyB = 0.0
            self.weekTendency = 0.0
        print("[model.stock.update] week tendancy:", self.weekTendencyA, self.weekTendencyB, self.weekTendency)

        self.save()

        if not len(self.history_set.filter(timestamp=self.timestamp)):
            self.history_set.create(tCurrentPrice=self.tCurrentPrice,
                                    tMarketCap=self.tMarketCap,
                                    tTotalShares=self.tTotalShares,
                                    tAvailableShares=self.tAvailableShares,
                                    tForecast=self.tForecast,
                                    tDemand=self.tDemand,
                                    timestamp=self.timestamp)


class History(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    tCurrentPrice = models.FloatField(default=0.0)
    tMarketCap = models.BigIntegerField(default=0)
    tTotalShares = models.BigIntegerField(default=0)
    tAvailableShares = models.BigIntegerField(default=0)
    tForecast = models.CharField(default="Average", max_length=20)
    tDemand = models.CharField(default="Average", max_length=20)
    timestamp = models.IntegerField(default=0)

    def __str__(self):
        return "{} at {}".format(self.stock.tAcronym, timestampToDate(self.timestamp))
