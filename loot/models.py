from django.db import models
from django.utils import timezone
from django.conf import settings

import requests

from yata.handy import apiCall
from setup.functions import randomKey


class NPC(models.Model):
    tId = models.IntegerField(default=0)
    name = models.CharField(max_length=20, default="?")
    status = models.CharField(max_length=20, default="Ok")
    hospitalTS = models.IntegerField(default=0)
    updateTS = models.IntegerField(default=0)
    show = models.BooleanField(default=False)

    def __str__(self):
        return "NPC {} [{}]".format(self.name, self.tId)

    def update(self, key=None):
        if key is None:
            key = randomKey()

        req = requests.get('https://api.torn.com/user/{}?&selections=profile,timestamp&key={}'.format(self.tId, key)).json()
        if 'error' in req:
            return req['error']
        else:
            self.name = req.get("name", "?")
            self.updateTS = int(req.get("timestamp", 0))
            states = req.get("states")
            status = req.get("status")

            if states['hospital_timestamp']:
                self.hospitalTS = states['hospital_timestamp']
                self.status = 'hospitalized'
            else:
                self.status = status["details"]

            print("[loot.NPC.update] {}: {} {} {}".format(self, self.status, self.hospitalTS, self.updateTS))
            self.save()

    def lootTimings(self, lvl=None):
        now = int(timezone.now().timestamp())
        lootTimings = dict({0: {"lvl": 0}})
        # ts = [self.hospitalTS,  # lvl 1
        #       self.hospitalTS + 30 * 60,  # lvl 2
        #       self.hospitalTS + 90 * 60,  # lvl 3
        #       self.hospitalTS + 210 * 60,  # lvl 4
        #       self.hospitalTS + 450 * 60,  # lvl 5
        #       ]

        add = 0
        next = 0
        for i in range(5):
            add = 2 * add + min(i, 1) * 30
            ts = self.hospitalTS + add * 60
            due = ts - now
            if due > 0:
                next += 1

            if next == 0:
                pro = 100
            elif next == 1:
                if add:
                    pro = 100 * (1. - max(due, 0) / float(add * 60))
                else:
                    pro = 100 * (1. - max(due, 0) / float(120 * 60))
            else:
                pro = 0

            lootTimings[i + 1] = {"lvl": i + 1, "ts": ts, "due": due, "pro": int(pro), "next": next}


        current = 5 - lootTimings[5]['next']
        if lvl is None:
            return lootTimings
        elif lvl in ['next']:
            return lootTimings[min(current + 1, 5)]
        elif lvl in ['current']:
            return lootTimings[current]
        else:
            return lootTimings[lvl]

    def nextLevel(self):
        return self.lootTimings(lvl='next')

    def currentLevel(self):
        return self.lootTimings(lvl='current')

    def levelIV(self):
        return self.lootTimings(lvl=4)

    def pictureURL(self):
        return "/static/images/loot/npc_{}.png".format(self.tId)
