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

from awards.models import Call

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

    # info for stocks APP
    stocksInfo = models.CharField(default="N/A", max_length=255)
    stocksJson = models.TextField(default="{}")
    stocksUpda = models.IntegerField(default=0)

    def __str__(self):
        return "{:15} [{:07}]".format(self.name, self.tId)

    def update_info(self):
        """ update player information

        """
        from yata.handy import apiCall
        from awards.functions import updatePlayerAwards
        from chain.models import Faction
        import json

        # API Calls
        user = apiCall('user', '', 'personalstats,crimes,education,battlestats,workstats,perks,networth,merits,profile,medals,honors,icons,bars', self.key, verbose=False)

        # set boolean
        self.active = int(timezone.now().timestamp()) - self.lastActionTS < 60 * 60 * 24 * 31
        self.validKey = False if user.get('apiErrorCode', 0) == 2 else self.validKey

        if not self.active and not self.validKey:
            print("[player.models.update_info] {} action: {:010} active: {:1} api: {:1} -> delete user".format(self, self.lastActionTS, self.active, self.validKey))
            self.save()
            # self.delete()
            return 0
        elif 'apiError' in user:
            print("[player.models.update_info] {} action: {:010} active: {:1} api: {:1} -> api error {}".format(self, self.lastActionTS, self.active, self.validKey, user["apiError"]))
            return 0
        else:
            print("[player.models.update_info] {} action: {:010} active: {:1} api: {:1}".format(self, self.lastActionTS, self.active, self.validKey))

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
        tornAwards = Call.objects.first().load()
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
