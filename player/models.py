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

from yata.handy import apiCall
from awards.functions import updatePlayerAwards
from chain.models import Faction
from awards.models import AwardsData


SECTION_CHOICES = (
    ('B', 'bazaar'),
    ('F', 'faction'),
    ('T', 'target'),
    ('A', 'awards'),
    ('S', 'stock'),
    ('L', 'loot'),
    )


class Player(models.Model):
    # user information: basic
    tId = models.IntegerField(default=4, unique=True)
    name = models.CharField(default="Duke", max_length=200)
    key = models.CharField(default="AAAA", max_length=16)
    dId = models.BigIntegerField(default=0)

    # BooleanField states
    active = models.BooleanField(default=True)
    validKey = models.BooleanField(default=True)

    # user information: faction
    factionId = models.IntegerField(default=0)
    factionAA = models.BooleanField(default=False)
    factionNa = models.CharField(default="My Faction", max_length=32)

    # user last update
    lastUpdateTS = models.IntegerField(default=0)
    lastActionTS = models.IntegerField(default=0)

    # info for chain APP
    chainInfo = models.CharField(default="N/A", max_length=255)
    chainJson = models.TextField(default="{}")
    chainUpda = models.IntegerField(default=0)

    # info for target APP
    targetInfo = models.CharField(default="N/A", max_length=255)
    targetJson = models.TextField(default="{}")
    targetUpda = models.IntegerField(default=0)

    # info for target APP
    bazaarInfo = models.CharField(default="N/A", max_length=255)
    bazaarJson = models.TextField(default="{}")
    bazaarUpda = models.IntegerField(default=0)

    # info for awards APP
    awardsInfo = models.CharField(default="N/A", max_length=255)
    awardsJson = models.TextField(default="{}")
    awardsUpda = models.IntegerField(default=0)
    awardsRank = models.IntegerField(default=99999)
    awardsScor = models.IntegerField(default=0)  # int(10000 x score in %)

    # info for stocks APP
    stocksInfo = models.CharField(default="N/A", max_length=255)
    stocksJson = models.TextField(default="{}")
    stocksUpda = models.IntegerField(default=0)

    def __str__(self):
        return "{:15} [{:07}]".format(self.name, self.tId)

    def update_info(self, i=None, n=None):
        """ update player information

        """

        progress="{:04}/{:04}: ".format(i, n) if i is not None else ""

        # API Calls
        user = apiCall('user', '', 'personalstats,crimes,education,battlestats,workstats,perks,networth,merits,profile,medals,honors,icons,bars,discord', self.key, verbose=False)

        # set active
        self.active = int(timezone.now().timestamp()) - self.lastActionTS < 60 * 60 * 24 * 31

        # change to false if error code 2
        self.validKey = False if user.get('apiErrorCode', 0) == 2 else self.validKey

        # change to true if fetch result
        self.validKey = True if user.get('name', False) else self.validKey

        # discrod id
        dId = user.get('discord', {'discordID': ''})['discordID']
        self.dId = 0 if dId in [''] else dId

        # skip if not yata active and no valid key
        if not self.active and not self.validKey:
            print("[player.models.update_info] {}{} action: {:010} active: {:1} api: {:1} -> delete user".format(progress, self, self.lastActionTS, self.active, self.validKey))
            # self.delete()
            self.save()
            return 0

        # skip if api error (not invalid key)
        elif 'apiError' in user:
            print("[player.models.update_info] {}{} action: {:010} active: {:1} api: {:1} -> api error {}".format(progress, self, self.lastActionTS, self.active, self.validKey, user["apiError"]))
            self.save()
            return 0

        # skip if not active in torn since last update
        elif self.lastUpdateTS > int(user.get("last_action")["timestamp"]):
            print("[player.models.update_info] {}{} skip since not active since last update".format(progress, self))
            return 0

        # do update
        else:
            print("[player.models.update_info] {}{} action: {:010} active: {:1} api: {:1}".format(progress, self, self.lastActionTS, self.active, self.validKey))

        # update basic info (and chain)
        self.name = user.get("name", "?")
        self.factionId = user.get("faction", dict({})).get("faction_id", 0)
        self.factionNa = user.get("faction", dict({})).get("faction_name", "N/A")

        # update chain info
        if self.factionId:
            faction = Faction.objects.filter(tId=self.factionId).first()
            if faction is None:
                faction = Faction.objects.create(tId=self.factionId)
            faction.name = self.factionNa

            chains = apiCall("faction", "", "chains", self.key, verbose=False)
            if chains.get("chains") is not None:
                self.factionAA = True
                self.chainInfo = "{} [AA]".format(self.factionNa)
                faction.addKey(self.tId, self.key)
            else:
                self.factionAA = False
                self.chainInfo = "{}".format(self.factionNa)
                faction.delKey(self.tId)

            faction.save()

        else:
            self.factionAA = False
            self.chainInfo = "N/A"
        self.chainUpda = int(timezone.now().timestamp())

        # update awards info
        # tornAwards = apiCall('torn', '', 'honors,medals', self.key)
        tornAwards = AwardsData.objects.first().loadAPICall()
        if 'apiError' in tornAwards:
            self.awardsJson = json.dumps(tornAwards)
            self.awardsInfo = "0"
        else:
            updatePlayerAwards(self, tornAwards, user)
        self.awardsUpda = int(timezone.now().timestamp())

        # clean '' targets
        targetsAttacks = json.loads(self.targetJson)
        if len(targetsAttacks):
            targets = targetsAttacks.get("targets", dict({}))
            for k, v in targets.items():
                if k == '':
                    print("[player.models.update_info] delete target of player {}: {}".format(self, v))
            if targets.get('') is not None:
                del targets['']
            targetsAttacks["targets"] = targets
            self.targetJson = json.dumps(targetsAttacks)
            self.targetInfo = len(targets)

        self.lastUpdateTS = int(timezone.now().timestamp())
        self.save()

        # print("[player.models.update_info] {} / {}".format(self.chainInfo, self.awardsInfo))


