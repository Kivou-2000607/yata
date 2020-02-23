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
from django.utils.html import format_html

import json
import requests
import re

from yata.handy import *
from player.models import Key
from player.models import Player
from faction.functions import *

BONUS_HITS = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000]
CHAIN_ATTACKS_STATUS = {
    6: "No new entry with cooldown [stop]",
    4: "Should have reached the end [continue]",
    3: "Normal [continue]",
    2: "Reached end of chain [stop]",
    1: "No new attack [stop]",
    0: "Waiting for first call",
    -1: "No enabled AA keys [stop]",
    -2: "API key major error (key deleted) [continue]",
    -3: "API key temporary error [continue]",
    -4: "Probably cached response [continue]",
    -5: "Empty payload [stop]",
    -6: "No new entry without cooldown [stop]",
    -7: "No new entry (looked 1h after end) [stop]"}

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
    -7: "Run for more than a week [stop]"}

REPORT_REVIVES_STATUS = {
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
    -7: "Run for more than a week [stop]"}

BB_BRIDGE = {
    "criminaloffences": "Offences",
    "busts": "Busts",
    "jails": "Jail sentences",
    "drugsused": "Drugs taken",
    "drugoverdoses": "Overdoses",
    "gymstrength": "Energy on strength",
    "gymspeed": "Energy on speed",
    "gymdefense": "Energy on defense",
    "gymdexterity": "Energy on dexterity",
    "traveltime": "Hours of flight",
    "hunting": "Hunts",
    "rehabs": "Rehabs",
    "caymaninterest": "Interest in Cayman",
    "medicalcooldownused": "Medical cooldown",
    "revives": "Revives",
    "medicalitemrecovery": "Life recovered",
    "hosptimereceived": "Hospital received",
    "candyused": "Candy used",
    "alcoholused": "Alcohol used",
    "energydrinkused": "Energy drinks used",
    "hosptimegiven": "Hospital given",
    "attacksdamagehits": "Damaging hits",
    "attacksdamage": "Damage dealt",
    "attacksdamaging": "Damage received",
    "attacksrunaway": "Runaways",
    "allgyms": "Energy all stats"}


