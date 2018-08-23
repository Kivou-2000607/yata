from django.db import models
from django.utils import timezone

import requests


class Config(models.Model):
    autorisedId = models.CharField(default="", max_length=200)
    apiKey = models.CharField(default="", max_length=16)
    nItems = models.IntegerField(default=10)
    lastScan = models.DateTimeField(default=timezone.now)

    def list_autorised_id(self):
        # split string by ","
        try:
            list = [int(id.strip()) for id in self.autorisedId.split(',')]
        except:
            print("[MODEL CONFIG]: WARNING autorised id couldn't be parsed", self.autorisedId)
            list = [-1]
        return list

    def update_last_scan(self):
        self.lastScan = timezone.now()
        self.save()
        return self.lastScan


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
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "[{}] {}".format(self.tId, self.tName)

    @classmethod
    def create(cls, k, v):
        print("[MODEL Item] create", k, v['name'], v['type'], v['market_value'])
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

    def update(self, k, v):
        # v = {'name': 'Kitchen Knife',
        #      'description': 'Do your attempts to prepare food like your favourite TV chef end up more like hack and saw than slice and dice? If so, a sharp new knife could be your saviour.',
        #      'type': 'Melee',
        #      'buy_price': 1500,
        #      'sell_price': 1000,
        #      'market_value': 2094,
        #      'circulation': 68911,
        #      'image': 'http://www.torn.com/images/items/6/large.png'}
        print("[MODEL Item] update", k, v['name'], v['type'], v['market_value'])
        self.tId = int(k)
        self.tName = v['name']
        self.tType = v['type'].replace(" ", "")
        self.tMarketValue = int(v['market_value'])
        self.tSellPrice = int(v['sell_price'])
        self.tBuyPrice = int(v['buy_price'])
        self.tCirculation = int(v['circulation'])
        self.tDescription = v['description']
        self.tImage = v['image']
        self.date = timezone.now()
        self.save()

    def display_image(self):
        from urllib.parse import urlparse
        from django.utils.html import format_html
        from django.contrib.staticfiles.templatetags.staticfiles import static
        return format_html("<img src=\"{}\" alt=\"{} [{}]\" />".format(static(urlparse(self.tImage)[2][1:]), self.tId, self.tName))

    def display_thumb(self):
        from urllib.parse import urlparse
        from django.utils.html import format_html
        from django.contrib.staticfiles.templatetags.staticfiles import static
        return format_html("<img src=\"{}\" alt=\"{} [{}]\" class=\"thumb\" />".format(static(urlparse(self.tImage)[2][1:]), self.tId, self.tName))

    def last_update(self):
        list = [s for s in str(timezone.now() - self.date).split(".")[0].split(':')]
        return "{}h {:02.0f}m".format(list[0], float(list[1]))

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
        req = requests.get("https://api.torn.com/market/{}?selections=bazaar&key={}".format(self.tId, key)).json()
        try:
            baz = req['bazaar']
            # delete and fill date
            self.marketdata_set.all().delete()
            if baz is not None:
                for i, r in enumerate(baz):
                    print("[MODEL Item] update_bazaar: {} (q:{}, c:{})".format(r, baz[r]["quantity"], baz[r]["cost"]))
                    self.marketdata_set.create(userId=r, quantity=baz[r]["quantity"], cost=baz[r]["cost"])
                    if i >= n - 1:
                        break
            self.date = timezone.now()
            self.save()
        except:
            pass

        return req


class MarketData(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    userId = models.BigIntegerField(default=0)
    quantity = models.BigIntegerField(default=1)
    cost = models.BigIntegerField(default=0)

    def __str__(self):
        return "{} ({}): {} x {}".format(self.item, self.userId, self.quantity, self.cost)


class Player(models.Model):
    name = models.CharField(default="Duke", max_length=100)
    playerId = models.BigIntegerField(default=4)
    date = models.DateTimeField(default=timezone.now)
    nLog = models.IntegerField(default=1)
    itemsId = models.TextField(default="", blank=True)

    def __str__(self):
        return "{} [{}]".format(self.name, self.playerId)

    def torn_url_page(self):
        return "https://www.torn.com/profiles.php?XID={}".format(self.playerId)

    def get_items_id(self):
        if self.itemsId:
            return self.itemsId.strip().replace(" ", "").split(',')
        else:
            return []

    def toggle_item(self, id):
        list_id = self.get_items_id()
        if id in list_id:
            del list_id[list_id.index(id)]
            self.itemsId = ",".join(list_id)
            self.save()
            return False
        else:
            list_id.append(id)
            self.itemsId = ",".join(list_id)
            self.save()
            return True


class Login(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
