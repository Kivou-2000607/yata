from django.db import models
from django.utils import timezone

from yata.handy import apiCall


class Preference(models.Model):
    # autorisedId = models.CharField(default="", max_length=200)
    key = models.CharField(default="", max_length=16)
    nItems = models.IntegerField(default=10)
    lastScanTS = models.IntegerField(default=0)
    apiString = models.CharField(default="0", max_length=330)  # for 10 pairs login(15):key(16)

    def get_random_key(self):
        from numpy.random import randint
        pairs = self.apiString.split(",")
        i = randint(0, len(pairs))
        return pairs[i].split(":")


class Item(models.Model):
    # torn ID of the item
    # object description from: https://api.torn.com/torn/{id}?selections=items&key=
    tId = models.IntegerField(unique=True)
    tName = models.CharField(max_length=200)
    tType = models.CharField(max_length=200)
    tDescription = models.TextField(default="")
    tMarketValue = models.BigIntegerField(default=0)
    tSellPrice = models.BigIntegerField(default=0)
    tBuyPrice = models.BigIntegerField(default=0)
    tCirculation = models.BigIntegerField(default=0)
    tImage = models.URLField(max_length=500)
    onMarket = models.BooleanField(default=False)
    lastUpdateTS = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)

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
                   tImage=v['image'])
        return item

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
        self.tImage = v['image']
        # self.lastUpdateTS = int(timezone.now().timestamp())
        # self.date = timezone.now() # don't update time since bazaar are not updated
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
                              'cumulative': int(float(bData[i].quantity) * float(bData[i].cost)) + tmp}
                             )
                tmp = cData[i]["cumulative"]
        except:
            cData = []
        return cData

    def update_bazaar(self, key="", n=10):
        # API Call
        baz = apiCall("market", self.tId, "bazaar", key, sub="bazaar")
        baz = dict({}) if baz is None else baz

        if 'apiError' in baz:
            return baz
        else:
            self.marketdata_set.all().delete()
            if baz is not None:
                for i, r in enumerate(baz):
                    print("[model.bazaar.update_bazaar] update_bazaar: {} (q:{}, c:{})".format(r, baz[r]["quantity"], baz[r]["cost"]))
                    self.marketdata_set.create(sellId=r, quantity=baz[r]["quantity"], cost=baz[r]["cost"])
                    if i >= n - 1:
                        break
            self.lastUpdateTS = int(timezone.now().timestamp())
            self.save()
            return baz


class MarketData(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    sellId = models.BigIntegerField(default=0)
    quantity = models.BigIntegerField(default=1)
    cost = models.BigIntegerField(default=0)

    def __str__(self):
        return "{} ({}): {} x {}".format(self.item, self.sellId, self.quantity, self.cost)
