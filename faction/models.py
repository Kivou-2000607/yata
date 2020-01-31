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
from faction.functions import *

BONUS_HITS = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000]
OPEN_CRONTAB = [1, 2, 3]
CHAIN_ATTACKS_STATUS = {
    3: "Normal [continue]",
    2: "Reached end of chain [stop]",
    1: "No new attack [stop]",
    0: "Waiting for first call",
    -1: "No enabled AA keys [stop]",
    -2: "API key major error (key deleted) [continue]",
    -3: "API key temporary error [continue]",
    -4: "Probably cached response [continue]",
    -5: "Empty payload [stop]",
    -6: "No new entry [continue]",
    }
REPORT_ATTACKS_STATUS = {
    3: "Normal [continue]",
    2: "Up to date [continue]",
    1: "No new attack [stop]",
    0: "Waiting for first call",
    -1: "No enabled AA keys [stop]",
    -2: "API key major error (key deleted) [continue]",
    -3: "API key temporary error [continue]",
    -4: "Probably cached response [continue]",
    -5: "Empty payload [stop]",
    -6: "No new entry [continue]",
    }


# Faction
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
    lastAttacksPulled = models.IntegerField(default=0)
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

    def fullname(self):
        return "{} [{}]".format(self.name, self.tId)

    def manageKey(self, player):
        key = player.key_set.first()
        if player.factionAA and player.validKey:
            self.masterKeys.add(key)
        else:
            self.masterKeys.remove(key)

        self.nKeys = len(self.masterKeys.filter(useFact=True))
        self.save()

    def getKey(self, useFact=True):
        key = self.masterKeys.filter(useFact=useFact).order_by("lastPulled").first()
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

    def updateMembers(self, key=None, force=True, indRefresh=False):
        # it's not possible to delete all memebers and recreate the base
        # otherwise the target list will be lost

        now = int(timezone.now().timestamp())

        # don't update if less than 1 hour ago and force is False
        if not force and (now - self.membersUpda) < 3600:
            print("{} skip update member".format(self))
            return self.member_set.all()

        # get key if needed
        if key is None:
            key = self.getKey()

        # call members and return error
        membersAPI = apiCall('faction', '', 'basic', key.value, sub='members')
        key.lastPulled = tsnow()
        key.reason = "Update member list"
        key.save()

        if 'apiError' in membersAPI:
            return membersAPI

        membersDB = self.member_set.all()
        for m in membersAPI:
            memberDB = membersDB.filter(tId=m).first()

            # faction member already exists
            if memberDB is not None:
                # update basics
                memberDB.name = membersAPI[m]['name']
                memberDB.lastAction = membersAPI[m]['last_action']['relative']
                memberDB.lastActionTS = membersAPI[m]['last_action']['timestamp']
                memberDB.daysInFaction = membersAPI[m]['days_in_faction']

                # update status
                memberDB.updateStatus(**membersAPI[m]['status'])

                # update energy/NNB
                player = Player.objects.filter(tId=memberDB.tId).first()
                if player is None:
                    memberDB.shareE = -1
                    memberDB.energy = 0
                    memberDB.shareN = -1
                    memberDB.nnb = 0
                    memberDB.arson = 0
                else:
                    if indRefresh and memberDB.shareE and memberDB.shareN:
                        req = apiCall("user", "", "perks,bars,crimes", key=player.getKey())
                        memberDB.updateEnergy(key=player.getKey(), req=req)
                        memberDB.updateNNB(key=player.getKey(), req=req)
                    elif indRefresh and memberDB.shareE:
                        memberDB.updateEnergy(key=player.getKey())
                    elif indRefresh and memberDB.shareN:
                        memberDB.updateNNB(key=player.getKey())

                memberDB.save()

            # member exists but from another faction
            elif Member.objects.filter(tId=m).first() is not None:
                memberTmp = Member.objects.filter(tId=m).first()
                memberTmp.faction = faction
                memberTmp.name = membersAPI[m]['name']
                memberTmp.lastAction = membersAPI[m]['last_action']['relative']
                memberTmp.lastActionTS = membersAPI[m]['last_action']['timestamp']
                memberTmp.daysInFaction = membersAPI[m]['days_in_faction']
                memberTmp.updateStatus(**membersAPI[m]['status'])

                # set shares to 0
                player = Player.objects.filter(tId=memberTmp.tId).first()
                memberTmp.shareE = -1 if player is None else 0
                memberTmp.shareN = -1 if player is None else 0
                memberTmp.energy = 0
                memberTmp.nnb = 0
                memberTmp.arson = 0

                memberTmp.save()

            # new member
            else:
                # print('[VIEW members] member {} [{}] created'.format(membersAPI[m]['name'], m))
                player = Player.objects.filter(tId=m).first()
                memberNew = self.member_set.create(
                    tId=m, name=membersAPI[m]['name'],
                    lastAction=membersAPI[m]['last_action']['relative'],
                    lastActionTS=membersAPI[m]['last_action']['timestamp'],
                    daysInFaction=membersAPI[m]['days_in_faction'],
                    shareE=-1 if player is None else 0,
                    shareN=-1 if player is None else 0,
                    )
                memberNew.updateStatus(**membersAPI[m]['status'])

        # delete old members
        for m in membersDB:
            if membersAPI.get(str(m.tId)) is None:
                m.delete()

        # remove AA keys from old members
        for key in self.masterKeys.all():
            if not len(self.member_set.filter(tId=key.tId)):
                self.delKey(tId=key.tId)

        self.nKeys = len(self.masterKeys.filter(useFact=True))
        self.membersUpda = now
        self.memberStatusUpda = now
        self.save()
        return self.member_set.all()

    def updateMemberStatus(self, key=None):
        # get now and delta update
        now = tsnow()
        delta = now - self.memberStatusUpda
        if delta > 30:
            key = self.getKey() if key is None else key
            membersAPI = apiCall('faction', '', 'basic', key.value, sub='members')
            key.lastPulled = now
            key.reason = "Update member status"
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


