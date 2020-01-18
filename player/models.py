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
# from awards.functions import updatePlayerAwards
# from faction.models import Faction
# from awards.models import AwardsData


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
    apikey = models.CharField(default="AAAA", max_length=16)

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

    # discord id and permission to give the bot the right to pull information
    dId = models.BigIntegerField(default=0)
    botPerm = models.BooleanField(default=False)
    activateNotifications = models.BooleanField(default=False)
    notifications = models.TextField(default="{}")

    def __str__(self):
        return "{:15} [{:07}]".format(self.name, self.tId)

    def getKey(self):
        key = self.key_set.first()
        return False if key is None else key.value

    def addKey(self, key):
        playerKey = self.key_set.first()
        if playerKey is None:
            self.key_set.create(value=key, tId=self.tId)
        else:
            playerKey.value = key
            playerKey.save()
        # temporary for the bot...
        self.apikey = key
        self.save()
        return


    def update_discord_id(self):
        error = False
        discord = apiCall("user", "", "discord", self.getKey())
        if 'apiError' in discord:
            error = {"apiErrorSub": discord["apiError"]}
        else:
            dId = discord.get('discord', {'discordID': ''})['discordID']
            self.dId = 0 if dId in [''] else dId
            self.save()

        return error


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


class Key(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)  # player
    tId = models.IntegerField(default=0)
    value = models.SlugField(default="aaaa", max_length=16)  # key
    lastPulled = models.IntegerField(default=0)  # ts when last pulled

    def __str__(self):
        return "Key of {}".format(self.player)