# Faction
class Faction(models.Model):
    # direct torn values
    tId = models.IntegerField(default=0, unique=True)
    name = models.CharField(default="MyFaction", max_length=64)
    respect = models.IntegerField(default=0)
    maxmembers = models.IntegerField(default=0)
    daysold = models.IntegerField(default=0)

    # keys
    masterKeys = models.ManyToManyField(Key, blank=True)
    nKeys = models.IntegerField(default=0)

    # chain and attacks
    hitsThreshold = models.IntegerField(default=100)
    lastAttacksPulled = models.IntegerField(default=0)
    lastRevivesPulled = models.IntegerField(default=0)
    chainsUpda = models.IntegerField(default=0)

    # poster
    poster = models.BooleanField(default=False)
    posterHold = models.BooleanField(default=False)
    posterOpt = models.TextField(default="{}")

    # respect simulator: TODO
    upgradesUpda = models.IntegerField(default=0)

    # members
    membersUpda = models.IntegerField(default=0)
    memberStatus = models.TextField(default="{}")  # dump all members status
    memberStatusUpda = models.IntegerField(default=0)

    # armory / networth
    armoryUpda = models.IntegerField(default=0)
    # armoryOld = models.IntegerField(default=8035200)

    # history options
    armoryHist = models.CharField(default="three_months", max_length=16)
    chainsHist = models.CharField(default="one_year", max_length=16)
    attacksHist = models.CharField(default="three_months", max_length=16)
    revivesHist = models.CharField(default="three_months", max_length=16)
    liveLength = models.CharField(default="one_week", max_length=16)

    # discord
    discordName = models.CharField(default="", max_length=64, null=True, blank=True)

    def __str__(self):
        return format_html("{} [{}]".format(self.name, self.tId))

    def fullname(self):
        return format_html("{} [{}]".format(self.name, self.tId))

    def getHist(self, key):
        if key == "armory":
            return HISTORY_TIMES.get(self.armoryHist, 3600)
        elif key == "chains":
            return HISTORY_TIMES.get(self.chainsHist, 3600)
        elif key == "attacks":
            return HISTORY_TIMES.get(self.attacksHist, 3600)
        elif key == "revives":
            return HISTORY_TIMES.get(self.revivesHist, 3600)
        elif key == "live":
            return HISTORY_TIMES.get(self.liveLength, 3600)
        else:
            return 3600

    def getHistName(self, key):
        if key == "armory":
            timeKey = self.armoryHist
        elif key == "chains":
            timeKey = self.chainsHist
        elif key == "attacks":
            timeKey = self.attacksHist
        elif key == "revives":
            timeKey = self.revivesHist
        elif key == "live":
            timeKey = self.liveLength
        else:
            timeKey = "one_hour"

        return " ".join([k for k in timeKey.split("_")])

    def cleanHistory(self):
        # clean chains
        old = tsnow() - self.getHist("chains")
        print(self.chain_set.filter(start__lt=old).delete())
        # clean attacks reports
        old = tsnow() - self.getHist("attacks")
        print(self.attacksreport_set.filter(start__lt=old).delete())
        # clean revives reports
        old = tsnow() - self.getHist("revives")
        print(self.revivesreport_set.filter(start__lt=old).delete())
        # clean news
        old = tsnow() - self.getHist("armory")
        print(self.news_set.filter(timestamp__lt=old).delete())
        print(self.log_set.filter(timestamp__lt=old).delete())

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

    def checkKeys(self):
        masterKeys = self.masterKeys.all()

        for key in masterKeys:
            # check currency for AA perm (smallest payload and give )
            req = apiCall("faction", "", "currency", key.value, verbose=False)

            if 'apiError' in req:
                code = req['apiErrorCode']
                if code in [1, 2, 10]:
                    # delete key
                    print("{} delete {} (API error {})".format(self, key, code))
                    key.delete()
                elif code in [7]:
                    # remove key
                    print("{} remove {} (API error {})".format(self, key, code))
                    self.masterKeys.remove(key)

            elif req['faction_id'] != self.tId:
                # remove key
                print("{} remove {} (changed faction)".format(self, key))
                self.masterKeys.remove(key)

            key.lastPulled = tsnow()
            key.reason = "Check AA perm"
            key.save()

        self.nKeys = len(self.getKeys())
        self.save()

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
                memberTmp.faction = self
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
                    shareN=-1 if player is None else 0)
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

    def updateLog(self):

        # get key
        key = self.getKey()
        if key is None:
            msg = "{} no key to update news".format(self)
            self.nKey = 0
            self.save()
            return False, "No keys to update the armory."

        # api call
        selection = 'armorynewsfull,fundsnewsfull,stats,donations,currency,basic,timestamp'
        factionInfo = apiCall('faction', self.tId, selection, key.value, verbose=False)
        if 'apiError' in factionInfo:
            msg = "Update news ({})".format(factionInfo["apiErrorString"])
            if factionInfo['apiErrorCode'] in [1, 2, 7, 10]:
                print("{} {} (remove key)".format(self, msg))
                self.delKey(key=key)
            else:
                key.reason = msg
                key.lastPulled = factionInfo.get("timestamp", 0)
                key.save()
                print("{} {}".format(self, msg))
            return False, "API error {}, armory not updated.".format(factionInfo["apiErrorString"])

        now = factionInfo.get("timestamp", 0)

        # update key
        key.reason = "Update armory"
        key.lastPulled = now
        key.save()

        # update faction
        self.maxmembers = max(self.maxmembers, len(factionInfo["members"]))
        self.daysold = factionInfo["age"]
        self.respect = factionInfo["respect"]

        # create/delete news
        old = now - self.getHist("armory")
        news = self.news_set.all()
        news.filter(timestamp__lt=old).delete()
        for type in ["armorynews", "fundsnews"]:
            for k, v in factionInfo.get(type, dict({})).items():
                newstype = news.filter(type=type)
                if v["timestamp"] > old:
                    v["news"] = cleanhtml(v["news"])[:512]
                    self.news_set.get_or_create(tId=k, type=type, defaults=v)

        # delete old logs
        self.log_set.filter(timestamp__lt=old).delete()

        # add daily log
        day = now - now % (3600 * 24)
        logdict = factionInfo.get("stats", dict({}))
        donationsmoney = 0
        donationspoints = 0
        for k, v in factionInfo.get("donations", dict({})).items():
            donationspoints += v["points_balance"]
            donationsmoney += v["money_balance"]
            logdict["donationsmoney"] = donationsmoney
            logdict["donationspoints"] = donationspoints
            logdict["respect"] = factionInfo.get("respect", 0)
            logdict["money"] = factionInfo.get("money", 0)
            logdict["points"] = factionInfo.get("points", 0)
        logdict["timestamp"] = now

        log = self.log_set.update_or_create(timestampday=day, defaults=logdict)

        # update faction
        self.armoryUpda = now
        self.save()
        return True, "Armory updated"

    def addContribution(self, stat):

        # get key
        key = self.getKey()
        if key is None:
            msg = "{} no key to update news".format(self)
            self.nKey = 0
            self.save()
            return False, "No keys to add contribution."

        # api call
        selection = 'basic,contributors&stat={}'.format(stat)
        contributors = apiCall('faction', self.tId, selection, key.value, verbose=False)
        if 'apiError' in contributors:
            msg = "Add contribution {} ({})".format(stat, contributors["apiErrorString"])
            if contributors['apiErrorCode'] in [1, 2, 7, 10]:
                print("{} {} (remove key)".format(self, msg))
                self.delKey(key=key)
            else:
                key.reason = msg
                key.lastPulled = contributors.get("timestamp", 0)
                key.save()
                print("{} {}".format(self, msg))
            return False, "API error {}, contribution not added.".format(contributors["apiErrorString"])

        # update key
        key.reason = "Update Big Brother"
        key.lastPulled = tsnow()
        key.save()

        mem = contributors["members"]
        if stat in contributors["contributors"]:
            con = contributors["contributors"][stat]
            now = tsnow()
            hour = now - now % (3600 // 4)
            c = dict({})
            for k, v in {k: v for k, v in con.items() if v["in_faction"]}.items():
                c[k] = [mem.get(k, dict({"name": "Player"})).get("name"), v["contributed"]]

            contrdict = {"timestamp": now, "contributors": json.dumps(c, separators=(',', ':'))}

            if self.contributors_set.filter(stat=stat).filter(timestamphour=hour).filter(stat=stat).first() is None:
                mod = "added"
            else:
                mod = "updated"
            self.contributors_set.update_or_create(timestamphour=hour, stat=stat, defaults=contrdict)

            return True, "{} contributors {}".format(BB_BRIDGE.get(stat, "?"), mod)

        else:
            print("{} not in API... that's weird".format(stat))
            return False, "{} not in API... that's weird".format(stat)

    def updateUpgrades(self):

        # get key
        key = self.getKey()
        if key is None:
            msg = "{} no key to update news".format(self)
            self.nKey = 0
            self.save()
            return False, "No keys to update faction upgrades"

        # api call
        upgrades = apiCall('faction', self.tId, "upgrades", key.value, verbose=False, sub="upgrades")
        if 'apiError' in upgrades:
            msg = "Update faction upgrades ({})".format(upgrades["apiErrorString"])
            if upgrades['apiErrorCode'] in [1, 2, 7, 10]:
                print("{} {} (remove key)".format(self, msg))
                self.delKey(key=key)
            else:
                key.reason = msg
                key.lastPulled = upgrades.get("timestamp", 0)
                key.save()
                print("{} {}".format(self, msg))
            return False, "API error {}, faction upgrades not updated".format(upgrades["apiErrorString"])

        # update key
        key.reason = "Update faction upgrades"
        key.lastPulled = tsnow()
        key.save()

        # deactivate all upgrades
        self.upgrade_set.filter(simu=False).update(active=False, level=1, unlocked="")

        # add upgrades
        for k, v in upgrades.items():
            for _ in ["ability", "basecost", "branch", "name"]:
                del v[_]
            v["active"] = True
            t = FactionTree.objects.filter(tId=k, level=v["level"]).first()
            v["shortname"] = t.shortname
            v["branch"] = t.branch
            self.upgrade_set.update_or_create(tId=k, simu=False, defaults=v)

        self.upgradesUpda = tsnow()
        self.save()
        return True, "Faction upgrades updated"

    def resetSimuUpgrades(self, update=False):
        if update:
            self.updateUpgrades()

        # deactivate all simu
        self.upgrade_set.filter(simu=True).update(active=False, level=1)

        # set all current
        for u in self.upgrade_set.filter(simu=False, active=True):
            v = dict({})
            v["branch"] = u.branch
            v["branchorder"] = u.branchorder
            v["branchmultiplier"] = u.branchmultiplier
            v["unlocked"] = ""
            v["shortname"] = u.shortname
            v["active"] = True
            v["level"] = u.level
            self.upgrade_set.update_or_create(tId=u.tId, simu=True, defaults=v)

    def getBranchesCosts(self, simu=True):
        allUpgrades = FactionTree.objects.all().order_by("tId", "-level")
        branchCost = dict({})
        for upgrade in self.upgrade_set.filter(simu=simu, active=True):
            branch = upgrade.getTree().branch
            if branch not in branchCost:
                branchCost[branch] = 0

            for u in allUpgrades.filter(shortname=upgrade.shortname, level__lte=upgrade.level):
                branchCost[branch] += u.base_cost

        return branchCost

    def setSimuDependencies(self, upgrade, unset=False):
        # change branch level if the modification of the subbranch requires it
        # lvl: level reuired
        # {sb: [[b1, lvl1], [b2, lvl2]]}
        r = {
            # Toleration
            27: [[29, 1]],  # side effect
            28: [[29, 13]],  # overdosing

            # Criminality
            13: [[14, 2]],  # nerve
            15: [[14, 2]],  # jail time
            17: [[14, 2], [15, 10]],  # bust skill
            16: [[14, 2], [15, 10], [17, 10]],  # bust nerve

            # Excrusion
            34: [[33, 2]],  # travel cost
            31: [[33, 3]],  # hunting
            35: [[33, 8]],  # rehab
            32: [[33, 9]],  # oversea banking

            # Supression
            45: [[46, 3]],  # maximum life
            48: [[47, 7]],  # escape

            # Agression
            44: [[43, 10]],  # accuracy
            40: [[42, 3]],  # hospitalization
            41: [[42, 15]],  # damage

            # Fortitude
            18: [[20, 2]],  # medical cooldown
            19: [[20, 13]],  # reviving
            21: [[20, 4]],  # life regeneration
            22: [[20, 4], [21, 5]],  # medical effectiveness

            # Voracity
            23: [[25, 2]],  # candy effect
            24: [[25, 15]],  # energy drink effect
            26: [[25, 9]],  # alcohol effect

            # Core
            10: [[11, 2]],  # chaining
            12: [[11, 2]]}  # territory

        for tId, lvl in [(b[0], b[1]) for b in r.get(upgrade.tId, [])]:
            u = FactionTree.objects.filter(tId=tId).first()
            v = {"active": True, "shortname": u.shortname, "branch": u.branch}
            up, _ = self.upgrade_set.update_or_create(simu=True, tId=u.tId, defaults=v)
            up.level = max(lvl, up.level)
            up.save()

        # change subbranch level to zero if the modification of the branch requires it
        # sb: sub branch
        # b: b branch
        # {b: [[sb1, lvl1], [sb2, lvl2]]}
        r = {
            # Toleration
            29: [[27, 1], [28, 13]],  # addiction

            # Criminality
            17: [[16, 10]],  # bust skill
            15: [[17, 10], [16, 10]],  # jail time
            14: [[15, 2], [13, 2], [17, 2], [16, 2]],  # crimes

            # Excrusion
            33: [[34, 2], [31, 3], [35, 8], [32, 9]],  # travel capacity

            # Supression
            46: [[45, 3]],  # defense
            47: [[48, 7]],  # dexterity

            # Agression
            43: [[44, 10]],  # speed
            42: [[40, 3], [41, 15]],  # strength

            # Fortitude
            20: [[18, 2], [21, 4], [22, 4], [19, 13]],   # hospitalization time
            21: [[22, 5]],   # life regeneration

            # Voracity
            25: [[23, 2], [24, 15], [26, 9]],  # booster cooldown

            # Core
            11: [[10, 2], [12, 2]]}  # capacity

        for tId, lvl in [(b[0], b[1]) for b in r.get(upgrade.tId, []) if b[1] > upgrade.level]:
            u = FactionTree.objects.filter(tId=tId).first()
            v = {"level": 1, "active": False, "shortname": u.shortname, "branch": u.branch}
            self.upgrade_set.update_or_create(simu=True, tId=u.tId, defaults=v)

        # special case for steadfast
        r = {
            37: [36, 38, 39],  # speed training
            36: [37, 38, 39],  # strength training
            38: [39, 36, 37],  # defense training
            39: [38, 36, 37]}  # dexterity training

        if r.get(upgrade.tId, False):
            # max the close branch to 10
            if upgrade.level > 10:
                u = FactionTree.objects.filter(tId=r.get(upgrade.tId)[0]).first()
                v = {"shortname": u.shortname, "branch": u.branch}
                up, _ = self.upgrade_set.update_or_create(simu=True, tId=u.tId, defaults=v)
                up.level = min(10, up.level)
                up.save()

            if upgrade.level > 15:
                u = FactionTree.objects.filter(tId=r.get(upgrade.tId)[1]).first()
                v = {"shortname": u.shortname, "branch": u.branch}
                up, _ = self.upgrade_set.update_or_create(simu=True, tId=u.tId, defaults=v)
                up.level = min(15, up.level)
                up.save()
                u = FactionTree.objects.filter(tId=r.get(upgrade.tId)[2]).first()
                v = {"shortname": u.shortname, "branch": u.branch}
                up, _ = self.upgrade_set.update_or_create(simu=True, tId=u.tId, defaults=v)
                up.level = min(15, up.level)
                up.save()

        # special case for core
        r = {
            1: [],  # weapon armory
            2: [1],  # armor armory
            3: [1, 2],  # tempory armory
            4: [1, 2],  # medical armory
            5: [1, 2, 3],  # booster armory
            6: [1, 2, 4],  # drug armory
            7: [1, 2, 3, 4, 5, 6],  # point storage
            8: [1, 2, 3, 4, 5, 6, 7]}  # laboratory

        if r.get(upgrade.tId) is not None:
            if unset:
                for u in [FactionTree.objects.filter(tId=i).first() for i, v in r.items() if upgrade.tId in v]:
                    v = {"shortname": u.shortname, "branch": u.branch, "level": 1, "active": False}
                    self.upgrade_set.update_or_create(simu=True, tId=u.tId, defaults=v)
            else:
                for u in [FactionTree.objects.filter(tId=i).first() for i in r.get(upgrade.tId)]:
                    v = {"shortname": u.shortname, "branch": u.branch, "active": True}
                    self.upgrade_set.update_or_create(simu=True, tId=u.tId, defaults=v)

        # set branch order
        for k, v in self.optimizedSimu().items():
            self.upgrade_set.filter(simu=True, branch=k).update(branchorder=v)

    def optimizedSimu(self, forceOrder=False):
        branchCost = self.getBranchesCosts(simu=True)

        order = 1
        orders = dict({})
        for k, v in sorted(branchCost.items(), key=lambda x: -x[1]):
            if k == 'Core':
                orders[k] = 0
            else:
                orders[k] = order
                order += 1

        if not forceOrder:
            return orders

        fb = forceOrder[0]  # branch name to force
        fo = forceOrder[1]  # branch order to force
        for k, v in orders.items():
            if k == fb:  # change order of the branch
                orders[k] = fo
            elif v <= fo:  # decrease by 1 the value of the branch if below or equal force
                orders[k] = max(orders[k] - 1, 0)  # to handle core = 0
            # elif v > fo:  # increase by 1 the value of the branch if above force
            #     orders[k] += 1

        return orders

    def getFactionTree(self, optimize=True, forceOrder=False):
        allUpgrades = FactionTree.objects.all().order_by("tId", "-level")
        facUpgrades = self.upgrade_set.filter(simu=False, active=True)
        simUpgrades = self.upgrade_set.filter(simu=True, active=True)

        if optimize:
            simuOrders = self.optimizedSimu(forceOrder=forceOrder)
        else:
            simuOrders = dict({})

        tree = dict({})
        maxorder = dict({})
        for u in allUpgrades:
            if u.branch not in tree:
                tree[u.branch] = dict({})
                maxorder[u.branch] = [0, 0]

            if u.shortname not in tree[u.branch]:
                tree[u.branch][u.shortname] = dict({})
                faction_order = 0
                faction_level = 0
                faction_cost = 0
                faction_base = 0
                simu_order = 0
                simu_level = 0
                simu_cost = 0
                simu_base = 0
                unsets_completed = 0

            # add faction
            fu = facUpgrades.filter(tId=u.tId, level=u.level).first()
            if fu is not None:
                faction_order = max(fu.branchorder, faction_order)
                faction_level = max(fu.level, faction_level)
                if fu.unsets_completed:
                    unsets_completed = fu.unsets_completed
            if u.branch == 'Core' and faction_level:
                faction_cost += u.base_cost
                faction_base += u.base_cost
            if faction_order:
                faction_cost += 2**(faction_order - 1) * (u.base_cost)
                faction_base += u.base_cost
            tree[u.branch][u.shortname]["faction_order"] = faction_order
            tree[u.branch][u.shortname]["faction_level"] = faction_level
            tree[u.branch][u.shortname]["faction_cost"] = faction_cost
            tree[u.branch][u.shortname]["faction_base"] = faction_base
            tree[u.branch][u.shortname]["unsets_completed"] = unsets_completed
            tree[u.branch][u.shortname]["id"] = u.tId

            maxorder[u.branch][0] = max(maxorder[u.branch][0], faction_order)

            # add simu
            fu = simUpgrades.filter(tId=u.tId, level=u.level).first()
            if fu is not None:
                simu_order = max(fu.branchorder, simu_order) if not optimize else simuOrders.get(u.branch, -1)
                simu_level = max(fu.level, simu_level)
            if u.branch == 'Core' and simu_level:
                simu_cost += u.base_cost
                simu_base += u.base_cost
            if simu_order:
                simu_cost += 2**(simu_order - 1) * (u.base_cost)
                simu_base += u.base_cost
            tree[u.branch][u.shortname]["simu_order"] = simu_order
            tree[u.branch][u.shortname]["simu_level"] = simu_level
            tree[u.branch][u.shortname]["simu_cost"] = simu_cost
            tree[u.branch][u.shortname]["simu_base"] = simu_base
            maxorder[u.branch][1] = max(maxorder[u.branch][1], simu_order)
            tree[u.branch][u.shortname]["level_list"] = range(u.maxlevel + 1)

            #
            # respect[u.branch]["simu"] += simu_cost
            # respect["Total"]["simu"] += simu_cost
            # if u.branch == 'Core':
            #     print(u, respect[u.branch]["faction"] )

        respect = dict({"Total": dict({"simu_cost": 0, "faction_cost": 0})})

        for k1, v1 in tree.items():
            respect[k1] = dict({"simu_cost": 0, "faction_cost": 0,
                                "simu_base": 0, "faction_base": 0,
                                "simu_order": 0, "faction_order": 0})
            for k2, v2 in v1.items():
                v2["faction_order"] = maxorder[k1][0]
                v2["simu_order"] = maxorder[k1][1]

                respect[k1]["simu_cost"] += v2["simu_cost"]
                respect[k1]["faction_cost"] += v2["faction_cost"]
                respect[k1]["simu_base"] += v2["simu_base"]
                respect[k1]["faction_base"] += v2["faction_base"]
                respect[k1]["simu_order"] = v2["simu_order"]
                respect[k1]["faction_order"] = v2["faction_order"]

            respect["Total"]["simu_cost"] += respect[k1]["simu_cost"]
            respect["Total"]["faction_cost"] += respect[k1]["faction_cost"]

        return tree, respect


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
    state = models.CharField(default="", max_length=64, blank=True)
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
        return format_html("{} [{}]".format(self.name, self.tId))

    def updateStatus(self, description=None, details=None, state=None, color=None, until=None, save=False, **args):
        # the **args is here to hade extra keys not needed
        if description is not None:
            splt = description.split("data-time=")
            if len(splt) > 1:
                try:
                    ts = int(splt[1].split(">")[0])
                    description = "{} {:.1f} minutes".format(cleanhtml(description), ts / 60)
                except BaseException as e:
                    print(e)
                    description = "{} ?? minutes".format(cleanhtml(description))
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
    current = models.IntegerField(default=0)  # only modified in getAttacks
    attacks = models.IntegerField(default=0)  # only modified in fillReport
    graphs = models.TextField(default="{}", null=True, blank=True)
    cooldown = models.BooleanField(default=False)

    # blameched variables
    addToEnd = models.IntegerField(default=0)  # add seconds to end timestamp if chain didn't reach last hit

    # for the combined report
    combine = models.BooleanField(default=False)

    def __str__(self):
        return format_html("{} chain [{}]".format(self.faction, self.tId))

    def cdTime(self):
        return "{:.1f} mins".format(self.chain / 6. if self.cooldown else 0)

    def elapsed(self):
        last = "{:.1f} days".format((self.last - self.start) / (60 * 60 * 24)) if self.last else "-"
        end = "{:.1f} days".format((self.end - self.start) / (60 * 60 * 24)) if self.end else "-"
        return "{} / {}".format(last, end)

    def assignCrontab(self):
        # check if already in a crontab
        chain = self.faction.chain_set.filter(computing=True).only("crontab").first()
        if chain is None or chain.crontab not in getCrontabs():
            cn = {c: len(Chain.objects.filter(crontab=c).only('crontab')) for c in getCrontabs()}
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

        print("{} live    {}".format(self, self.live))
        print("{} start   {}".format(self, timestampToDate(tss)))
        print("{} last    {}".format(self, timestampToDate(tsl)))
        print("{} end     {}".format(self, timestampToDate(tse)))
        if self.cooldown:
            tse += self.chain * 10
            print("{} with cd {}".format(self, timestampToDate(tse)))
        else:
            self.current = min(self.current, self.chain)

        # add + 2 s to the endTS
        tse += self.addToEnd

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
            respect = float(v["respect_gain"]) > 0
            # chainAttack = int(v["chain"])
            # if newAttack and factionAttack:
            if newAttack and factionAttack:
                v = modifiers2lvl1(v)
                self.attackchain_set.get_or_create(tId=int(k), defaults=v)
                newEntry += 1
                tsl = max(tsl, ts)
                if int(v["timestamp_ended"]) - self.end < 0:  # case we're before cooldown
                    self.current = max(self.current, v["chain"])
                elif self.cooldown and respect:  # case we're after cooldown and we want cooldown
                    self.current += 1

                # print("{} attack [{}] current {}".format(self, k, current))

        self.last = tsl

        print("{} last  {}".format(self, timestampToDate(self.last)))
        print("{} new entries {}".format(self, newEntry))
        print("{} progress {} / {} ({})%".format(self, self.current, self.chain, self.progress()))

        if self.live:
            if req["chain"]["current"] < 10:
                print("{} reached end of live chain (stop)".format(self))
                self.computing = False
                self.crontab = 0
                self.state = 2
                self.save()
                return 2

        else:

            if self.current == self.chain and not self.cooldown:
                print("{} Reached end of chain (stop)".format(self))
                self.computing = False
                self.crontab = 0
                self.state = 2
                self.save()
                return 2

            if len(apiAttacks) < 2:
                if self.cooldown:
                    print("{} no api entry for non live report cooldown (stop)".format(self))
                    self.computing = False
                    self.crontab = 0
                    self.state = 1
                    self.save()
                    return 1

                elif self.addToEnd > 3600:
                    # add 10 seconds
                    print("{} didn't find last attack even looking after 1 hour (stop)".format(self))
                    self.computing = False
                    self.crontab = 0
                    self.state = -7
                    self.save()
                    return -7

                # add 10 seconds
                print("{} no api entry for non live report no cooldown (continue)".format(self))
                self.addToEnd += 10
                self.state = 4
                self.save()
                return 4

            if not newEntry and len(apiAttacks) > 1:
                print("{} no new entry from payload (stop)".format(self))
                self.computing = False
                self.crontab = 0
                self.state = 6 if self.cooldown else -6
                self.save()
                return 6 if self.cooldown else -6

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
                # if att.chain:
                if att.respect_gain > 0.0:
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
        # print("progress", float((100 * self.current) / float(max(1, self.chain))))
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
        return format_html("Count for {}".format(self.chain))


class Bonus(models.Model):
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE)
    tId = models.IntegerField(default=0)
    name = models.CharField(default="Duke", max_length=15)
    hit = models.IntegerField(default=0)
    respect = models.FloatField(default=0)
    targetId = models.IntegerField(default=0)
    targetName = models.CharField(default="Unkown", max_length=15)

    def __str__(self):
        return format_html("Bonus for {}".format(self.chain))