class News(models.Model):
    player = models.ManyToManyField(Player, blank=True)
    type = models.CharField(default="Info", max_length=16)
    text = models.TextField()
    authorId = models.IntegerField(default=2000607)  # hopefully it will be relevent not to put this as default some day...
    authorName = models.CharField(default="Kivou", max_length=32)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{} of {:%Y/%M/%d} by {}".format(self.type, self.date, self.authorName)

    def read(self):
        return len(self.player.all())


class Message(models.Model):
    section = models.CharField(default="B", max_length=16, choices=SECTION_CHOICES)
    text = models.TextField()
    authorId = models.IntegerField(default=2000607)
    authorName = models.CharField(default="Kivou", max_length=32)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{} of {:%Y/%M/%d} by {}".format(self.section, self.date, self.authorName)


class Donation(models.Model):
    event = models.CharField(max_length=512)
    # You were sent {GIFT} from {SENDER} with the message: {MESSAGE} {DATE}

    def __str__(self):
        return self.event

    def split(self):
        spl = self.event.split(": ")

        spl1 = spl[0].split(" from ")
        gift = " ".join(spl1[0].split(" ")[3:])
        sender = spl1[1].split(" ")[0]

        spl2 = spl[1].split(" ")
        message = " ".join(spl2[:-2])
        date = " ".join(spl2[-2:])

        return {"date": date, "message": message, "sender": sender, "gift": gift}


class PlayerData(models.Model):
    nTotal = models.IntegerField(default=1)
    nValid = models.IntegerField(default=0)
    nInval = models.IntegerField(default=0)
    nPrune = models.IntegerField(default=0)
    nInact = models.IntegerField(default=0)

    nDay = models.IntegerField(default=0)
    nHour = models.IntegerField(default=0)
    nMonth = models.IntegerField(default=0)

    ipsBan = models.TextField(default="[]")

    def updateNumberOfPlayers(self):
        players = Player.objects.exclude(tId=-1)

        self.nTotal = len(players)
        self.nValid = len(players.filter(active=True).exclude(validKey=False))
        self.nInact = len(players.filter(active=False))
        self.nInval = len(players.filter(validKey=False))
        self.nPrune = len(players.filter(validKey=False).exclude(active=True))

        t = int(timezone.now().timestamp())
        self.nHour = len(players.filter(lastActionTS__gte=(t - (3600))))
        self.nDay = len(players.filter(lastActionTS__gte=(t - (24 * 3600))))
        self.nMonth = len(players.filter(lastActionTS__gte=(t - (31 * 24 * 3600))))

        self.save()
