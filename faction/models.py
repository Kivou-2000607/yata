"""
Copyright 2020 kivou.2000607@gmail.com

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
from django.forms.models import model_to_dict

import json
import requests
import re

from yata.handy import *
from player.models import Key
from player.models import Player


class Faction(models.Model):
    # direct torn values
    tId = models.IntegerField(default=0, unique=True)
    name = models.CharField(default="MyFaction", max_length=32)
    respect = models.IntegerField(default=0)

    # keys
    masterKeys = models.ManyToManyField(Key, blank=True)
    nKeys = models.IntegerField(default=0)

    # chain and attacks
    hitsThreshold = models.IntegerField(default=100)
    # lastAPICall = models.IntegerField(default=0)
    # nAPICall = models.IntegerField(default=2)
    # createLive = models.BooleanField(default=False)
    # createReport = models.BooleanField(default=False)

    # poster
    poster = models.BooleanField(default=False)
    posterHold = models.BooleanField(default=False)
    posterOpt = models.TextField(default="{}")

    # respect simulator: TODO
    # factionTree = models.TextField(default="{}")
    # simuTree = models.TextField(default="{}")
    # treeUpda = models.IntegerField(default=0)

    # members
    membersUpda = models.IntegerField(default=0)
    memberStatus = models.TextField(default="{}")  # dump all members status
    memberStatusUpda = models.IntegerField(default=0)

    # armory / networth: TODO
    # armoryRecord = models.BooleanField(default=False)
    # armoryString = models.TextField(default="{}")
    # fundsString = models.TextField(default="{}")
    # networthString = models.TextField(default="{}")

    # discord
    # discordName = models.CharField(default="", max_length=32, null=True, blank=True)

    def __str__(self):
        return "{} [{}]".format(self.name, self.tId)

    def manageKey(self, player):
        key = player.key_set.first()
        if player.factionAA and player.validKey:
            self.masterKeys.add(key)
        else:
            self.masterKeys.remove(key)

        self.nKeys = len(self.masterKeys.filter(useFact=True))
        self.save()

    def getKey(self):
        key = self.masterKeys.filter(useFact=True).order_by("lastPulled").first()
        # key.lastPulled = tsnow()
        # key.save()
        return key

    def delKey(self, tId=None, player=None, key=None):
        if player is not None:
            key = player.key_set.first()
            self.masterKeys.remove(key)
        elif tId is not None:
            player = Player.objects.filter(tId=tId).first()
            key = player.key_set.first()
            self.masterKeys.remove(key)
        elif key is not None:
            self.masterKeys.remove(key)

        return key

    def getKeys(self, ignored=False):
        if ignored:
            return {k.player.tId: k.value for k in self.masterKeys.filter(useSelf=True)}
        else:
            return {k.player.tId: k.value for k in self.masterKeys.filter(useFact=True)}

    def updateMemberStatus(self, key=None):
        # get now and delta update
        now = tsnow()
        delta = now - self.memberStatusUpda
        if delta > 30:
            key = self.getKey() if key is None else key
            membersAPI = apiCall('faction', '', 'basic', key.value, sub='members')
            key.lastPulled = now
            key.reason = "Faction -> Members status"
            key.save()

            if 'apiError' in membersAPI:
                return json.loads(self.memberStatus)

            # print("update members status", delta)
            self.memberStatus = json.dumps(membersAPI)
            self.memberStatusUpda = now
            self.save()
        # else:
        #     print("skip update members status", delta)

        return json.loads(self.memberStatus)


class Member(models.Model):
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    tId = models.IntegerField(default=0, unique=True)
    name = models.CharField(default="Duke", max_length=15)
    daysInFaction = models.IntegerField(default=0)

    # last action
    lastAction = models.CharField(default="-", max_length=200)
    lastActionTS = models.IntegerField(default=0)

    # new status of december 2019
    description = models.CharField(default="", max_length=128, blank=True)
    details = models.CharField(default="", max_length=128, blank=True)
    state = models.CharField(default="", max_length=32, blank=True)
    color = models.CharField(default="", max_length=16, blank=True)
    until = models.IntegerField(default=0)

    # share energy and NNB with faction
    # -1: not on YATA 0: doesn't wish to share 1: share
    shareE = models.IntegerField(default=-1)
    energy = models.IntegerField(default=0)

    # share natural nerve bar
    # -1: not on YATA 0: doesn't wish to share 1: share
    shareN = models.IntegerField(default=-1)
    nnb = models.IntegerField(default=0)
    arson = models.IntegerField(default=0)

    def __str__(self):
        return "{} [{}]".format(self.name, self.tId)

    def updateStatus(self, description=None, details=None, state=None, color=None, until=None, save=False, **args):
        # the **args is here to hade extra keys not needed
        if description is not None:
            self.description = description
        if details is not None:
            self.details = details
        if state is not None:
            self.state = state
        if color is not None:
            self.color = color
        if until is not None:
            self.until = until
        if save:
            self.save()

    def updateEnergy(self, key=None, req=False):
        error = False
        if not self.shareE:
            self.energy = 0
        else:
            if not req:
                req = apiCall("user", "", "bars", key=key)

            # url = "https://api.torn.com/user/?selections=bars&key=2{}".format(key)
            # req = requests.get(url).json()
            if 'apiError' in req:
                error = req
                self.energy = 0
            else:
                energy = req['energy'].get('current', 0)
                self.energy = energy

        self.save()

        return error

    def updateNNB(self, key=None, req=False):
        error = False
        if not self.shareN:
            self.nnb = 0
        else:
            if not req:
                req = apiCall("user", "", "perks,bars,crimes", key=key)

            if 'apiError' in req:
                error = req
                self.nnb = 0
            else:
                nnb = req['nerve'].get('maximum', 0)

                # company perks
                for p in req.get("company_perks", []):
                    sp = p.split(' ')
                    # not python 3.5 compatible
                    # match = re.match(r'([+]){1} (\d){1,2} ([mMaximum]){7} nerve', p)
                    if len(sp) == 4 and sp[3] == "nerve" and sp[2] == "maximum":
                        nnb -= int(sp[1])

                # faction perks
                for p in req.get("faction_perks", []):
                    sp = p.split(' ')
                    if len(sp) == 6 and sp[3] == "nerve" and sp[2] == "maximum":
                        nnb -= int(sp[5])

                # merit perks
                for p in req.get("merit_perks", []):
                    sp = p.split(' ')
                    if len(sp) == 4 and sp[3] == "nerve" and sp[2] == "Maximum":
                        nnb -= int(sp[1])

                self.nnb = nnb
                self.arson = req["criminalrecord"].get("fraud_crimes", 0)

        self.save()
        return error