class AttackChain(models.Model):
    report = models.ForeignKey(Chain, on_delete=models.CASCADE)

    # API Fields
    tId = models.IntegerField(default=0)
    timestamp_started = models.IntegerField(default=0)
    timestamp_ended = models.IntegerField(default=0)
    attacker_id = models.IntegerField(default=0)
    attacker_name = models.CharField(default="attacker_name", max_length=16, null=True, blank=True)
    attacker_faction = models.IntegerField(default=0)
    attacker_factionname = models.CharField(default="attacker_factionname", max_length=64, null=True, blank=True)
    defender_id = models.IntegerField(default=0)
    defender_name = models.CharField(default="defender_name", max_length=16, null=True, blank=True)
    defender_faction = models.IntegerField(default=0)
    defender_factionname = models.CharField(default="defender_factionname", max_length=64, null=True, blank=True)
    result = models.CharField(default="result", max_length=64)
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
        return format_html("Attack for chain [{}]".format(self.tId))


# Walls
class Wall(models.Model):
    tId = models.IntegerField(default=0)
    tss = models.IntegerField(default=0)
    tse = models.IntegerField(default=0)
    attackers = models.TextField(default="{}", null=True, blank=True)
    defenders = models.TextField(default="{}", null=True, blank=True)
    attackerFactionId = models.IntegerField(default=0)
    attackerFactionName = models.CharField(default="AttackFaction", max_length=64)
    defenderFactionId = models.IntegerField(default=0)
    defenderFactionName = models.CharField(default="DefendFaction", max_length=64)
    territory = models.CharField(default="AAA", max_length=3)
    result = models.CharField(default="Unset", max_length=10)
    factions = models.ManyToManyField(Faction, blank=True)
    # array of the two faction ID. Toggle wall for a faction adds/removes the ID to this array
    breakdown = models.TextField(default="[]", null=True, blank=True)
    # temporary bool only here to pass breakdown of the faction to template
    breakSingleFaction = models.BooleanField(default=False)

    def __str__(self):
        return format_html("Wall [{}]".format(self.tId))

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
        return format_html("{} report [{}]".format(self.faction, self.pk))

    def elapsed(self):
        last = "{:.1f} days".format((self.last - self.start) / (60 * 60 * 24)) if self.last else "-"
        end = "{:.1f} days".format((self.end - self.start) / (60 * 60 * 24)) if self.end else "-"
        return "{} / {}".format(last, end)

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
        if report is None or report.crontab not in getCrontabs():
            cn = {c: len(AttacksReport.objects.filter(crontab=c).only('crontab')) for c in getCrontabs()}
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

        # check if not running for too long
        week = 60 * 60 * 24 * 7
        if self.last - self.start > week:
            weekAgo = tsnow() - week
            self.computing = False
            self.crontab = 0
            self.attackreport_set.filter(timestamp_ended__gt=weekAgo).delete()
            self.state = -7
            self.save()
            return -7

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

        # add attacks
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
    attacker_factionname = models.CharField(default="attacker_factionname", max_length=64, null=True, blank=True)
    defender_id = models.IntegerField(default=0)
    defender_name = models.CharField(default="defender_name", max_length=16, null=True, blank=True)
    defender_faction = models.IntegerField(default=0)
    defender_factionname = models.CharField(default="defender_factionname", max_length=64, null=True, blank=True)
    result = models.CharField(default="result", max_length=64)
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


