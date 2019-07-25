from django.db import models
from django.utils import timezone

import json
import math
from scipy import stats


class Stock(models.Model):
    tId = models.IntegerField(default=0, unique=True)
    tName = models.CharField(default="tName", max_length=200)
    tAcronym = models.CharField(default="tAcronym", max_length=10)
    tDirector = models.CharField(default="tDirector", max_length=20)
    tCurrentPrice = models.FloatField(default=0.0)
    tMarketCap = models.IntegerField(default=0)
    tTotalShares = models.IntegerField(default=0)
    tAvailableShares = models.IntegerField(default=0)
    tForecast = models.CharField(default="tForecast", max_length=20)
    tDemand = models.CharField(default="tDemand", max_length=20)
    tRequirement = models.IntegerField(default=0)
    tDescription = models.CharField(default="tDescription", blank=True, max_length=20)
    priceHistory = models.TextField(default="{}")  # dictionary {timestamp: price}
    dayTendency = models.FloatField(default=0.0)
    dayTendencyA = models.FloatField(default=0.0)
    dayTendencyB = models.FloatField(default=0.0)
    timestamp = models.IntegerField(default=0)

    def __str__(self):
        return "[{}] {}".format(self.tId, self.tName)

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
        self.timestamp = int(ts)

        # update price history
        priceHistory = json.loads(self.priceHistory)
        ts = int(ts) - int(ts) % 3600  # get the hour rounding
        to_del = []
        for t, p in priceHistory.items():
            if ts - int(t) > (3600 * 24 * 7):
                to_del.append(t)

        for t in to_del:
            print(f"[model.bazaar.item] remove history entry {t}: {priceHistory[t]}")
            del priceHistory[t]

        priceHistory[str(ts)] = float(v['current_price'])
        self.priceHistory = json.dumps(priceHistory)

        # update tendency
        ts = 0
        for t, p in priceHistory.items():
            ts = max(ts, int(t))

        # 24h Tendency
        try:
            x = []
            y = []
            for t, p in priceHistory.items():
                if ts - int(t) < 3600 + 30 and int(p):
                    x.append(int(t))
                    y.append(int(p))
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
                    time = abs(x[0] - x[-1])
                    mean = abs(0.5 * a * (x[0] + x[-1]) + b)
                    self.dayTendency = a * time / float(mean)
            else:
                self.dayTendencyA = 0.0
                self.dayTendencyB = 0.0
                self.dayTendency = 0.0
        except BaseException as e:
            self.dayTendencyA = 0.0
            self.dayTendencyB = 0.0
            self.dayTendency = 0.0
        print("[model.stock.update] day tendancy:", self.dayTendencyA, self.dayTendencyB, self.dayTendency)

        self.save()