# Chains
class Chain(models.Model):
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)

    # torn api
    tId = models.IntegerField(default=0)
    chain = models.IntegerField(default=0)
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    respect = models.FloatField(default=0)

    # information to compute report
    report = models.BooleanField(default=False)  # if report is computed/ing
    computing = models.BooleanField(default=False)  # if currently computing
    live = models.BooleanField(default=False)  # if live chain
    update = models.IntegerField(default=0)  # ts of last update
    last = models.IntegerField(default=0)  # ts of last attack
    state = models.IntegerField(default=0)  # output status of last attack pulled
    crontab = models.IntegerField(default=0)  # to see on which crontab the report will be computed

    # information for the report
    current = models.IntegerField(default=0)
    attacks = models.IntegerField(default=0)
    graphs = models.TextField(default="{}", null=True, blank=True)

    # for the combined report
    combine = models.BooleanField(default=False)

    def __str__(self):
        return "{} chain [{}]".format(self.faction, self.tId)

    def assignCrontab(self):
        # check if already in a crontab
        chain = self.faction.chain_set.filter(computing=True).only("crontab").first()
        if chain is None or chain.crontab not in OPEN_CRONTAB:
            cn = {c: len(Chain.objects.filter(crontab=c).only('crontab')) for c in OPEN_CRONTAB}
            self.crontab = sorted(cn.items(), key=lambda x: x[1])[0][0]
        elif chain is not None:
            self.crontab = chain.crontab
        self.save()
        return self.crontab

    def getAttacks(self):
        """ Fill chain with attacks
        """
        # handle live chain
        if self.live:
            self.end = tsnow()

        # shortcuts
        faction = self.faction
        tss = self.start
        tse = self.end

        # compute last ts
        lastAttack = self.attackchain_set.order_by("-timestamp_ended").first()
        tsl = self.start if lastAttack is None else lastAttack.timestamp_ended
        self.last = tsl

        print("{} live {}".format(self, self.live))
        print("{} start {}".format(self, timestampToDate(tss)))
        print("{} last  {}".format(self, timestampToDate(tsl)))
        print("{} end   {}".format(self, timestampToDate(tse)))

        # add + 2 s to the endTS
        tse += 10

        # get existing attacks (just the ids)
        attacks = [r.tId for r in self.attackchain_set.all()]
        print("{} {} existing attacks".format(self, len(attacks)))

        # get key
        key = faction.getKey(useFact=True)
        if key is None:
            print("{} no key".format(self))
            self.computing = False
            self.crontab = 0
            self.attackchain_set.all().delete()
            self.state = -1
            self.save()
            return -1

        # prevent cache response
        delay = tsnow() - self.update
        delay = min(tsnow() - faction.lastAttacksPulled, delay)
        if delay < 32:
            sleeptime = 32 - delay
            print("{} last update {}s ago, waiting {} for cache...".format(self, delay, sleeptime))
            time.sleep(sleeptime)

        # make call
        selection = "chain,attacks,timestamp&from={}&to={}".format(tsl, tse)
        req = apiCall("faction", faction.tId, selection, key.value, verbose=False)
        key.reason = "Pull attacks for chain report"
        key.lastPulled = tsnow()
        key.save()
        self.update = tsnow()
        faction.lastAttacksPulled = self.update
        faction.save()

        # in case there is an API error
        if "apiError" in req:
            print('{} api key error: {}'.format(self, req['apiError']))
            if req['apiErrorCode'] in API_CODE_DELETE:
                print("{} --> deleting {}'s key from faction (blank turn)".format(self, key.player))
                faction.delKey(key=key)
                self.state = -2
                self.save()
                return -2
            self.state = -3
            self.save()
            return -3

        # try to catch cache response
        tornTS = int(req["timestamp"])
        nowTS = self.update
        cache = abs(nowTS - tornTS)
        print("{} cache = {}s".format(self, cache))

        # in case cache
        if cache > 5:
            print('{} probably cached response... (blank turn)'.format(self))
            self.state = -4
            self.save()
            return -4

        if self.live:
            print("{} update values".format(self))
            self.chain = req["chain"]["current"]

        apiAttacks = req["attacks"]

        # in case empty payload
        if not len(apiAttacks):
            print('{} empty payload'.format(self))
            self.computing = False
            self.crontab = 0
            self.state = -5
            self.save()
            return -5

        print("{} {} attacks from the API".format(self, len(apiAttacks)))

        newEntry = 0
        for k, v in apiAttacks.items():
            ts = int(v["timestamp_ended"])

            # probably because of cache
            before = int(v["timestamp_ended"]) - self.last
            after = int(v["timestamp_ended"]) - tse
            if before < 0 or after > 0:
                print("{} /!\ ts out of bound: before = {} after = {}".format(self, before, after))

            newAttack = int(k) not in attacks
            factionAttack = v["attacker_faction"] == faction.tId
            # chainAttack = int(v["chain"])
            if newAttack and factionAttack:
                v = modifiers2lvl1(v)
                self.attackchain_set.create(tId=int(k), **v)
                newEntry += 1
                tsl = max(tsl, ts)
                self.current = max(self.current, v["chain"])
                # print("{} attack [{}] current {}".format(self, k, current))

        self.last = tsl

        print("{} last  {}".format(self, timestampToDate(self.last)))
        print("{} new entries {}".format(self, newEntry))
        print("{} progress {} / {} ({})%".format(self, self.current, self.chain, self.progress()))

        if self.live:
            # stopping criterions of standard chains
            if req["chain"]["current"] < 10:
                print("{} reached end of live chain (stop)".format(self))
                self.computing = False
                self.crontab = 0
                self.state = 2
                self.save()
                return 2

        else:
            if not newEntry and len(apiAttacks) > 1 and self:
                print("{} no new entry from payload (continue)".format(self))
                self.state = -6
                self.save()
                return -6

            if self.current == self.chain:
                print("{} Reached end of chain (stop)".format(self))
                self.computing = False
                self.crontab = 0
                self.state = 2
                self.save()
                return 2

            if len(apiAttacks) < 2:
                print("{} no api entry for non live report (stop)".format(self))
                self.computing = False
                self.crontab = 0
                self.state = 1
                self.save()
                return 1

        self.state = 3
        self.save()
        return 3

    def fillReport(self):
        # get faction / key
        faction = self.faction
        key = faction.getKey()

        # get members
        members = faction.updateMembers(key=key, force=False)

        # initialisation of variables before loop
        nWRA = [0, 0.0, 0, 0]  # number of wins, respect and attacks, max count (should be = to number of wins)
        bonus = []  # chain bonus
        attacksForHisto = []  # record attacks timestamp histogram
        attacksCriticalForHisto = dict({"30": [], "60": [], "90": []})  # record critical attacks timestamp histogram

        # create attackers array on the fly to avoid db connection in the loop
        attackers = dict({})
        attackersHisto = dict({})
        for m in members:
            # 0: attacks
            # 1: wins
            # 2: fairFight
            # 3: war
            # 4: retaliation
            # 5: groupAttack
            # 6: overseas
            # 7: chainBonus
            # 8: respect_gain
            # 9: daysInFaction
            # 10: tId
            # 11: sum(time(hit)-time(lasthit))
            # 12: #bonuses
            # 13: #war
            attackers[m.tId] = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, m.daysInFaction, m.name, 0, 0, 0]

        #  for debug
        # PRINT_NAME = {"Thiirteen": 0,}
        # chainIterator = []

        # loop over attacks
        lastTS = 0
        for att in self.attackchain_set.order_by('timestamp_ended'):
            attackerID = att.attacker_id
            attackerName = att.attacker_name
            # if attacker part of the faction at the time of the chain
            if att.attacker_faction == faction.tId:
                # if attacker not part of the faction at the time of the call
                if attackerID not in attackers:
                    # print('[function.chain.fillReport] hitter out of faction: {} [{}]'.format(attackerName, attackerID))
                    attackers[attackerID] = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1, attackerName, 0, 0, 0]  # add out of faction attackers on the fly

                attackers[attackerID][0] += 1
                nWRA[2] += 1

                # if it's a hit
                # if respect > 0.0 and chainCount == 0:
                #     print("[function.chain.fillReport] Attack with respect but no hit {}:".format(k))
                #     for kk, vv in v.items():
                #         print("[function.chain.fillReport] \t{}: {}".format(kk, vv))
                if att.chain:
                    # chainIterator.append(v["chain"])
                    # print("Time stamp:", att.timestamp_ended)

                    # init lastTS for the first iteration of the loop
                    lastTS = att.timestamp_ended if lastTS == 0 else lastTS

                    # compute chain watcher version 2
                    timeSince = att.timestamp_ended - lastTS
                    attackers[attackerID][11] += timeSince
                    lastTS = att.timestamp_ended

                    # add to critical attack
                    timeLeft = max(300 - timeSince, 0)
                    if timeLeft < 30:
                        attacksCriticalForHisto["30"].append(att.timestamp_ended)
                    elif timeLeft < 60:
                        attacksCriticalForHisto["60"].append(att.timestamp_ended)
                    elif timeLeft < 90:
                        attacksCriticalForHisto["90"].append(att.timestamp_ended)

                    attacksForHisto.append(att.timestamp_ended)
                    if attackerID in attackersHisto:
                        attackersHisto[attackerID].append(att.timestamp_ended)
                    else:
                        attackersHisto[attackerID] = [att.timestamp_ended]

                    nWRA[0] += 1
                    nWRA[1] += att.respect_gain
                    nWRA[3] = max(att.chain, nWRA[3])

                    if att.chain in BONUS_HITS:
                        attackers[attackerID][12] += 1
                        r = getBonusHits(att.chain, att.timestamp_ended)
                        # print('{} bonus {}: {} respects'.format(self, att.chain, r))
                        bonus.append((att.chain, attackerID, attackerName, att.respect_gain, r, att.defender_id, att.defender_name))
                    else:
                        attackers[attackerID][1] += 1
                        attackers[attackerID][2] += float(att.fairFight)
                        attackers[attackerID][3] += float(att.war)
                        attackers[attackerID][4] += float(att.retaliation)
                        attackers[attackerID][5] += float(att.groupAttack)
                        attackers[attackerID][6] += float(att.overseas)
                        attackers[attackerID][7] += float(att.chainBonus)
                        attackers[attackerID][8] += float(att.respect_gain) / float(att.chainBonus)
                        if float(att.war) > 1.0:
                            attackers[attackerID][13] += 1

                # else:
                #     print("[function.chain.fillReport] Attack {} -> {}: {} (respect {})".format(v['attacker_factionname'], v["defender_factionname"], v['result'], v['respect_gain']))
                # if(v["attacker_name"] in PRINT_NAME):
                #     if respect > 0.0:
                #         PRINT_NAME[v["attacker_name"]] += 1
                #         print("[function.chain.fillReport] {} {} -> {}: {} respect".format(v['result'], v['attacker_name'], v["defender_name"], v['respect_gain']))
                #     else:
                #         print("[function.chain.fillReport] {} {} -> {}: {} respect".format(v['result'], v['attacker_name'], v["defender_name"], v['respect_gain']))

        # for k, v in PRINT_NAME.items():
        #     print("[function.chain.fillReport] {}: {}".format(k, v))
        #
        # for i in range(1001):
        #     if i not in chainIterator:
        #         print(i, "not in chain")

        # create histogram
        # chain.start = int(attacksForHisto[0])
        # chain.end = int(attacksForHisto[-1])
        diff = max(int(self.end - self.start), 1)
        binsGapMinutes = 5
        while diff / (binsGapMinutes * 60) > 256:
            binsGapMinutes += 5

        bins = [self.start]
        for i in range(256):
            add = bins[i] + (binsGapMinutes * 60)
            if add > self.end:
                break
            bins.append(add)

        # bins = max(min(int(diff / (5 * 60)), 256), 1)  # min is to limite the number of bins for long chains and max is to insure minimum 1 bin
        # print('{} chain delta time: {} second'.format(self, diff))
        # print('{} histogram bins delta time: {} second'.format(self, binsGapMinutes * 60))
        # print('{} histogram number of bins: {}'.format(self, len(bins) - 1))

        # fill attack histogram
        histo, bin_edges = numpy.histogram(attacksForHisto, bins=bins)
        binsCenter = [int(0.5 * (a + b)) for (a, b) in zip(bin_edges[0:-1], bin_edges[1:])]
        graphs = dict({})
        graphs["hits"] = ','.join(['{}:{}'.format(a, b) for (a, b) in zip(binsCenter, histo)])

        # fill 30, 60, 90s critical attacks histogram
        histo30, _ = numpy.histogram(attacksCriticalForHisto["30"], bins=bins)
        histo60, _ = numpy.histogram(attacksCriticalForHisto["60"], bins=bins)
        histo90, _ = numpy.histogram(attacksCriticalForHisto["90"], bins=bins)
        graphs["crit"] = ','.join(['{}:{}:{}'.format(a, b, c) for (a, b, c) in zip(histo30, histo60, histo90)])

        # potentially add this to chain to compare with API
        if self.live:
            # self.chain = nWRA[0]  # update for live chains
            self.respect = nWRA[1]  # update for live chains
        self.attacks = nWRA[2]
        self.save()

        # fill the database with counts
        print('{} fill database with counts'.format(self))
        self.count_set.all().delete()
        hitsForStats = []
        for k, v in attackers.items():
            # for stats later
            if v[1]:
                hitsForStats.append(v[1])

            # time now - chain end - days old: determine if member was in the fac for the chain
            delta = int(timezone.now().timestamp()) - self.end - v[9] * 24 * 3600
            beenThere = True if (delta < 0 or v[9] < 0) else False
            if k in attackersHisto:
                histoTmp, _ = numpy.histogram(attackersHisto[k], bins=bins)
                # watcher = sum(histoTmp > 0) / float(len(histoTmp)) if len(histo) else 0
                watcher = v[11] / float(diff)
                graphTmp = ','.join(['{}:{}'.format(a, b) for (a, b) in zip(binsCenter, histoTmp)])
            else:
                graphTmp = ''
                watcher = 0
            # 0: attacks
            # 1: wins
            # 2: fairFight
            # 3: war
            # 4: retaliation
            # 5: groupAttack
            # 6: overseas
            # 7: chainBonus
            # 8:respect_gain
            # 9: daysInFaction
            # 10: tId
            # 11: for chain watch
            # 12: #bonuses
            # 13: #war
            self.count_set.create(attackerId=k,
                                  name=v[10],
                                  hits=v[0],
                                  wins=v[1],
                                  bonus=v[12],
                                  fairFight=v[2],
                                  war=v[3],
                                  retaliation=v[4],
                                  groupAttack=v[5],
                                  overseas=v[6],
                                  respect=v[8],
                                  daysInFaction=v[9],
                                  beenThere=beenThere,
                                  graph=graphTmp,
                                  watcher=watcher,
                                  warhits=v[13])

        # create attack stats
        stats, statsBins = numpy.histogram(hitsForStats, bins=32)
        statsBinsCenter = [int(0.5 * (a + b)) for (a, b) in zip(statsBins[0:-1], statsBins[1:])]
        graphs["members"] = ','.join(['{}:{}'.format(a, b) for (a, b) in zip(statsBinsCenter, stats)])
        self.graphs = json.dumps(graphs)

        # fill the database with bonus
        print('{} fill database with bonus'.format(self))
        self.bonus_set.all().delete()
        for b in bonus:
            self.bonus_set.create(hit=b[0], tId=b[1], name=b[2], respect=b[3], targetId=b[5], targetName=b[6])

        self.save()
        return 0

    def progress(self):
        return int((100 * self.current) // float(max(1, self.chain)))

    def displayCrontab(self):
        if self.crontab > 0:
            return "#{}".format(self.crontab)
        elif self.crontab == 0:
            return "No crontab assigned"
        else:
            return "Special crontab you lucky bastard..."


class Count(models.Model):
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE)
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
        return("Count for {}".format(self.chain))