# Revive report
class RevivesReport(models.Model):
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    last = models.IntegerField(default=0)
    live = models.BooleanField(default=True)

    # information for computing
    computing = models.BooleanField(default=True)
    state = models.IntegerField(default=0)
    crontab = models.IntegerField(default=0)
    update = models.IntegerField(default=0)

    # global information for the report
    reviverFactions = models.TextField(default="[]")
    targetFactions = models.TextField(default="[]")
    revivesMade = models.IntegerField(default=0)
    revivesReceived = models.IntegerField(default=0)

    def __str__(self):
        return format_html("{} revives [{}]".format(self.faction, self.pk))

    def elapsed(self):
        last = "{:.1f} days".format((self.last - self.start) / (60 * 60 * 24)) if self.last else "-"
        end = "{:.1f} days".format((self.end - self.start) / (60 * 60 * 24)) if self.end else "-"
        return "{} / {}".format(last, end)

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
        report = self.faction.revivesreport_set.filter(computing=True).only("crontab").first()
        if report is None or report.crontab not in getCrontabs():
            cn = {c: len(RevivesReport.objects.filter(crontab=c).only('crontab')) for c in getCrontabs()}
            self.crontab = sorted(cn.items(), key=lambda x: x[1])[0][0]
        elif report is not None:
            self.crontab = report.crontab
        self.save()
        return self.crontab

    def getRevives(self):
        """ Fill report with revives
        """
        # handle live report
        if self.live:
            self.end = tsnow()

        # shortcuts
        faction = self.faction
        tss = self.start
        tse = self.end

        # compute last ts
        lastRevive = self.revive_set.order_by("-timestamp").first()
        tsl = self.start if lastRevive is None else lastRevive.timestamp
        self.last = tsl

        print("{} live {}".format(self, self.live))
        print("{} start {}".format(self, timestampToDate(tss)))
        print("{} last  {}".format(self, timestampToDate(tsl)))
        print("{} end   {}".format(self, timestampToDate(tse)))

        # check if not running for too long
        week = 60 * 60 * 24 * 7
        if self.last - self.start > week:
            weekAgo = tsnow() - week
            self.computing = False
            self.crontab = 0
            self.revive_set.filter(timestamp__gt=weekAgo).delete()
            self.live = False
            self.state = -7
            self.save()
            return -7

        # add + 2 s to the endTS
        tse += 10

        # get existing revives (just the ids)
        revives = [r.tId for r in self.revive_set.all()]
        print("{} {} existing revives".format(self, len(revives)))

        # get key
        key = faction.getKey(useFact=True)
        if key is None:
            print("{} no key".format(self))
            self.computing = False
            self.crontab = 0
            self.revive_set.all().delete()
            self.state = -1
            self.save()
            return -1

        # prevent cache response
        delay = tsnow() - self.update
        delay = min(tsnow() - faction.lastRevivesPulled, delay)
        if delay < 32:
            sleeptime = 32 - delay
            print("{} last update {}s ago, waiting {} for cache...".format(self, delay, sleeptime))
            time.sleep(sleeptime)

        # make call
        selection = "revives,timestamp&from={}&to={}".format(tsl, tse)
        req = apiCall("faction", faction.tId, selection, key.value, verbose=False)
        key.reason = "Pull revives for report"
        key.lastPulled = tsnow()
        key.save()
        self.update = tsnow()
        faction.lastRevivesPulled = self.update
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

        apiRevives = req["revives"]

        # in case empty payload
        if not len(apiRevives):
            print('{} empty payload'.format(self))
            self.computing = False
            self.crontab = 0
            self.state = -5
            self.save()
            return -5

        print("{} {} revives from the API".format(self, len(apiRevives)))

        # add attacks
        newEntry = 0
        for k, v in apiRevives.items():
            ts = int(v["timestamp"])

            # probably because of cache
            before = int(v["timestamp"]) - self.last
            after = int(v["timestamp"]) - tse
            if before < 0 or after > 0:
                print("{} /!\ ts out of bound: before = {} after = {}".format(self, before, after))

            a = self.revive_set.update_or_create(tId=int(k), defaults=v)
            newEntry += 1
            tsl = max(tsl, ts)
            if v["reviver_faction"] == faction.tId:
                self.revivesMade += 1
            else:
                self.revivesReceived += 1

        self.last = tsl

        print("{} last  {}".format(self, timestampToDate(self.last)))
        print("{} progress ({})%".format(self, self.progress()))

        if not newEntry and len(apiRevives) > 1:
            print("{} no new entry with cache = {} (continue)".format(self, cache))
            self.state = -6
            self.save()
            return -6

        if len(apiRevives) < 2 and not self.live:
            print("{} no api entry for non live chain (stop)".format(self))
            self.computing = False
            self.crontab = 0
            self.state = 1
            self.last = self.end
            self.save()
            return 1

        if len(apiRevives) < 2 and self.live:
            print("{} no api entry for live chain (continue)".format(self))
            self.state = 2
            self.end = self.last
            self.save()
            return 2

        self.state = 3
        self.save()
        return 3


