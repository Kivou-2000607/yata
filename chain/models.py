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
import requests
import re

from yata.handy import apiCall


class Faction(models.Model):
    tId = models.IntegerField(default=0, unique=True)
    name = models.CharField(default="MyFaction", max_length=32)
    hitsThreshold = models.IntegerField(default=100)
    respect = models.IntegerField(default=0)

    lastAPICall = models.IntegerField(default=0)
    nAPICall = models.IntegerField(default=2)

    apiString = models.TextField(default="{}")
    posterOpt = models.TextField(default="{}")
    poster = models.BooleanField(default=False)
    posterHold = models.BooleanField(default=False)

    factionTree = models.TextField(default="{}")
    simuTree = models.TextField(default="{}")
    treeUpda = models.IntegerField(default=0)

    membersUpda = models.IntegerField(default=0)
    memberStatusUpda = models.IntegerField(default=0)
    memberStatus = models.TextField(default="{}")

    numberOfKeys = models.IntegerField(default=0)

    armoryRecord = models.BooleanField(default=False)
    armoryString = models.TextField(default="{}")
    fundsString = models.TextField(default="{}")
    networthString = models.TextField(default="{}")

    createLive = models.BooleanField(default=False)
    createReport = models.BooleanField(default=False)

    discordName = models.CharField(default="", max_length=32, null=True, blank=True)

    def __str__(self):
        return "{} [{}]".format(self.name, self.tId)

    def getFullName(self):
        return "{} [{}]".format(self.name, self.tId)

    def addKey(self, id, key):
        try:
            keys = json.loads(self.apiString)
        except BaseException:
            keys = {}
        if str(id) in keys:
            if keys[str(id)][:16] == key:
                pass
                # print("[model.faction.addKey] same key, nothing changed")
            else:
                # print("[model.faction.addKey] key changed")
                keys[str(id)] = key
        else:
            # print("[model.faction.addKey] new key")
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

    def updateMemberStatus(self):
        # get now and delta update
        now = int(timezone.now().timestamp())
        delta = now - self.memberStatusUpda
        if delta > 30:
            key = self.getRandomKey()
            membersAPI = apiCall('faction', '', 'basic', key[1], sub='members')
            if 'apiError' in membersAPI:
                return json.loads(self.memberStatus)

            # print("update members status", delta)
            self.memberStatus = json.dumps(membersAPI)
            self.memberStatusUpda = now
            self.save()
        # else:
        #     print("skip update members status", delta)

        return json.loads(self.memberStatus)


class Stat(models.Model):
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    timestamp = models.IntegerField(default=0)
    name = models.CharField(default="stat type", max_length=64)
    # type = models.IntegerField(default=0)
    contributors = models.TextField(default="{}")


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
    graphCrit = models.TextField(default="", null=True, blank=True)
    graphStat = models.TextField(default="", null=True, blank=True)
    wall = models.BooleanField(default=False)

    def __str__(self):
        if self.wall:
            return "{} wall #{}".format(self.faction, self.tId)
        else:
            return "{} chain #{}".format(self.faction, self.tId)

    def toggle_report(self):
        self.jointReport = not self.jointReport
        return self.jointReport


class Member(models.Model):
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    tId = models.IntegerField(default=0, unique=True)
    name = models.CharField(default="Duke", max_length=15)
    daysInFaction = models.IntegerField(default=0)

    # last action
    lastAction = models.CharField(default="-", max_length=200)
    lastActionTS = models.IntegerField(default=0)
    # status = models.CharField(default="-", max_length=200)

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


class Report(models.Model):
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE)

    def __str__(self):
        return("{} - Report".format(self.chain))


