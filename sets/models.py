from django.db import models
from django.utils import timezone

import requests

# ApiKey


class config(models.Model):
    key = models.SlugField(max_length=16)
    stockKeys = models.CharField(default="", max_length=200)
    nItems = models.IntegerField(default=10)

    def listOfStockKeys(self):
        # string look like "user1:key1,user2:key2"
        # split string by ","
        try:
            kvs = self.stockKeys.strip().split(',')
            list = [kv.split(':') for kv in kvs]
        except:
            print("[MODEL CONFIG]: WARNING Stock keys couldn't be parsed", self.stockKeys)
            list = {'Stock': 0}
        return list

# Create your models here.


class Item(models.Model):
    # torn ID of the item
    # object description from: https://api.torn.com/torn/{id}?selections=items&key=
    tId = models.IntegerField(unique=True)
    tName = models.CharField(max_length=200)
    tType = models.CharField(max_length=200)
    tDescription = models.TextField(default="")
    tMarketValue = models.BigIntegerField(default=0)
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
                   tDescription=v['description'],
                   tImage=v['image'])
        return item

    def update(self, k, v, uq=None):
        # k (key): item id
        # v (values): item values from API
        # list of us : userStock [ [user1,stock1], [user2,stock2] ]
        print("[MODEL Item] update", k, v['name'], v['type'], v['market_value'])
        self.tId = int(k)
        self.tName = v['name']
        self.tType = v['type'].replace(" ", "")
        self.tMarketValue = int(v['market_value'])
        self.tDescription = v['description']
        self.tImage = v['image']
        if uq is not None:
            # update userStock
            # try to find if user name already exists
            for u, q in uq:
                try:
                    existingUserStock = self.userstock_set.filter(user=u)[0]
                    existingUserStock.quantity = q
                    existingUserStock.save()
                    print("[MODEL Item] update user stock: ", u, q)
                except:
                    us = userStock(id=None, user=u, quantity=q, item=self)
                    us.save()
                    print("[MODEL Item] create user stock: ", u, q)

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
        list = [s for s in str(timezone.now()-self.date).split(".")[0].split(':')]
        return "{}h {:02.0f}m".format(list[0], float(list[1]))

    def getBazaar(self, n=10):
        bData = self.marketdata_set.all().order_by('cost')
        try:
            cData = []
            tmp = 0
            for i in range(len(bData)):
                cData.append({'cost':       bData[i].cost,
                              'quantity':   bData[i].quantity,
                              'cumulative': int(float(bData[i].quantity)*float(bData[i].cost))+tmp}
                             )
                tmp = cData[i]["cumulative"]
        except:
            cData = []
        return cData

    def updateBazaar(self, key="", n=10):
        # API Call
        req = requests.get("https://api.torn.com/market/{}?selections=bazaar&key={}".format(self.tId, key)).json()
        try:
            baz = req['bazaar']
            # delete and fill date
            self.marketdata_set.all().delete()
            if baz is not None:
                for i, r in enumerate(baz):
                    print("[MODEL Item] getBazaar: {} (q:{}, c:{})".format(r, baz[r]["quantity"], baz[r]["cost"]))
                    self.marketdata_set.create(user_id=r, quantity=baz[r]["quantity"], cost=baz[r]["cost"])
                    if i >= n-1:
                        break
            self.date = timezone.now()
            self.save()
        except:
            pass

        return req


class userStock(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    user = models.CharField(default="0", max_length=100)
    quantity = models.IntegerField(default=0)


class MarketData(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    user_id = models.BigIntegerField(default=0)
    quantity = models.BigIntegerField(default=1)
    cost = models.BigIntegerField(default=0)

    def __str__(self):
        return "{} ({}): {} x {}".format(self.item, self.user_id, self.quantity, self.cost)


class login(models.Model):
    user_name = models.CharField(default="Duke", max_length=100)
    user_id = models.BigIntegerField(default=4)
    date = models.DateTimeField(default=timezone.now)
    n_log = models.IntegerField(default=1)

    def __str__(self):
        return "{} [{}]".format(self.user_name, self.user_id)

    def torn_url_page(self):
        return "https://www.torn.com/profiles.php?XID={}".format(self.user_id)

class loginDate(models.Model):
    login = models.ForeignKey(login, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