class Revive(models.Model):
    report = models.ForeignKey(RevivesReport, on_delete=models.CASCADE)
    tId = models.IntegerField(default=0)
    timestamp = models.IntegerField(default=0)
    reviver_id = models.IntegerField(default=0)
    reviver_name = models.CharField(default="reviver_name", max_length=32)
    reviver_faction = models.IntegerField(default=0)
    reviver_factionname = models.CharField(default="reviver_factionname", null=True, blank=True, max_length=64)
    target_id = models.IntegerField(default=0)
    target_name = models.CharField(default="target_name", max_length=32)
    target_faction = models.IntegerField(default=0)
    target_factionname = models.CharField(default="target_factionname", null=True, blank=True, max_length=64)


# Armory
class News(models.Model):
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    type = models.CharField(default="typenews", max_length=16)
    tId = models.IntegerField(default=0)
    timestamp = models.IntegerField(default=0)
    news = models.CharField(default="news", max_length=512)

    def __str__(self):
        return format_html("{} {} [{}]".format(self.faction, self.type, self.tId))


class Log(models.Model):
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    timestamp = models.IntegerField(default=0)
    timestampday = models.IntegerField(default=0)

    # armory
    money = models.BigIntegerField(default=0)
    donationsmoney = models.BigIntegerField(default=0)
    points = models.BigIntegerField(default=0)
    donationspoints = models.BigIntegerField(default=0)

    # respect
    respect = models.BigIntegerField(default=0)

    # stats
    medicalitemsused = models.BigIntegerField(default=0)
    criminaloffences = models.BigIntegerField(default=0)
    organisedcrimerespect = models.BigIntegerField(default=0)
    organisedcrimemoney = models.BigIntegerField(default=0)
    organisedcrimesuccess = models.BigIntegerField(default=0)
    organisedcrimefail = models.BigIntegerField(default=0)
    attackswon = models.BigIntegerField(default=0)
    attackslost = models.BigIntegerField(default=0)
    attacksleave = models.BigIntegerField(default=0)
    attacksmug = models.BigIntegerField(default=0)
    attackshosp = models.BigIntegerField(default=0)
    bestchain = models.BigIntegerField(default=0)
    busts = models.BigIntegerField(default=0)
    revives = models.BigIntegerField(default=0)
    jails = models.BigIntegerField(default=0)
    hosps = models.BigIntegerField(default=0)
    medicalitemrecovery = models.BigIntegerField(default=0)
    medicalcooldownused = models.BigIntegerField(default=0)
    gymtrains = models.BigIntegerField(default=0)
    gymstrength = models.BigIntegerField(default=0)
    gymspeed = models.BigIntegerField(default=0)
    gymdefense = models.BigIntegerField(default=0)
    gymdexterity = models.BigIntegerField(default=0)
    candyused = models.BigIntegerField(default=0)
    alcoholused = models.BigIntegerField(default=0)
    energydrinkused = models.BigIntegerField(default=0)
    drugsused = models.BigIntegerField(default=0)
    drugoverdoses = models.BigIntegerField(default=0)
    rehabs = models.BigIntegerField(default=0)
    caymaninterest = models.BigIntegerField(default=0)
    traveltimes = models.BigIntegerField(default=0)
    traveltime = models.BigIntegerField(default=0)
    hunting = models.BigIntegerField(default=0)
    attacksdamagehits = models.BigIntegerField(default=0)
    attacksdamage = models.BigIntegerField(default=0)
    hosptimegiven = models.BigIntegerField(default=0)
    hosptimereceived = models.BigIntegerField(default=0)
    attacksdamaging = models.BigIntegerField(default=0)
    attacksrunaway = models.BigIntegerField(default=0)
    highestterritories = models.BigIntegerField(default=0)
    territoryrespect = models.BigIntegerField(default=0)

    def __str__(self):
        return "{} Log [{}]".format(self.faction, self.timestampday)


