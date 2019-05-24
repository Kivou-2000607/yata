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

class Player(models.Model):
    # user information: basic
    tId = models.IntegerField(default=4, unique=True)
    name = models.CharField(default="Duke", max_length=200)
    key = models.CharField(default="AAAA", max_length=16)

    # user information: faction
    factionId = models.IntegerField(default=0)
    factionAA = models.BooleanField(default=False)
    factionNa = models.CharField(default="My Faction", max_length=32)

    # user last update
    lastUpdateTS = models.IntegerField(default=0)

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

    def __str__(self):
        return "{} [{}]".format(self.name, self.tId)

    def update_info(self):
        """ update player information

        """
        print("[player.models.update_info] {}".format(self))
        from yata.handy import apiCall
        from awards.functions import updatePlayerAwards
        from chain.models import Faction
        import json

        # API Calls
        user = apiCall('user', '', 'personalstats,crimes,education,battlestats,workstats,perks,networth,merits,profile,medals,honors,icons', self.key)

        # update basic info (and chain)
        self.name = user.get("name", "?")
        self.factionId = user.get("faction", dict({})).get("faction_id", 0)
        self.factionNa = user.get("faction", dict({})).get("faction_name", "N/A")

        # update chain info
        if self.factionId:
            chains = apiCall("faction", "", "chains", self.key)
            if chains.get("chains") is not None:
                self.factionAA = True
                self.chainInfo = "{} [AA]".format(self.factionNa)
                Faction.objects.filter(tId=self.factionId).first().addKey(self.tId, self.key)
            else:
                self.factionAA = False
                self.chainInfo = "{}".format(self.factionNa)
                Faction.objects.filter(tId=self.factionId).first().delKey(self.tId)
        else:
            self.factionAA = False
            self.chainInfo = "N/A"
        self.chainUpda = int(timezone.now().timestamp())

        # update awards info
        tornAwards = apiCall('torn', '', 'honors,medals', self.key)
        if 'apiError' in tornAwards:
            self.awardsJson = json.dumps(tornAwards)
            self.awardsInfo = "0"
        else:
            updatePlayerAwards(self, tornAwards, user)
        self.awardsUpda = int(timezone.now().timestamp())

        self.lastUpdateTS = int(timezone.now().timestamp())
        self.save()

        print("[player.models.update_info] {} / {}".format(self.chainInfo, self.awardsInfo))
