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
import json


class Preference(models.Model):
    allowedFactions = models.TextField(default="{}")


class Faction(models.Model):
    tId = models.IntegerField(default=0, unique=True)
    name = models.CharField(default="MyFaction", max_length=200)
    hitsThreshold = models.IntegerField(default=100)

    lastAPICall = models.IntegerField(default=0)
    nAPICall = models.IntegerField(default=2)

    apiString = models.TextField(default="{}")
    posterOpt = models.TextField(default="{}")
    poster = models.BooleanField(default=False)

    membersUpda = models.IntegerField(default=0)

    numberOfKeys = models.IntegerField(default=0)

    armoryRecord = models.BooleanField(default=False)
    armoryString = models.TextField(default="{}")

    def __str__(self):
        return "{} [{}]".format(self.name, self.tId)

    def addKey(self, id, key):
        try:
            keys = json.loads(self.apiString)
        except BaseException:
            keys = {}
        if str(id) in keys:
            if keys[str(id)][:16] == key:
                print("[model.faction.addKey] same key, nothing changed")
            else:
                print("[model.faction.addKey] key changed")
                keys[str(id)] = key
        else:
            print("[model.faction.addKey] new key")
            keys[str(id)] = key

        self.apiString = json.dumps(keys)
        self.numberOfKeys = self.nKeys()
        self.save()

    def toggleKey(self, id):
        try:
            keys = json.loads(self.apiString)
        except BaseException:
            keys = {}
        if str(id) in keys:
            if len(keys[str(id)]) == 16:
                keys[str(id)] += "0"
            elif len(keys[str(id)]) == 17:
                keys[str(id)] = keys[str(id)][:16]
        else:
            pass

        self.apiString = json.dumps(keys)
        self.numberOfKeys = self.nKeys()
        self.save()
        return id, keys.get(str(id), "0")

    def delKey(self, id):
        try:
            keys = json.loads(self.apiString)
        except BaseException:
            keys = {}
        if str(id) in keys:
            del keys[str(id)]

        self.apiString = json.dumps(keys)
        self.numberOfKeys = self.nKeys()
        self.save()

    def getRandomKey(self):
        import random
        try:
            keys = json.loads(self.apiString)
        except BaseException:
            keys = {}
        ignore = []
        for k, v in keys.items():
            if len(v) != 16:
                ignore.append(k)
        for k in ignore:
            del keys[k]
        return random.choice(list(keys.items())) if len(keys) else ("0", "")

    def getAllPairs(self, enabledKeys=False):
        try:
            keys = json.loads(self.apiString)
        except BaseException:
            keys = {}
        if enabledKeys:
            ignore = []
            for k, v in keys.items():
                if len(v) != 16:
                    ignore.append(k)
            for k in ignore:
                del keys[k]
        return list(keys.items())

    def numberOfReportsToCreate(self):
        return len(self.chain_set.filter(createReport=True))

    def liveChain(self):
        return bool(self.chain_set.filter(tId=0))

    def nKeys(self):
        try:
            keys = json.loads(self.apiString)
        except BaseException:
            keys = {}
        ignore = []
        for k, v in keys.items():
            if len(v) != 16:
                ignore.append(k)
        for k in ignore:
            del keys[k]
        return len(keys)


class Chain(models.Model):
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    tId = models.IntegerField(default=0)
    reportNHits = models.IntegerField(default=0)
    nHits = models.IntegerField(default=1)
    nAttacks = models.IntegerField(default=1)
    respect = models.FloatField(default=0)
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    lastUpdate = models.IntegerField(default=0)
    status = models.BooleanField(default=True)
    createReport = models.BooleanField(default=False)
    hasReport = models.BooleanField(default=False)
    jointReport = models.BooleanField(default=False)
    graph = models.TextField(default="", null=True, blank=True)

    def __str__(self):
        return "{} chain #{}".format(self.faction, self.tId)

    # def have_report(self):
    #     return True if len(self.report_set.all()) else False

    def toggle_report(self):
        self.jointReport = not self.jointReport
        return self.jointReport


class Member(models.Model):
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    tId = models.IntegerField(default=0, unique=True)
    name = models.CharField(default="Duke", max_length=15)
    daysInFaction = models.IntegerField(default=0)
    lastAction = models.CharField(default="-", max_length=200)
    status = models.CharField(default="-", max_length=200)

    def __str__(self):
        return "{} [{}]".format(self.name, self.tId)


class Report(models.Model):
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE)

    def __str__(self):
        return("{} - Report".format(self.chain))


class Bonus(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    tId = models.IntegerField(default=0)
    name = models.CharField(default="Duke", max_length=64)
    hit = models.IntegerField(default=0)
    respect = models.FloatField(default=0)
    respectMax = models.FloatField(default=0)

    def __str__(self):
        return("Bonus of {}".format(self.report.chain))


class Count(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    attackerId = models.IntegerField(default=0)
    name = models.CharField(default="Duke", max_length=64)
    hits = models.IntegerField(default=0)
    bonus = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    respect = models.FloatField(default=0)
    fairFight = models.FloatField(default=0)
    war = models.FloatField(default=0)
    retaliation = models.FloatField(default=0)
    groupAttack = models.FloatField(default=0)
    overseas = models.FloatField(default=0)
    daysInFaction = models.IntegerField(default=0)
    beenThere = models.BooleanField(default=False)
    graph = models.TextField(default="", null=True, blank=True)
    watcher = models.FloatField(default=0)
    warhits = models.IntegerField(default=0)

    def __str__(self):
        return("Count of {}".format(self.report.chain))


class Attacks(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    tss = models.IntegerField(default=0)
    tse = models.IntegerField(default=0)
    req = models.TextField()


class Crontab(models.Model):
    id = models.AutoField(primary_key=True)
    tabNumber = models.IntegerField(default=0)
    faction = models.ManyToManyField(Faction, blank=True)
    open = models.BooleanField(default=True)

    def __str__(self):
        return "Crontab #{}".format(self.tabNumber)

    def nFactions(self):
        return len(self.faction.all())


class Wall(models.Model):
    tId = models.IntegerField(default=0)
    tss = models.IntegerField(default=0)
    tse = models.IntegerField(default=0)
    attackers = models.TextField(default="{}", null=True, blank=True)
    defenders = models.TextField(default="{}", null=True, blank=True)
    attackerFactionId = models.IntegerField(default=0)
    attackerFactionName = models.CharField(default="AttackFaction", max_length=200)
    defenderFactionId = models.IntegerField(default=0)
    defenderFactionName = models.CharField(default="DefendFaction", max_length=200)
    territory = models.CharField(default="AAA", max_length=3)
    result = models.CharField(default="Timeout", max_length=3)
    factions = models.ManyToManyField(Faction, blank=True)


    def update(self, req):
        self.tId = int(req.get('tId'))
        self.tss = int(req.get('tss'))
        self.tse = int(req.get('tse'))
        self.attackers = req.get('attackers')
        self.defenders = req.get('defenders')
        self.attackerFactionId = int(req.get('attackerFactionId'))
        self.attackerFactionName = req.get('attackerFactionName')
        self.defenderFactionId = int(req.get('defenderFactionId'))
        self.defenderFactionName = req.get('defenderFactionName')
        self.territory = req.get('territory')
        self.result = req.get('result', 0)

        self.save()