# Big brother
class Contributors(models.Model):
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    timestamp = models.IntegerField(default=0)
    timestamphour = models.IntegerField(default=0)

    stat = models.CharField(default="stat", max_length=64)
    contributors = models.TextField(default="{}")

    def __str__(self):
        return format_html("{} {} contributors".format(self.faction, self.stat))


# Territories
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


# Faction data
class FactionData(models.Model):
    territoryUpda = models.IntegerField(default=0)
    crontabs = models.TextField(default="[1,2,3]")
    # upgradeTree = models.TextField(default="{}", null=True, blank=True)

    def __str__(self):
        return "Faction data [{}]".format(self.pk)


class FactionTree(models.Model):
    # api
    tId = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    branch = models.CharField(default="branch", max_length=32)
    name = models.CharField(default="name", max_length=32)
    ability = models.CharField(default="ability", max_length=256)
    challenge = models.CharField(default="challenge", max_length=256)
    base_cost = models.IntegerField(default=0)

    # additions field
    shortname = models.CharField(default="name", max_length=32)
    maxlevel = models.IntegerField(default=0)

    def __str__(self):
        return "{} - {} [{}] level {}/{}".format(self.branch, self.shortname, self.tId, self.level, self.maxlevel)

    def progress(self, faction):
        # get last log
        log = faction.log_set.all().order_by("-timestamp").first()
        if log is None:
            print("no log")
            return -1, -1

        # return done, to be done
        if self.challenge == "No challenge":
            return -1, -1

        elif self.tId == 8:
            goal = int(self.challenge.split(" ")[1])
            curr = faction.maxmembers
            return curr, goal

        elif self.tId == 10:
            goal = int(self.challenge.split(" ")[-1])
            curr = log.bestchain
            return curr, goal

        elif self.tId == 11:
            goal = int(self.challenge.split(" ")[-2])
            curr = faction.daysold
            return curr, goal

        elif self.tId == 12:
            goal = int(self.ability.split(" ")[-2]) - 1
            curr = log.highestterritories
            return curr, goal

        elif self.tId == 13:
            goal = int(self.challenge.split(" ")[-2].replace(",", ""))
            curr = log.criminaloffences
            return curr, goal

        elif self.tId == 15:
            goal = int(self.challenge.split(" ")[1].replace(",", ""))
            curr = log.jails
            return curr, goal

        elif self.tId in [16, 17]:
            goal = int(self.challenge.split(" ")[1].replace(",", ""))
            curr = log.busts
            return curr, goal

        elif self.tId == 18:
            goal = int(self.challenge.split(" ")[1].replace(",", ""))
            curr = log.medicalcooldownused
            return curr, goal

        elif self.tId == 19:
            goal = int(self.challenge.split(" ")[1].replace(",", ""))
            curr = log.revives
            return curr, goal

        elif self.tId == 21:
            goal = int(self.challenge.split(" ")[1].replace(",", ""))
            curr = log.medicalitemrecovery
            return curr, goal

        elif self.tId == 22:
            goal = int(self.challenge.split(" ")[1].replace(",", ""))
            curr = log.hosptimereceived
            return curr, goal

        elif self.tId == 23:
            goal = int(self.challenge.split(" ")[1].replace(",", ""))
            curr = log.candyused
            return curr, goal

        elif self.tId == 24:
            goal = int(self.challenge.split(" ")[1].replace(",", ""))
            curr = log.energydrinkused
            return curr, goal

        elif self.tId == 26:
            goal = int(self.challenge.split(" ")[1].replace(",", ""))
            curr = log.alcoholused
            return curr, goal

        elif self.tId == 27:
            goal = int(self.challenge.split(" ")[1].replace(",", ""))
            curr = log.drugsused
            return curr, goal

        elif self.tId == 28:
            goal = int(self.challenge.split(" ")[1].replace(",", ""))
            curr = log.drugoverdoses
            return curr, goal

        elif self.tId == 31:
            goal = int(self.challenge.split(" ")[1].replace(",", ""))
            curr = log.hunting
            return curr, goal

        elif self.tId == 32:
            goal = int(self.challenge.split(" ")[1].replace(",", "").replace("$", ""))
            curr = log.caymaninterest
            return curr, goal

        elif self.tId == 34:
            goal = int(self.challenge.split(" ")[1].replace(",", ""))
            curr = log.traveltime
            return curr, goal

        elif self.tId == 35:
            goal = int(self.challenge.split(" ")[1].replace(",", ""))
            curr = log.rehabs
            return curr, goal

        elif self.tId == 36:
            goal = int(self.challenge.split(" ")[1].replace(",", ""))
            curr = log.gymstrength
            return curr, goal

        elif self.tId == 37:
            goal = int(self.challenge.split(" ")[1].replace(",", ""))
            curr = log.gymspeed
            return curr, goal

        elif self.tId == 38:
            goal = int(self.challenge.split(" ")[1].replace(",", ""))
            curr = log.gymdefense
            return curr, goal

        elif self.tId == 39:
            goal = int(self.challenge.split(" ")[1].replace(",", ""))
            curr = log.gymdexterity
            return curr, goal

        elif self.tId == 40:
            goal = int(self.challenge.split(" ")[-2].replace(",", ""))
            curr = log.hosptimegiven
            return curr, goal

        elif self.tId == 41:
            goal = int(self.challenge.split(" ")[1].replace(",", ""))
            curr = log.attacksdamage
            return curr, goal

        elif self.tId == 44:
            goal = int(self.challenge.split(" ")[1].replace(",", ""))
            curr = log.attacksdamagehits
            return curr, goal

        elif self.tId == 45:
            goal = int(self.challenge.split(" ")[1].replace(",", ""))
            curr = log.attacksdamaging
            return curr, goal

        elif self.tId == 48:
            goal = int(self.challenge.split(" ")[-2].replace(",", ""))
            curr = log.attacksrunaway
            return curr, goal

        else:
            return 6, 10


class Upgrade(models.Model):
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)

    tId = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    branchorder = models.IntegerField(default=0)
    branchmultiplier = models.IntegerField(default=0)
    unlocked = models.CharField(default="unlocked", max_length=32, null=True, blank=True)
    unsets_completed = models.IntegerField(default=0)

    # reserverd for simulation
    simu = models.BooleanField(default=False)

    # active or not (to avoid deleting changes)
    active = models.BooleanField(default=False)

    # to link with branch FactionTree
    shortname = models.CharField(default="name", max_length=32)
    branch = models.CharField(default="name", max_length=32)

    def __str__(self):
        return format_html("{} upgrade {} - {}".format(self.faction, self.tId, self.level))

    def getTree(self):
        return FactionTree.objects.filter(tId=self.tId, level=self.level).first()