class Bonus(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    tId = models.IntegerField(default=0)
    name = models.CharField(default="Duke", max_length=15)
    hit = models.IntegerField(default=0)
    respect = models.FloatField(default=0)
    respectMax = models.FloatField(default=0)
    targetId = models.IntegerField(default=0)
    targetName = models.CharField(default="Unkown", max_length=15)

    def __str__(self):
        return("Bonus of {}".format(self.report.chain))


class Count(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    attackerId = models.IntegerField(default=0)
    name = models.CharField(default="Duke", max_length=15)
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

    def __str__(self):
        return("Attack {} of {}".format(self.pk, self.report))


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
    attackerFactionName = models.CharField(default="AttackFaction", max_length=32)
    defenderFactionId = models.IntegerField(default=0)
    defenderFactionName = models.CharField(default="DefendFaction", max_length=32)
    territory = models.CharField(default="AAA", max_length=3)
    result = models.CharField(default="Unset", max_length=10)
    factions = models.ManyToManyField(Faction, blank=True)
    # array of the two faction ID. Toggle wall for a faction adds/removes the ID to this array
    breakdown = models.TextField(default="[]", null=True, blank=True)
    # temporary bool only here to pass breakdown of the faction to template
    breakSingleFaction = models.BooleanField(default=False)

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


class AttacksBreakdown(models.Model):
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    tss = models.IntegerField(default=0)
    tse = models.IntegerField(default=0)
    live = models.BooleanField(default=False)
    computing = models.BooleanField(default=True)
    attackerFactions = models.TextField(default="[]")
    defenderFactions = models.TextField(default="[]")


class Attack(models.Model):
    breakdown = models.ForeignKey(AttacksBreakdown, on_delete=models.CASCADE)

    # API Fields
    tId = models.IntegerField(default=0)
    timestamp_started = models.IntegerField(default=0)
    timestamp_ended = models.IntegerField(default=0)
    attacker_id = models.IntegerField(default=0)
    attacker_name = models.CharField(default="attacker_name", max_length=16, null=True, blank=True)
    attacker_faction = models.IntegerField(default=0)
    attacker_factionname = models.CharField(default="attacker_factionname", max_length=32, null=True, blank=True)
    defender_id = models.IntegerField(default=0)
    defender_name = models.CharField(default="defender_name", max_length=16, null=True, blank=True)
    defender_faction = models.IntegerField(default=0)
    defender_factionname = models.CharField(default="defender_factionname", max_length=32, null=True, blank=True)
    result = models.CharField(default="result", max_length=32)
    stealthed = models.IntegerField(default=0)
    respect_gain = models.FloatField(default=0.0)
    chain = models.IntegerField(default=0)
    # mofifiers
    fairFight = models.FloatField(default=0.0)
    war = models.IntegerField(default=0)
    retaliation = models.FloatField(default=0.0)
    groupAttack = models.FloatField(default=0.0)
    overseas = models.FloatField(default=0.0)
    chainBonus = models.IntegerField(default=0)


class Territory(models.Model):
    tId = models.CharField(default="XXX", max_length=3)
    sector = models.IntegerField(default=0)
    size = models.IntegerField(default=0)
    density = models.IntegerField(default=0)
    daily_respect = models.IntegerField(default=0)
    coordinate_x = models.FloatField(default=0)
    coordinate_y = models.FloatField(default=0)
    faction = models.IntegerField(default=0)
    racket = models.TextField(default="{}", null=True, blank=True)

    def __str__(self):
        return "Territory {} [{}]".format(self.tId, self.faction)


class Racket(models.Model):
    # territory = models.ForeignKey(Territory, on_delete=models.CASCADE)
    tId = models.CharField(default="XXX", max_length=3)
    name = models.CharField(default="Racket Name", max_length=200)
    reward = models.CharField(default="Get nice things for free", max_length=200)
    created = models.IntegerField(default=0)
    changed = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    faction = models.IntegerField(default=0)

    def __str__(self):
        return "Racket {} [{}]".format(self.tId, self.faction)


class FactionData(models.Model):
    territoryTS = models.IntegerField(default=0)
    upgradeTree = models.TextField(default="{}", null=True, blank=True)


class ReviveContract(models.Model):
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)

    # timestamp input by user
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)

    # timestamp computed
    first = models.IntegerField(default=0)
    last = models.IntegerField(default=0)

    # to compute
    computing = models.BooleanField(default=True)
    owner = models.BooleanField(default=True)

    # number of revives
    revivesMade = models.IntegerField(default=0)
    revivesReceived = models.IntegerField(default=0)
    revivesContract = models.IntegerField(default=0)
    goal = models.IntegerField(default=0)

    # toggle factions
    factionsRevivers = models.TextField(default="[]")
    factionsTargets = models.TextField(default="[]")


# class ReviveContractShared(models.Model):
#     faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
#     contract = models.ForeignKey(ReviveContract, on_delete=models.CASCADE)


class Revive(models.Model):
    contract = models.ForeignKey(ReviveContract, on_delete=models.CASCADE)
    tId = models.IntegerField(default=0)
    timestamp = models.IntegerField(default=0)
    reviver_id = models.IntegerField(default=0)
    reviver_name = models.CharField(default="reviver_name", max_length=32)
    reviver_faction = models.IntegerField(default=0)
    reviver_factionname = models.CharField(default="reviver_factionname", null=True, blank=True, max_length=32)
    target_id = models.IntegerField(default=0)
    target_name = models.CharField(default="target_name", max_length=32)
    target_faction = models.IntegerField(default=0)
    target_factionname = models.CharField(default="target_factionname", null=True, blank=True, max_length=32)