class Bonus(models.Model):
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE)
    tId = models.IntegerField(default=0)
    name = models.CharField(default="Duke", max_length=15)
    hit = models.IntegerField(default=0)
    respect = models.FloatField(default=0)
    targetId = models.IntegerField(default=0)
    targetName = models.CharField(default="Unkown", max_length=15)

    def __str__(self):
        return("Bonus for {}".format(self.chain))


class AttackChain(models.Model):
    report = models.ForeignKey(Chain, on_delete=models.CASCADE)

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

    def __str__(self):
        return "Attack for chain [{}]".format(self.tId)


# Walls
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

    def __str__(self):
        return "Wall [{}]".format(self.tId)


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

    def getReport(self, faction):
        # WARNING a wall does not belong to a single faction
        # get potential report
        report = self.attacksreport_set.first()
        if report is None:
            return False
        else:
            return report if faction in [f for f in self.factions.all()] else False


# Attacks report
class AttacksReport(models.Model):
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    last = models.IntegerField(default=0)
    live = models.BooleanField(default=False)

    # information for computing
    computing = models.BooleanField(default=True)
    state = models.IntegerField(default=0)  # output status of last attack pulled
    crontab = models.IntegerField(default=0)
    update = models.IntegerField(default=0)

    # global information for the report
    attackerFactions = models.TextField(default="[]")
    defenderFactions = models.TextField(default="[]")
    defends = models.IntegerField(default=0)
    attacks = models.IntegerField(default=0)

    # link to wall
    wall = models.ManyToManyField(Wall, blank=True)

    def __str__(self):
        return "{} report [{}]".format(self.faction, self.pk)

    def progress(self):
        end = self.end if self.end else tsnow()
        last = self.last if self.last else self.start
        total = max(end - self.start, 1)
        elaps = last - self.start
        return int((100 * elaps) // float(total))

    def displayCrontab(self):
        if self.crontab > 0:
            return "#{}".format(self.crontab)
        elif self.crontab == 0:
            return "No crontab assigned"
        else:
            return "Special crontab you lucky bastard..."

    def assignCrontab(self):
        # check if already in a crontab
        report = self.faction.attacksreport_set.filter(computing=True).only("crontab").first()
        if report is None or report.crontab not in OPEN_CRONTAB:
            cn = {c: len(AttacksReport.objects.filter(crontab=c).only('crontab')) for c in OPEN_CRONTAB}
            self.crontab = sorted(cn.items(), key=lambda x: x[1])[0][0]
        elif report is not None:
            self.crontab = report.crontab
        self.save()
        return self.crontab

    def getAttacks(self):
        """ Fill report with attacks
        """
        # handle live chain
        if self.live:
            self.end = tsnow()

        # shortcuts
        faction = self.faction
        tss = self.start
        tse = self.end

        # compute last ts
        lastAttack = self.attackreport_set.order_by("-timestamp_ended").first()
        tsl = self.start if lastAttack is None else lastAttack.timestamp_ended
        self.last = tsl

        print("{} live {}".format(self, self.live))
        print("{} start {}".format(self, timestampToDate(tss)))
        print("{} last  {}".format(self, timestampToDate(tsl)))
        print("{} end   {}".format(self, timestampToDate(tse)))

        # add + 2 s to the endTS
        tse += 10

        # get existing attacks (just the ids)
        attacks = [r.tId for r in self.attackreport_set.all()]
        print("{} {} existing attacks".format(self, len(attacks)))

        # get key
        key = faction.getKey(useFact=True)
        if key is None:
            print("{} no key".format(self))
            self.computing = False
            self.crontab = 0
            self.attackreport_set.all().delete()
            self.state = -1
            self.save()
            return -1

        # prevent cache response
        delay = tsnow() - self.update
        delay = min(tsnow() - faction.lastAttacksPulled, delay)
        if delay < 32:
            sleeptime = 32 - delay
            print("{} last update {}s ago, waiting {} for cache...".format(self, delay, sleeptime))
            time.sleep(sleeptime)

        # make call
        selection = "attacks,timestamp&from={}&to={}".format(tsl, tse)
        req = apiCall("faction", faction.tId, selection, key.value, verbose=False)
        key.reason = "Pull attacks for attacks report"
        key.lastPulled = tsnow()
        key.save()
        self.update = tsnow()
        faction.lastAttacksPulled = self.update
        faction.save()

        # in case there is an API error
        if "apiError" in req:
            print('{} api key error: {}'.format(self, req['apiError']))
            if req['apiErrorCode'] in API_CODE_DELETE:
                print("{} --> deleting {}'s key from faction (blank turn)".format(self, key.player))
                faction.delKey(key=key)
                self.state = -2
                self.save()
                return -2
            self.state = -3
            self.save()
            return -3

        # try to catch cache response
        tornTS = int(req["timestamp"])
        nowTS = self.update
        cache = abs(nowTS - tornTS)
        print("{} cache = {}s".format(self, cache))

        # in case cache
        if cache > 5:
            print('{} probably cached response... (blank turn)'.format(self))
            self.state = -4
            self.save()
            return -4

        apiAttacks = req["attacks"]

        # in case empty payload
        if not len(apiAttacks):
            print('{} empty payload'.format(self))
            self.computing = False
            self.crontab = 0
            self.state = -5
            self.save()
            return -5

        print("{} {} attacks from the API".format(self, len(apiAttacks)))

        newEntry = 0
        for k, v in apiAttacks.items():
            ts = int(v["timestamp_ended"])

            # probably because of cache
            before = int(v["timestamp_ended"]) - self.last
            after = int(v["timestamp_ended"]) - tse
            if before < 0 or after > 0:
                print("{} /!\ ts out of bound: before = {} after = {}".format(self, before, after))

            newAttack = int(k) not in attacks
            factionAttack = v["attacker_faction"] == faction.tId
            # chainAttack = int(v["chain"])
            if newAttack:
                v = modifiers2lvl1(v)
                self.attackreport_set.create(tId=int(k), **v)
                newEntry += 1
                tsl = max(tsl, ts)

                if factionAttack:
                    self.attacks += 1
                else:
                    self.defends += 1

        self.last = tsl

        print("{} last  {}".format(self, timestampToDate(self.last)))
        print("{} progress ({})%".format(self, self.progress()))

        if not newEntry and len(apiAttacks) > 1:
            print("{} no new entry with cache = {} (continue)".format(self, cache))
            self.state = -6
            self.save()
            return -6

        if len(apiAttacks) < 2 and not self.live:
            print("{} no api entry for non live chain (stop)".format(self))
            self.computing = False
            self.crontab = 0
            self.state = 1
            self.last = self.end
            self.save()
            return 1

        if len(apiAttacks) < 2 and self.live:
            print("{} no api entry for live chain (continue)".format(self))
            self.state = 2
            self.end = self.last
            self.save()
            return 2

        self.state = 3
        self.save()
        return 3


class AttackReport(models.Model):
    report = models.ForeignKey(AttacksReport, on_delete=models.CASCADE)

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
