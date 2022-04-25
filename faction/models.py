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
from django.core.exceptions import MultipleObjectsReturned
from django.conf import settings
from django.core.paginator import Paginator
from django.core.cache import cache

from numpy.core.numeric import normalize_axis_tuple
from rest_framework import serializers
from yata.BulkManager2 import BulkManager

import json
import requests
import re
import random
import os
from decouple import config
import hashlib

from yata.handy import *
from yata.bulkManager import *
from player.models import Key
from player.models import Player
from bazaar.models import BazaarData
from faction.functions import *
from faction.storage import OverwriteStorage

BONUS_HITS = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000]
MINIMAL_API_ATTACKS_STOP = 10
FONT_DIR = os.path.join(settings.SRC_ROOT, 'fonts')


if settings.DEBUG:
    CACHE_RESPONSE = int(config('CACHE_RESPONSE', default=10, cast=int))
else:
    CACHE_RESPONSE = 10

CHAIN_ATTACKS_STATUS = {

    # cooldown
    52: "No new attacks [stop]",
    32: "No new entries [continue]",
    12: "Computing [continue]",

    # no cooldown
    51: "Reached end of chain [stop]",
    21: "Looking after end of chain [continue]",
    11: "Computing [continue]",

    # live
    50: "Reached end of chain [stop]",
    10: "Computing [continue]",

    # init
    1: "Waiting for first call",
    0: "No reports",

    # errors
    -1: "No enabled AA keys [stop]",
    -2: "API key major error (key deleted) [continue]",
    -3: "API key temporary error [continue]",
    -4: "Probably cached response [continue]",
    -5: "Empty payload [stop]",
    -6: "No new entry (looked 1h after end) [stop]"
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

REPORTS_STATUS = {
    # init
    0: "Waiting for first call [starting]",
    1: "Report computed [stop]",
    2: "Live report up to date [continue]",
    3: "Report being computed [continue]",

    # errors
    -1: "ERROR: No keys found [stop]",
    -2: "ERROR: Fatal API error on faction key (key deleted) [continue]",
    -3: "ERROR: API error on faction key [continue]",
    -4: "WARNING: Received cache from torn API [continue]",
    -5: "ERROR: Running for too long [stop]",
    -6: "ERROR: Server error [stop]"
}

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


def posterRenameHead(instance, filename):
    ext = filename.split('.')[-1]
    return f'posters/{instance.tId}-head.{ext}'


def posterRenameTail(instance, filename):
    ext = filename.split('.')[-1]
    return f'posters/{instance.tId}-tail.{ext}'


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
    posterImg = models.ImageField(blank=True)
    posterGymImg = models.ImageField(blank=True)
    posterHeadImg = models.ImageField(max_length=64, blank=True, upload_to=posterRenameHead, storage=OverwriteStorage())
    posterTailImg = models.ImageField(max_length=64, blank=True, upload_to=posterRenameTail, storage=OverwriteStorage())

    # respect simulator
    upgradesUpda = models.IntegerField(default=0)
    simulationTS = models.IntegerField(default=0)
    simulationID = models.IntegerField(default=0)

    # members
    membersUpda = models.IntegerField(default=0)

    # crimes
    crimesUpda = models.IntegerField(default=0)
    ph_pa_Dump = models.TextField(default="[]")
    crimesRank = models.TextField(default="[]")

    # history options
    crimesHist = models.CharField(default="one_month", max_length=16)
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
        elif key == "crimes":
            return HISTORY_TIMES.get(self.crimesHist, 3600)
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
        elif key == "crimes":
            timeKey = self.crimesHist
        else:
            timeKey = "one_hour"

        return " ".join([k for k in timeKey.split("_")])

    def getTargetsId(self):
        return [t.target_id for t in self.target_set.all()]

    def getWarsHistory(self):
        # api call and update key
        key = self.getKey()

        if key is None:
            return {}
        else:
            news = apiCall(
                "faction",
                self.tId,
                "mainnews",
                key=key.value,
                sub="mainnews",
                cache_response=3600,
                cache_private=False,
                verbose=True
            )

        if 'apiError' in news:
            return news

        wars = dict({})
        for v in news.values():

            if "rankreport&rankID=" in v["news"]:  # case ranked war
                war_type = "ranked"
                reg = r'rankreport&rankID=\d{1,10}|step=profile&ID=\d{1,10}'
            elif "warreport&warID=" in v["news"]:  # case territorial war
                war_type = "territorial"
                reg = r'warreport&warID=\d{1,10}|step=profile&ID=\d{1,10}'
            elif "raidreport&raidID=" in v["news"]:  # case raid war
                war_type = "raid"
                reg = r'raidreport&raidID=\d{1,10}|step=profile&ID=\d{1,10}'
            else:
                continue

            # get factions ID and war ID
            fac_a, fac_b, war_id = re.findall(reg, v["news"])
            fac_a = int(fac_a.split("=")[-1])
            fac_b = int(fac_b.split("=")[-1])
            war_id = int(war_id.split("=")[-1])

            # get other faction id
            us_first = 1 if fac_a == self.tId else 0
            other_fac_id = fac_b if us_first else fac_a

            if other_fac_id not in wars:
                if war_type == "ranked":
                    reg = fr'ID={other_fac_id}>(.*?)</a>'
                elif war_type == "territorial":
                    reg = fr'ID={other_fac_id}">(.*?)</a>'
                elif war_type == "raid":
                    reg = fr'ID={other_fac_id}">(.*?)</a>'

                name = re.findall(reg, v["news"])[0]
                wars[other_fac_id] = {
                    "name": name,
                    "n": 0,
                    "wars": []
                }

            # extra data (dump for js)
            extra = {}
            if war_type == "territorial":
                reg = r'terrName=(.*?)">'
                extra["territory"] = re.findall(reg, v["news"])[0]
                reg = fr'ID={other_fac_id}">(.*?)</a>'
                extra["other_fac_name"] = re.findall(reg, v["news"])[0]
            elif war_type == "raid":
                reg = fr'ID={other_fac_id}">(.*?)</a>'
                extra["other_fac_name"] = re.findall(reg, v["news"])[0]

            # try to get report
            report = self.attacksreport_set.filter(
                war_id=war_id,
                war_type=war_type
            ).first()
            wars[other_fac_id]["wars"].append({
                "type": war_type,
                "us_first": us_first,
                "war_id": war_id,
                "report": report,
                "other_fac_id": other_fac_id,
                "timestamp": v["timestamp"],
                **extra
            })
            wars[other_fac_id]["n"] += 1

        # print("get wars")
        # for k1, v1 in wars.items():
        #     print(f'{k1}')
        #     for k2, v2 in v1.items():
        #         print(f'\t{k2}: {v2}')

        return sorted(wars.items(), key=lambda x: -x[1]["n"])

    def updateCrimes(self, force=False):

        now = int(timezone.now().timestamp())
        old = now - self.getHist("crimes")
        # don't update if less than 1 hour ago and force is False
        if (not force and (now - self.crimesUpda) < 3600):
           return self.crimes_set.all(), False, False

        # api call and update key
        key = self.getKey()
        if key is None:
            msg = "{} no key to update news".format(self)
            self.nKey = 0
            self.save()
            return self.crimes_set.all(), True, "No keys to update faction upgrades"

        crimesAPI = apiCall("faction", "", "crimes", key=key.value, sub="crimes", verbose=False)
        if 'apiError' in crimesAPI:
            msg = f'Update faction upgrades ({crimesAPI["apiErrorString"]})'
            if crimesAPI['apiErrorCode'] in API_CODE_DELETE:
                print("{} {} (remove key)".format(self, msg))
                self.delKey(key=key)
                return self.crimes_set.all(), True, msg
            else:
                key.reason = msg
                key.lastPulled = crimesAPI.get("timestamp", 0)
                key.save()
                print("{} {}".format(self, msg))
            return self.crimes_set.all(), True, msg

        key.lastPulled = tsnow()
        key.reason = "Update crimes list"
        key.save()

        # get db crimes
        crimesDB = self.crimes_set.all()

        # information dictionnary for the output
        n = {"created": 0, "updated": 0, "deleted": 0, "ready": 0}

        # loop over db crimes to check for cancelled crimes (ie not in api)
        for crime in crimesDB.filter(initiated=False):
            if str(crime.tId) not in crimesAPI:
                n["deleted"] += 1
                crime.delete()

        # sort crimes API (from older to newer)
        crimesAPI = sorted(crimesAPI.items(), key=lambda x: (-x[1]["initiated"], x[1]["time_started"]))

        # create ranking based on sub ranking
        # sub_ranking = [[int(list(p.keys())[0]) for p in v["participants"]] for k, v in crimesAPI if v.get("participants", False) and not v.get("initiated", False)]
        sub_ranking = [[int(list(p.keys())[0]) for p in v["participants"]] for k, v in crimesAPI if v.get("participants", False)]
        main_ranking = self.updateRanking(sub_ranking)

        # second loop over API to create new crimes
        batch = Crimes.objects.bulk_operation()
        for k, v in crimesAPI:
            # ignore old crimes
            if v["initiated"] and v["time_completed"] < old:
                # if in the DB but not initated change it to initated so that it's deleted after the loop
                # it can happen if crimes haven't been update for a while
                v["initiated"] = True
                v["participants"] = json.dumps([int(list(p.keys())[0]) for p in v["participants"]])
                h = hash(tuple(sorted(v["participants"])))
                v["team_id"] = int(hashlib.sha256(str(h).encode("utf-8")).hexdigest(), 16) % 10**8
                batch.update_or_create(tId=k, faction_id=self.pk, defaults=v)
                # self.crimes_set.filter(tId=k).update(initiated=True)
                continue

            # define if ready
            v["ready"] = not bool(v["time_left"])
            if v["ready"]:
                for status in [list(p.values())[0] for p in v["participants"]]:
                    if status is None:
                        v["ready"] = False
                        continue
                    if status.get("description") != "Okay":
                        v["ready"] = False
                        continue

            if v["ready"]:
                n["ready"] += 1

            # get crimeBD
            crimeDB = crimesDB.filter(tId=int(k)).first()

            v["participants"] = json.dumps([int(list(p.keys())[0]) for p in v["participants"]])
            h = hash(tuple(sorted(v["participants"])))
            v["team_id"] = int(hashlib.sha256(str(h).encode("utf-8")).hexdigest(), 16) % 10**8

            # create new or update non initiated
            if crimeDB is None:
                n["created"] += 1

            elif not crimeDB.initiated:
                n["updated"] += 1
                del v["participants"]

            batch.update_or_create(tId=k, faction_id=self.pk, defaults=v)

        if batch.count():
            batch.run()

        # delete old initiated crimes
        nDeleted, _ = crimesDB.filter(initiated=True, time_completed__lt=old).delete()
        n["deleted"] += nDeleted

        self.nKeys = len(self.masterKeys.filter(useFact=True))
        self.crimesUpda = now
        # save only participants ids of successful PH and PA
        self.ph_pa_Dump = json.dumps([[int(list(p.keys())[0]) for p in v["participants"] if isinstance(p, dict)] for k, v in crimesAPI if v["crime_id"] in [7, 8] and v["success"] == 1 and v.get("participants", False)])

        self.save()
        return self.crimes_set.all(), False, n

    def updateRanking(self, sub_ranking):

        # get members for ranking
        faction_members = self.member_set.order_by("-nnb").only("tId", "nnb", 'crimesRank')
        faction_members_nnb = {m.tId: m.nnb for m in faction_members}

        # DEBUG
        # members_full = {m.tId: m for m in self.member_set.all()}

        # get previous main ranking
        previous_ranking = json.loads(self.crimesRank)
        # previous_ranking = []

        # remove old players from previous ranking
        to_delete = []
        for m_id in previous_ranking:
            if m_id not in faction_members_nnb:
                to_delete.append(m_id)
        for m_id in to_delete:
            previous_ranking.remove(m_id)

        # append new members
        for m_id in [m.tId for m in faction_members]:
            if m_id not in previous_ranking:
                previous_ranking.append(m_id)

        # reorder with NNB in case there are new members
        # (well all the time...)
        current_nnb = 60
        wrong_nnb = []
        for i, m_id in enumerate(previous_ranking):
            m_nnb = faction_members_nnb[m_id]
            if m_nnb > current_nnb:
                wrong_nnb.append(m_id)
            else:
                # update current nnb if not 0 (ie if nnb is known)
                current_nnb = m_nnb if m_nnb else current_nnb

        for m_id in wrong_nnb:
            # get member NNB
            m_nnb = faction_members_nnb[m_id]
            # get previous ranking with NNB
            previous_ranking_nnb = [[m_id, faction_members_nnb[m_id]] for m_id in previous_ranking]
            # get member wrong rank
            m_rank = previous_ranking.index(m_id)

            # find the lowest position with this NNB in the previous ranking
            for p_id, p_nnb in previous_ranking_nnb:
                if p_nnb < m_nnb:  # NNB lower (assign this position then exit)
                    # assign m_id to p_id postion then exit the loop
                    # 1. get index of p_id
                    p_rank = previous_ranking.index(p_id)
                    # 2. put m_id at p_id
                    previous_ranking.insert(p_rank, previous_ranking.pop(m_rank))
                    break

        # main ranking based on previous if possible or ordered NNB
        # NOTE: can directly put previous_ranking now that we append missing members just above
        main_ranking = previous_ranking if len(previous_ranking) else [m.tId for m in faction_members]

        # DEBUG
        # main_ranking_before = main_ranking[:]

        # print("rank before:", main_ranking.index(2190204))

        # loop over the sub rankings
        for team in sub_ranking:

            # first loop over participants (member point of view)
            for member in [p for p in team if p in main_ranking]:

                # get member main and sub rank
                mem_m_rank = main_ranking.index(member)
                mem_s_rank = team.index(member)

                # second loop over participants (for comparison)
                for participant in [p for p in team if p != member and p in main_ranking]:

                    # get participant global and crime rank
                    par_m_rank = main_ranking.index(participant)
                    par_s_rank = team.index(participant)

                    # update main ranking
                    mem_m_rank = main_ranking.index(member)
                    mem_s_rank = team.index(member)

                    # check if bad ordering
                    if (mem_m_rank > par_m_rank) != (mem_s_rank > par_s_rank):

                        # change global ordering
                        if par_s_rank < mem_s_rank:
                            # participant should be above member
                            main_ranking.insert(mem_m_rank, main_ranking.pop(par_m_rank))

                        # elif par_s_rank > mem_s_rank:
                        #     # member should be above member
                        #     main_ranking.insert(par_m_rank, main_ranking.pop(mem_m_rank))

        # print("rank after:", main_ranking.index(2190204))

        # cleanup old members
        for rank_id in main_ranking:
            if rank_id not in [m.tId for m in faction_members]:
                main_ranking.remove(rank_id)

        # DEBUG
        # for i, (r1, r2) in enumerate(zip(main_ranking_before, main_ranking)):
        #     m1 = members_full[r1]
        #     m2 = members_full[r2]
        #     print(f'{i:<3}{m1.name:<16}\t{m2.name}')

        # update crimesRank
        self.crimesRank = json.dumps(main_ranking)
        self.save()

        # save members ranking
        bulk_u_mgr = BulkUpdateManager(['crimesRank'], chunk_size=100)
        for member in faction_members:
            # print(member.name, member.crimesRank, main_ranking.index(member.tId) + 1)
            # try:
            member.crimesRank = main_ranking.index(member.tId) + 1
            # except BaseException:
            # member.crimesRank = 100
            bulk_u_mgr.add(member)
        bulk_u_mgr.done()

        return main_ranking

    def cleanHistory(self):
        # clean chains
        old = tsnow() - self.getHist("chains")
        self.chain_set.filter(start__lt=old).delete()
        # clean attacks reports
        old = tsnow() - self.getHist("attacks")
        self.attacksreport_set.filter(start__lt=old).delete()
        # clean revives reports
        old = tsnow() - self.getHist("revives")
        self.revivesreport_set.filter(start__lt=old).delete()
        # clean armory reports
        old = tsnow() - self.getHist("armory")
        self.armoryreport_set.filter(start__lt=old).delete()
        # clean crimes reports
        old = tsnow() - self.getHist("crimes")
        self.crimes_set.filter(initiated=True, time_completed__lt=old).delete()

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
        # print(f'{self} check keys')
        masterKeys = self.masterKeys.all()

        for key in masterKeys:
            # print(f'{self} check key {key}: {key.value}')

            # check currency for AA perm (smallest payload and give )
            req = apiCall("faction", "", "currency", key.value, verbose=False)

            if 'apiError' in req:
                code = req['apiErrorCode']
                if code in API_CODE_DELETE:
                    # delete key
                    print("{} delete {} (API error {})".format(self, key, code))
                    key.delete()
                elif code in [4, 7, 16]:  # 4 because of API bug returning 4 in case of no perm
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

    def updateMembers(self, key=None, force=False, private=False):
        # it's not possible to delete all memebers and recreate the base
        # otherwise the target list will be lost

        now = tsnow()

        # don't update if less than 5 minutes and force is False
        # if not force and (now - self.membersUpda) < 300:
        #     print("{} skip update member".format(self))
        #     return self.member_set.all()

        # get key if needed
        if key is None or isinstance(key, bool):
            key = self.getKey()

        # call members and return error
        membersAPI = apiCall('faction', '', 'basic', key.value, sub='members')
        key.lastPulled = tsnow()
        key.reason = "Update member list"
        key.save()

        if 'apiError' in membersAPI:
            return membersAPI


        batch = Member.objects.bulk_operation()
        players_on_yata = Player.objects.filter(tId__in=membersAPI)

        # set members newly on yata from -1 to 0
        id_on_yata = [p.tId for p in players_on_yata]
        members_on_yata = self.member_set.filter(tId__in=id_on_yata)
        members_on_yata.filter(shareE=-1).update(shareE=0)
        members_on_yata.filter(shareN=-1).update(shareN=0)
        members_on_yata.filter(shareS=-1).update(shareS=0)

        # force low level perm to 0
        id_low_lvl = [p.tId for p in players_on_yata.filter(key_level__lt=3)]
        self.member_set.filter(tId__in=id_low_lvl).update(
            shareE=0,
            shareN=0,
            shareS=0
        )

        # set members not on yata to -1
        self.member_set.exclude(tId__in=id_on_yata).update(
            shareE=-1,
            shareN=-1,
            shareS=-1
        )

        for k, v in membersAPI.items():

            defaults = {
                "faction_id": int(self.id),
                "name": v["name"],
                "daysInFaction": v["days_in_faction"],
                "lastActionStatus": v["last_action"]["status"],
                "lastAction": v["last_action"]["relative"],
                "lastActionTS": v["last_action"]["timestamp"]
            }

            # status
            for k2, v2 in v['status'].items():
                defaults[k2] = v2

            batch.update_or_create(
                # faction_id=int(self.id),
                tId=int(k),
                defaults=defaults
            )

        if batch.count():
            batch.run()

        membersDB = self.member_set.all()

        # delete old members and update private data
        for m in membersDB:
            if membersAPI.get(str(m.tId)) is None:
                m.delete()
                continue

            if private:
                m.updatePrivateData()

        # remove AA keys from old members
        for key in self.masterKeys.all():
            if not len(self.member_set.filter(tId=key.tId)):
                self.delKey(tId=key.tId)

        self.nKeys = len(self.masterKeys.filter(useFact=True))
        self.membersUpda = now
        self.save()
        return membersDB

    def getLogs(self, page=1, n_logs=7):
        logsAll = self.log_set.order_by("timestamp").all()
        logtmp = dict({})
        r = 0
        m = 0
        for log in logsAll:
            logtmp[log.timestamp] = {"deltaMoney": (log.money - log.donationsmoney) - m, "deltaRespect": log.respect - r}
            m = (log.money - log.donationsmoney)
            r = log.respect

        logsAll = logsAll.order_by("-timestamp").all()
        for log in logsAll:
            log.deltaMoney = logtmp[log.timestamp]["deltaMoney"]
            log.deltaRespect = logtmp[log.timestamp]["deltaRespect"]
        logs = Paginator(logsAll, n_logs).get_page(page)

        return logs, logsAll

    def updateLog(self):

        # get key
        key = self.getKey()
        if key is None:
            msg = "{} no key to update news".format(self)
            self.nKey = 0
            self.save()
            return False, "No keys to update the armory."

        # api call
        selection = 'stats,donations,currency,basic,timestamp'
        factionInfo = apiCall('faction', self.tId, selection, key.value, verbose=False)
        if 'apiError' in factionInfo:
            msg = "Update logs ({})".format(factionInfo["apiErrorString"])
            if factionInfo['apiErrorCode'] in API_CODE_DELETE:
                print("{} {} (remove key)".format(self, msg))
                self.delKey(key=key)
            else:
                key.reason = msg
                key.lastPulled = factionInfo.get("timestamp", 0)
                key.save()
                print("{} {}".format(self, msg))
            return False, "API error {}, logs not updated.".format(factionInfo["apiErrorString"])

        now = factionInfo.get("timestamp", 0)

        # update key
        key.reason = "Update logs"
        key.lastPulled = now
        key.save()

        # update faction
        self.maxmembers = max(self.maxmembers, len(factionInfo["members"]))
        self.daysold = factionInfo["age"]
        self.respect = factionInfo["respect"]

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
        self.save()
        return True, "Logs updated"

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
            if contributors['apiErrorCode'] in API_CODE_DELETE:
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
        # contributors["contributors"] is not None and -> fix contributors being None
        if contributors["contributors"] is not None and stat in contributors["contributors"]:
            con = contributors["contributors"][stat]
            now = tsnow()
            hour = now - now % (3600 // 4)

            # set all current members to 0
            # it prevents non contributors being treated as non members
            c = dict({str(m.tId): [m.name, 0] for m in self.member_set.all()})
            # c = dict({})
            # for k, v in {k: v for k, v in con.items() if v["in_faction"]}.items():
            for k, v in {k: v for k, v in con.items()}.items():
                c[k] = [mem.get(k, dict({"name": "Player"})).get("name"), v["contributed"]]

            # need to add contributors if in faction but hasn't contributed

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
        facInfo = apiCall('faction', self.tId, "basic,upgrades", key.value, verbose=False)
        if 'apiError' in facInfo:
            msg = "Update faction upgrades ({})".format(facInfo["apiErrorString"])
            if facInfo['apiErrorCode'] in API_CODE_DELETE:
                print("{} {} (remove key)".format(self, msg))
                self.delKey(key=key)
            else:
                key.reason = msg
                key.lastPulled = facInfo.get("timestamp", 0)
                key.save()
                print("{} {}".format(self, msg))
            return False, "API error {}, faction upgrades not updated".format(facInfo["apiErrorString"])

        upgrades = facInfo["upgrades"]
        self.respect = facInfo.get("respect", 0)

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
            v["unsets_completed"] = v.get("unsets_completed", 0)
            try:
                self.upgrade_set.update_or_create(tId=k, simu=False, defaults=v)
            except BaseException as e:
                self.upgrade_set.filter(tId=k, simu=False).all().delete()
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
            try:  # in case getTree retursn None
                branch = upgrade.getTree().branch
                if branch not in branchCost:
                    branchCost[branch] = 0

                for u in allUpgrades.filter(shortname=upgrade.shortname, level__lte=upgrade.level):
                    branchCost[branch] += u.base_cost
            except BaseException:
                pass

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
            45: [[46, 7]],  # maximum life
            48: [[47, 3]],  # escape

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
            46: [[45, 7]],  # defense
            47: [[48, 3]],  # dexterity

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

    def getSpies(self):
        from faction.functions import optimize_spies

        all_spies = cache.get(f"spy-faction-{self.tId}")
        print(f'[getSpies] faction cache: {"no" if all_spies is None else "yes"}')
        if all_spies is None or settings.DEBUG:
            all_spies = {}
            for database in self.spydatabase_set.all():
                for target_id, spy in database.getSpies(cc=True).items():
                    all_spies[target_id] = optimize_spies(spy, all_spies[target_id]) if target_id in all_spies else spy
            cache.set(f"spy-faction-{self.tId}", all_spies, 3600)

        return all_spies

    def json(self):
        from faction.serializer import FactionSerializer
        return FactionSerializer(self).data


class Member(models.Model):
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    tId = models.IntegerField(default=0, unique=True)
    name = models.CharField(default="Duke", max_length=15)
    daysInFaction = models.IntegerField(default=0)
    bonusScore = models.IntegerField(default=0)

    # last action
    lastAction = models.CharField(default="-", max_length=200)
    lastActionTS = models.IntegerField(default=0)
    lastActionStatus = models.CharField(default="Offline", max_length=16)

    # new status of december 2019
    description = models.CharField(default="", max_length=128, blank=True)
    details = models.CharField(default="", max_length=128, blank=True)
    state = models.CharField(default="", max_length=64, blank=True)
    color = models.CharField(default="", max_length=16, blank=True)
    until = models.IntegerField(default=0)

    # honors
    singleHitHonors = models.IntegerField(default=0)  # 1: carnage, 2: massacren 3: genocide

    # share energy and NNB with faction
    # -1: not on YATA 0: doesn't wish to share 1: share
    shareE = models.IntegerField(default=1)
    energy = models.IntegerField(default=0)
    energyRefillUsed = models.BooleanField(default=False)
    revive = models.BooleanField(default=False)
    drugCD = models.IntegerField(default=0)

    # share natural nerve bar
    # -1: not on YATA 0: doesn't wish to share 1: share
    shareN = models.IntegerField(default=1)
    nnb = models.IntegerField(default=0)
    arson = models.IntegerField(default=0)
    crimesRank = models.IntegerField(default=100)

    # share stats
    # -1: not on YATA 0: doesn't wish to share 1: share
    shareS = models.IntegerField(default=-1)
    dexterity = models.BigIntegerField(default=0)
    defense = models.BigIntegerField(default=0)
    speed = models.BigIntegerField(default=0)
    strength = models.BigIntegerField(default=0)

    objects = BulkManager()

    def __str__(self):
        return format_html("{} [{}]".format(self.name, self.tId))

    def updateEnergy(self, key=None, save=False, req=False):
        error = False
        if not self.shareE:
            self.energy = 0
        else:
            if not req:
                req = apiCall("user", "", "bars,refills,cooldowns,perks", key=key)

            # url = "https://api.torn.com/user/?selections=bars&key=2{}".format(key)
            # req = requests.get(url).json()
            if 'apiError' in req:
                error = req
                self.energy = 0
                self.energyRefillUsed = True
                self.drugCD = 0
            else:
                energy = req['energy'].get('current', 0)
                self.energy = energy
                self.energyRefillUsed = req["refills"]["energy_refill_used"] is True
                self.revive = "+ Ability to revive" in req["job_perks"]
                self.drugCD = req["cooldowns"]["drug"]

        if save:
            self.save()

        return error

    def updateHonors(self, key=None, save=False, req=False):
        if self.singleHitHonors == 3:
            return False

        error = False
        if not req:
            req = apiCall("user", "", "honors", key=key)

        if 'apiError' in req:
            error = req
        else:
            if 478 in req["honors_awarded"]:
                self.singleHitHonors = 3
            elif 477 in req["honors_awarded"]:
                self.singleHitHonors = 2
            elif 256 in req["honors_awarded"]:
                self.singleHitHonors = 1

        if save:
            self.save()

        return error

    def updateStats(self, key=None, save=False, req=False):
        error = False
        if not self.shareS:
            self.dexterity = 0
            self.defense = 0
            self.speed = 0
            self.strength = 0
        else:
            if not req:
                req = apiCall("user", "", "battlestats", key=key)

            # url = "https://api.torn.com/user/?selections=bars&key=2{}".format(key)
            # req = requests.get(url).json()
            if 'apiError' in req:
                error = req
                self.dexterity = 0
                self.defense = 0
                self.speed = 0
                self.strength = 0
            else:
                self.dexterity = int(str(req.get('dexterity', 0)).replace(",", ""))
                self.defense = int(str(req.get('defense', 0)).replace(",", ""))
                self.speed = int(str(req.get('speed', 0)).replace(",", ""))
                self.strength = int(str(req.get('strength', 0)).replace(",", ""))

        if save:
            self.save()

        return error

    def updateNNB(self, key=None, save=False, req=False):
        error = False
        if not self.shareN:
            self.nnb = 0
            self.arson = 0
        else:
            if not req:
                req = apiCall("user", "", "perks,bars,crimes", key=key)

            if 'apiError' in req:
                error = req
                self.nnb = 0
                self.arson = 0
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

                # compute equivalent arons
                arson = req["criminalrecord"].get("fraud_crimes", 0)  # assumed arson
                arson += 0.11 * req["criminalrecord"].get("theft", 0)  # assumed steal jackets
                arson += 0.66 * req["criminalrecord"].get("auto_theft", 0)  # assumed Steal Parked Car
                arson -= 0.5 * req["criminalrecord"].get("drug_deals", 0)  # assumed -5k for 10k
                arson += 0.5 * req["criminalrecord"].get("computer_crimes", 0)  # assumed Stealth Virus
                arson += 0.66 * req["criminalrecord"].get("murder", 0)  # assumed Assassinate Mob Boss
                for oc in json.loads(self.faction.ph_pa_Dump):
                    if self.tId in oc:
                        add = 650 if len(oc) == 4 else 150  # PA or PH
                        arson += add
                self.arson = int(arson)
        if save:
            self.save()

        return error

    def updatePrivateData(self):
        player = Player.objects.filter(tId=self.tId).first()
        if player is None:
            self.shareE = -1
            self.shareN = -1
            self.shareS = -1
        elif player.key_level < 3:
            self.shareE = 0
            self.shareN = 0
            self.shareS = 0
        else:
            key = player.getKey()
            selections = [
                "perks",
                "bars",
                "crimes",
                "battlestats",
                "honors",
                "refills",
                "cooldowns"
            ]
            req = apiCall("user", "", ",".join(selections), key=player.getKey())
            self.updateEnergy(req=req)
            self.updateStats(req=req)
            self.updateNNB(req=req)
            self.updateHonors(req=req)
            self.updateHonors(req=req)
        self.save()

    def shareData(self):
        return self.shareE > 0 or self.shareN > 0 or self.shareS > 0

    def getTotalStats(self):
        return self.dexterity + self.speed + self.strength + self.defense

    def json(self):
        from faction.serializer import MemberSerializer
        return MemberSerializer(self).data


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
    respectComputed = models.FloatField(default=0)  # actual respect computed

    # blameched variables
    addToEnd = models.IntegerField(default=10)  # add seconds to end timestamp if chain didn't reach last hit

    # for the combined report
    combine = models.BooleanField(default=False)

    # share ID
    shareId = models.SlugField(default="", null=True, blank=True, max_length=32)

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
        crontab_type = "crontabs_chain_live" if self.live else "crontabs_chain_report"
        if chain is None or chain.crontab not in getCrontabs(crontab_type):
            cn = {c: len(Chain.objects.filter(crontab=c).only('crontab')) for c in getCrontabs(crontab_type)}
            self.crontab = sorted(cn.items(), key=lambda x: x[1])[0][0]
        elif chain is not None:
            self.crontab = chain.crontab
        self.save()
        return self.crontab

    def getNextBonus(self):
        for i in BONUS_HITS:
            if i >= self.current:
                return i
        return 100000

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
        tsl = self.start if lastAttack is None else max(lastAttack.timestamp_started, self.last)
        self.last = tsl

        print("{} live    {}".format(self, self.live))
        print("{} start   {} {}".format(self, timestampToDate(tss), tss))
        print("{} last    {} {}".format(self, timestampToDate(tsl), tsl))
        print("{} end     {} {}".format(self, timestampToDate(tse), tse))
        if self.cooldown:
            tse += self.chain * 6
            print("{} end cd   {} {}".format(self, timestampToDate(tse), tse))
        else:
            self.current = min(self.current, self.chain)

        # add +n seconds to the endTS
        tse += self.addToEnd
        if self.addToEnd:
            print("{} end+    {}".format(self, timestampToDate(tse)))

        # get existing attacks (just the ids)
        attacks = [r.tId for r in self.attackchain_set.all()]
        print("{} {} existing attacks".format(self, len(attacks)))

        # get the keys and init the attacks dict
        apiAttacks = {}
        keys = faction.masterKeys.filter(useFact=True).order_by("lastPulled")
        nKeys = len(keys)

        # stop if no master keys
        if not nKeys:
            print("{} no keys".format(self))
            self.computing = False
            self.crontab = 0
            self.attackchain_set.all().delete()
            self.state = -1
            self.save()
            return self.state

        # loop over keys to get the attacks
        for i, key in enumerate(keys):
            print(f"{self} Key #{i}: {key}")

            # prevent cache response
            delay = min(tsnow() - faction.lastAttacksPulled, tsnow() - self.update)
            if delay < 32:
                sleeptime = 32 - delay
                print("{} last update {}s ago, waiting {} for cache...".format(self, delay, sleeptime))
                time.sleep(sleeptime)

            # make call
            selection = "chain,attacks,timestamp&from={}&to={}".format(tsl - 1, tse)
            req = apiCall("faction", faction.tId, selection, key.value, verbose=True)
            key.reason = "Pull attacks for chain report"
            key.lastPulled = tsnow()
            key.save()

            # in case there is an API error
            # A single key error will trigger a status for the whole report
            # even if the other keys are good
            # It can be optimized but since it's never a critical status it's ok for now
            if "apiError" in req:
                print('{}\t api key error: {}'.format(self, req['apiError']))
                if req['apiErrorCode'] in API_CODE_DELETE:
                    faction.delKey(key=key)
                    print("{} --> deleting {}'s key from faction (blank turn)".format(self, key.player))
                    self.state = -2
                    self.save()
                    return self.state

                self.state = -3
                self.save()
                return self.state

            # try to catch cache response
            tornTS = int(req["timestamp"])
            nowTS = tsnow()
            cache = abs(nowTS - tornTS)
            print("{}\t cache = {}s".format(self, cache))
            print("{}\t attacks in the API = {}".format(self, len(req["attacks"])))

            # in case cache
            if cache > CACHE_RESPONSE:
                print('{}\t probably cached response... (blank turn)'.format(self))
                self.state = -4
                self.save()
                return self.state

            if self.live:
                print("{}\t update values".format(self))
                self.chain = req["chain"]["current"]

            n = 0
            for id, attack in req["attacks"].items():
                if id not in apiAttacks:
                    n += 1
                    apiAttacks[id] = attack
                    tsl = max(tsl, attack["timestamp_started"])

            print(f'{self}\t adding {n} attacks')
            print(f'{self}\t last time {timestampToDate(tsl)}')
            if not n:
                print(f'{self}\t escape loop because no new attacks')
                break

        # update timestamp
        self.update = tsnow()
        faction.lastAttacksPulled = self.update
        faction.save()

        # in case empty payload
        if not len(apiAttacks):
            print('{} empty payload'.format(self))
            self.computing = False
            self.crontab = 0
            self.state = -5
            self.save()
            return self.state

        print("{} {} attacks from the API".format(self, len(apiAttacks)))

        newEntry = 0
        batch = AttackChain.objects.bulk_operation()
        for k, v in apiAttacks.items():
            ts = int(v["timestamp_started"])
            tsl = max(tsl, ts)

            # probably because of cache
            # before = int(v["timestamp_started"]) - self.last
            # after = int(v["timestamp_ended"]) - tse
            # if before < 0 or after > 0:
            #     print(f'{self} Attack out of bound')
            #     print(f'{self}\t timestamp_started = {v["timestamp_started"]} {timestampToDate(v["timestamp_started"])}')
            #     print(f'{self}\t timestamp_ended = {v["timestamp_ended"]} {timestampToDate(v["timestamp_ended"])}')
            #     print(f'{self}\t self.last = {self.last} {timestampToDate(self.last)}')
            #     print(f'{self}\t tse = {tse} {timestampToDate(tse)}')
            #     print(f'{self}\t before = {before}s')
            #     print(f'{self}\t after = {after}s')

            newAttack = int(k) not in attacks
            factionAttack = v["attacker_faction"] == faction.tId
            respect = float(v["respect_gain"]) > 0

            # we can display this warning but can't trust it as sometimes hits are 1s after the official end of the chain.
            if v["timestamp_ended"] < self.start or v["timestamp_ended"] > self.end:
                print(f'{self} attack out of bound {k}: {v["code"]}')

            if newAttack and factionAttack:

                v = modifiers2lvl1(v)
                # self.attackchain_set.get_or_create(tId=int(k), defaults=v)
                batch.update_or_create(report_id=int(self.id), tId=int(k), defaults=v)
                newEntry += 1
                # tsl = max(tsl, ts)
                if int(v["timestamp_ended"]) - self.end - self.addToEnd <= 0:  # case we're before cooldown
                    self.current = max(self.current, v["chain"])
                elif self.cooldown and respect:  # case we're after cooldown and we want cooldown
                    self.current += 1

                # print("{} attack [{}] current {}".format(self, k, current))

        if batch.count():
            batch.run()

        self.last = tsl

        print("{} last  {}".format(self, timestampToDate(self.last)))
        print("{} new entries {}".format(self, newEntry))
        print("{} progress {} / {}: {}%".format(self, self.current, self.chain, self.progress()))

        if self.live:

            if req["chain"]["current"] < 10:
                print("{} reached end of live chain [stop]".format(self))
                self.computing = False
                self.crontab = 0
                self.state = 50
                self.save()
                return self.state

        elif self.cooldown:

            # not live and with cooldown

            if len(apiAttacks) < MINIMAL_API_ATTACKS_STOP:
                # (nearly) empty payload can occur when faction stop attacking  or reveiving attacks before end of cooldown
                print("{} no api entry (not live) (cooldown) [stop]".format(self))
                self.computing = False
                self.crontab = 0
                self.state = 52
                self.save()
                return self.state

            if not newEntry and len(apiAttacks) > 1:
                # no new entry should happen only if full payload doesn't count for the chain
                # last attack ts is still updated so next call should be different
                print("{} no new entry from payload (not live) (cooldown) [continue]".format(self))
                self.state = 32
                self.save()
                return self.state

        else:

            if self.current == self.chain:
                print("{} Reached end of chain (not live) (no cooldown) [stop]".format(self))
                self.computing = False
                self.crontab = 0
                self.state = 51
                self.save()
                return self.state

            if len(apiAttacks) < MINIMAL_API_ATTACKS_STOP or not newEntry:
                # empty api call

                if self.addToEnd > 3600:
                    # stop adding
                    print("{} didn't find last attack even looking after 1 hour (not live) (no cooldown) [stop]".format(self))
                    self.computing = False
                    self.crontab = 0
                    self.state = -6
                    self.save()
                    return self.state

                else:
                    # add 10 seconds
                    print("{} no new entry (not live) (no cooldown) [continue]".format(self))
                    self.addToEnd += 10
                    self.state = 21
                    self.save()
                    return self.state

            # if not newEntry and len(apiAttacks) > 1:
            #     print("{} no new entry from payload (not live) (no cooldown) [continue]".format(self))
            #     self.computing = False
            #     self.crontab = 0
            #     self.state = -6
            #     self.save()
            #     return -6

        # all good continue computing status
        if self.live:
            self.state = 10
        elif self.cooldown:
            self.state = 12
        else:
            self.state = 11

        self.save()
        return self.state

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
            # 2: fair_fight
            # 3: war
            # 4: retaliation
            # 5: group_attack
            # 6: overseas
            # 7: chain_bonus
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
        chain_hit_count = []
        for att in self.attackchain_set.order_by('timestamp_ended'):
            attackerID = att.attacker_id
            attackerName = att.attacker_name
            # if attacker part of the faction at the time of the chain
            if att.attacker_faction == faction.tId:
                if att.chain in chain_hit_count:
                    print(f'{self} ignoring attack {att.tId} {att.code}: second hit #{att.chain}')
                    continue

                # if attacker not part of the faction at the time of the call
                if attackerID not in attackers:
                    # print('[function.chain.fillReport] hitter out of faction: {} [{}]'.format(attackerName, attackerID))
                    attackers[attackerID] = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1, attackerName, 0, 0, 0]  # add out of faction attackers on the fly

                attackers[attackerID][0] += 1
                nWRA[2] += 1


                if self.cooldown:
                    its_a_hit = att.respect_gain > 0.0
                else:
                    its_a_hit = att.respect_gain > 0.0 and att.chain
                if its_a_hit:

                    # init lastTS for the first iteration of the loop
                    lastTS = att.timestamp_ended if lastTS == 0 else lastTS

                    # compute chain watcher version 2
                    # condition added in order **not** to count watcher in CD
                    timeSince = att.timestamp_ended - lastTS if att.timestamp_ended <= self.end else 0
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
                        # don't add bonus as hist in attackers[attackerID][1]
                        # because it's already accounded for in the report
                        attackers[attackerID][12] += 1
                        r = getBonusHits(att.chain, att.timestamp_ended)
                        # print('{} bonus {}: {} respects'.format(self, att.chain, r))
                        bonus.append((att.chain, attackerID, attackerName, att.respect_gain, r, att.defender_id, att.defender_name))
                    else:
                        attackers[attackerID][1] += 1
                        attackers[attackerID][2] += float(att.fair_fight)
                        attackers[attackerID][3] += float(att.war)
                        attackers[attackerID][4] += float(att.retaliation)
                        attackers[attackerID][5] += float(att.group_attack)
                        attackers[attackerID][6] += float(att.overseas)
                        attackers[attackerID][7] += float(att.chain_bonus)
                        attackers[attackerID][8] += float(att.respect_gain) / float(att.chain_bonus)
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

        # create histogram OLD WAY
        # diff = max(int(self.last - self.start), 1)
        # binsGapMinutes = 5
        # while diff / (binsGapMinutes * 60) > 256:
        #     binsGapMinutes += 5
        #
        # bins = [self.start]
        # for i in range(256):
        #     add = bins[i] + (binsGapMinutes * 60)
        #     if add > self.last:
        #         break
        #     bins.append(add)
        # create histogram OLD WAY
        diff = max(int(self.last - self.start), 1)
        if diff < 3600:
            binsGapMinutes = 5
        elif diff < 2 * 3600:
            binsGapMinutes = 10
        elif diff < 6 * 3600:
            binsGapMinutes = 30
        else:
            binsGapMinutes = 60

        bins = [self.start - self.start % (binsGapMinutes * 60)]
        while True:
            add = bins[-1] + (binsGapMinutes * 60)
            if add > self.last:
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
            self.chain = nWRA[0]  # update for live chains
            self.respect = nWRA[1]  # update for live chains
        self.attacks = nWRA[2]
        self.respectComputed = nWRA[1]
        self.save()

        # fill the database with counts
        print('{} fill database with counts'.format(self))
        self.count_set.all().delete()
        hitsForStats = []

        batch = Count.objects.bulk_operation()
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
            # 2: fair_fight
            # 3: war
            # 4: retaliation
            # 5: group_attack
            # 6: overseas
            # 7: chain_bonus
            # 8:respect_gain
            # 9: daysInFaction
            # 10: tId
            # 11: for chain watch
            # 12: #bonuses
            # 13: #war
            batch.update_or_create(
                chain_id=self.id,
                attackerId=k,
                name=v[10],
                hits=v[0],
                wins=v[1],
                bonus=v[12],
                fair_fight=v[2],
                war=v[3],
                retaliation=v[4],
                group_attack=v[5],
                overseas=v[6],
                respect=v[8],
                daysInFaction=v[9],
                beenThere=beenThere,
                graph=graphTmp,
                watcher=watcher,
                warhits=v[13]
            )

        if batch.count():
            batch.run(batch_size=20)

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

    def progress_cd(self):

        # return progress based on attacks if < 100
        attack_progress = self.progress()
        if attack_progress < 100:
            return attack_progress

        # otherwise return progress based on elapsed time in CD
        if self.cooldown:
            return int(100 * (self.last - self.end) / (6 * max(self.chain, 1)))
        else:
            return 0

    def show_progress(self):
        if self.cooldown:
            return self.progress_cd()
        else:
            return self.progress()

    def displayCrontab(self):
        if self.crontab > 0:
            return "#{}".format(self.crontab)
        elif self.crontab == 0:
            return "No crontab assigned"
        else:
            return "Special crontab you lucky bastard..."

    def json(self):
        from faction.serializer import ChainSerializer
        return ChainSerializer(self).data


class Count(models.Model):
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE)
    attackerId = models.IntegerField(default=0)
    name = models.CharField(default="Duke", max_length=15)
    hits = models.IntegerField(default=0)
    bonus = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    respect = models.FloatField(default=0)
    fair_fight = models.FloatField(default=0)
    war = models.FloatField(default=0)
    retaliation = models.FloatField(default=0)
    group_attack = models.FloatField(default=0)
    overseas = models.FloatField(default=0)
    daysInFaction = models.IntegerField(default=0)
    beenThere = models.BooleanField(default=False)
    graph = models.TextField(default="", null=True, blank=True)
    watcher = models.FloatField(default=0)
    warhits = models.IntegerField(default=0)

    # bulk manager
    objects = BulkManager()

    def __str__(self):
        return format_html("Count for {}".format(self.chain))

    def json(self):
        from faction.serializer import CountSerializer
        return CountSerializer(self).data


class Bonus(models.Model):
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE)
    tId = models.IntegerField(default=0)
    name = models.CharField(default="Duke", max_length=15)
    hit = models.IntegerField(default=0)
    respect = models.FloatField(default=0)
    targetId = models.IntegerField(default=0)
    targetName = models.CharField(default="Unknown", max_length=15)

    def __str__(self):
        return format_html("Bonus for {}".format(self.chain))

    def json(self):
        from faction.serializer import BonusSerializer
        return BonusSerializer(self).data


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
    respect = models.FloatField(default=0.0)
    respect_gain = models.FloatField(default=0.0)
    respect_lost = models.FloatField(default=0.0)
    raid = models.BooleanField(default=False)
    ranked_war = models.BooleanField(default=False)
    chain = models.IntegerField(default=0)
    code = models.SlugField(default="0", max_length=32)


    # mofifiers
    fair_fight = models.FloatField(default=0.0)
    war = models.IntegerField(default=0)
    retaliation = models.FloatField(default=0.0)
    group_attack = models.FloatField(default=0.0)
    overseas = models.FloatField(default=0.0)
    chain_bonus = models.FloatField(default=0.0)

    objects = BulkManager()

    def __str__(self):
        return format_html("Attack for chain [{}]".format(self.tId))


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
    # from when reports were filled by the user
    # fill = models.IntegerField(default=0)

    # global information for the report
    factions = models.TextField(default="[]")
    player_filter = models.IntegerField(default=0)
    filter = models.IntegerField(default=0)  # 0: no filters, 10: incoming, 01: outgoing, 11: both
    defends = models.IntegerField(default=0)
    attacks = models.IntegerField(default=0)

    # war
    war = models.TextField(default="{}")
    war_type = models.CharField(default="Unkown", max_length=16)
    war_id = models.IntegerField(default=0)

    # share ID
    shareId = models.SlugField(default="", null=True, blank=True, max_length=32)

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
        crontab_type = "crontabs_attacks_live" if self.live else "crontabs_attacks_report"
        if report is None or report.crontab not in getCrontabs(crontab_type):
            cn = {c: len(AttacksReport.objects.filter(crontab=c).only('crontab')) for c in getCrontabs(crontab_type)}
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
        lastAttack = self.attackreport_set.order_by("-timestamp_started").first()
        tsl = self.start if lastAttack is None else max(lastAttack.timestamp_started, self.last)
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
            # self.attackreport_set.filter(timestamp_started__gt=weekAgo).delete()
            self.state = -7
            self.save()
            return -7

        # add + 2 s to the endTS
        tse += 10

        # get existing attacks (just the ids)
        attacks = [r.tId for r in self.attackreport_set.all()]
        print("{} {} existing attacks".format(self, len(attacks)))

        # get the keys and init the attacks dict
        apiAttacks = {}
        keys = faction.masterKeys.filter(useFact=True).order_by("lastPulled")
        nKeys = len(keys)

        # stop if no master keys
        if not keys:
            print("{} no key".format(self))
            self.computing = False
            self.crontab = 0
            self.attackreport_set.all().delete()
            self.state = -1
            self.save()
            return -1

        # loop over keys to get the attacks
        for i, key in enumerate(keys):
            print(f"{self} Key #{i}: {key}")

            # prevent cache response
            delay = min(tsnow() - faction.lastAttacksPulled, tsnow() - self.update)
            if delay < 32:
                sleeptime = 32 - delay
                print("{} last update {}s ago, waiting {} for cache...".format(self, delay, sleeptime))
                time.sleep(sleeptime)

            # make call
            selection = "attacks,timestamp&from={}&to={}".format(tsl - 1, tse)
            req = apiCall("faction", faction.tId, selection, key.value, verbose=False)
            key.reason = "Pull attacks for attacks report"
            key.lastPulled = tsnow()
            key.save()

            # in case there is an API error
            # A single key error will trigger a status for the whole report
            # even if the other keys are good
            # It can be optimized but since it's never a critical status it's ok for now
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
            nowTS = tsnow()
            cache = abs(nowTS - tornTS)
            print("{} cache = {}s".format(self, cache))

            # in case cache
            if cache > CACHE_RESPONSE:
                print('{} probably cached response... (blank turn)'.format(self))
                self.state = -4
                self.save()
                return -4

            n = 0
            for id, attack in req["attacks"].items():
                if id not in apiAttacks:
                    n += 1
                    apiAttacks[id] = attack
                    tsl = max(tsl, attack["timestamp_started"])

            print(f'{self}\t adding {n} attacks')
            print(f'{self}\t last time {timestampToDate(tsl)}')
            if not n:
                print(f'{self}\t escape loop because no new attacks')
                break

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
        batch = AttackReport.objects.bulk_operation()
        for k, v in apiAttacks.items():
            ts = int(v["timestamp_started"])

            # probably because of cache
            before = int(v["timestamp_started"]) - self.last
            after = int(v["timestamp_started"]) - tse
            if before < 0 or after > 0:
                print("{} /!\ ts out of bound: before = {} after = {}".format(self, before, after))

            newAttack = int(k) not in attacks
            factionAttack = v["attacker_faction"] == faction.tId
            # chainAttack = int(v["chain"])
            if newAttack:
                v = modifiers2lvl1(v)
                batch.update_or_create(report_id=int(self.id), tId=int(k), defaults=v)
                newEntry += 1
                tsl = max(tsl, ts)

                if factionAttack:
                    self.attacks += 1
                else:
                    self.defends += 1

        if batch.count():
            batch.run()
        self.last = tsl

        print("{} last  {}".format(self, timestampToDate(self.last)))
        print("{} progress ({})%".format(self, self.progress()))

        # if not newEntry and len(apiAttacks) > 1:
        #     print("{} no new entry with cache = {} [continue]".format(self, cache))
        #     self.state = -6
        #     self.save()
        #     return -6

        if len(apiAttacks) < MINIMAL_API_ATTACKS_STOP and not self.live:
            print("{} no api entry for non live chain [stop]".format(self))
            self.computing = False
            self.crontab = 0
            self.state = 1
            self.last = self.end
            self.save()
            return 1

        if len(apiAttacks) < 2 and self.live:
            print("{} no api entry for live chain [continue]".format(self))
            self.state = 2
            self.end = self.last
            self.save()
            return 2

        self.state = 3
        self.update = tsnow()
        self.save()
        return 3

    def fillReport(self):
        print("{} fill report".format(self))
        allAttacks = self.attackreport_set.all()

        # put stealth as faction id = -1
        allAttacks.filter(attacker_id=0).update(attacker_faction=-1)

        self.attacks = len(allAttacks.filter(attacker_faction=self.faction.tId))
        self.defends = len(allAttacks.exclude(attacker_faction=self.faction.tId))

        print("{} attacks {} {}".format(self, self.attacks, self.defends))
        print("{} set players and factions counts".format(self))
        # create factions and players
        f_set = dict({})
        p_set = dict({})
        for attack in allAttacks:
            won = attack.result not in ["Stalemate", "Assist", "Lost", "Timeout", "Escape"]

            # handle attacker faction
            if attack.attacker_faction in f_set:
                n = [f_set[attack.attacker_faction][k] for k in ["hits", "attacks", "defends", "attacked"]]
                n[0] = n[0] + 1 if won else n[0]
                n[1] = n[1] + 1
            else:
                n = [1 if won else 0, 1, 0, 0]
            f_set[attack.attacker_faction] = {"faction_id": attack.attacker_faction, "faction_name": attack.attacker_factionname,
                                              "hits": n[0], "attacks": n[1], "defends": n[2], "attacked": n[3]}

            # handle defender faction
            if attack.defender_faction in f_set:
                n = [f_set[attack.defender_faction][k] for k in ["hits", "attacks", "defends", "attacked"]]
                n[2] = n[2] if won else n[2] + 1
                n[3] = n[3] + 1
            else:
                n = [0, 0, 0 if won else 1, 1]
            f_set[attack.defender_faction] = {"faction_id": attack.defender_faction, "faction_name": attack.defender_factionname,
                                              "hits": n[0], "attacks": n[1], "defends": n[2], "attacked": n[3]}

            # handle attacker player
            if attack.attacker_id in p_set:
                n = [p_set[attack.attacker_id][k] for k in ["hits", "attacks", "defends", "attacked"]]
                n[0] = n[0] + 1 if won else n[0]
                n[1] = n[1] + 1
            else:
                n = [1 if won else 0, 1, 0, 0]
            p_set[attack.attacker_id] = {"player_id": attack.attacker_id, "player_name": attack.attacker_name,
                                         "player_faction_id": attack.attacker_faction, "player_faction_name": attack.attacker_factionname,
                                         "hits": n[0], "attacks": n[1], "defends": n[2], "attacked": n[3]}

            # handle defender player
            if attack.defender_id in p_set:
                n = [p_set[attack.defender_id][k] for k in ["hits", "attacks", "defends", "attacked"]]
                n[2] = n[2] if won else n[2] + 1
                n[3] = n[3] + 1
            else:
                n = [0, 0, 0 if won else 1, 1]
            p_set[attack.defender_id] = {"player_id": attack.defender_id, "player_name": attack.defender_name,
                                         "player_faction_id": attack.defender_faction, "player_faction_name": attack.defender_factionname,
                                         "hits": n[0], "attacks": n[1], "defends": n[2], "attacked": n[3]}

        print("{} update factions".format(self))

        # update factions
        batch = AttacksFaction.objects.bulk_operation()
        for k, v in f_set.items():
            defaults={
                "hits": int(v["hits"]),
                "attacks": int(v["attacks"]),
                "defends": int(v["defends"]),
                "attacked": int(v["attacked"])
            }
            batch.update_or_create(
                report_id=int(self.id),
                faction_id=int(k),
                faction_name=v["faction_name"],
                defaults=defaults
            )

        if batch.count():
            batch.run(batch_size=20)

        # update players
        batch = AttacksPlayer.objects.bulk_operation()
        for k, v in p_set.items():
            defaults={
                "hits": int(v["hits"]),
                "attacks": int(v["attacks"]),
                "defends": int(v["defends"]),
                "attacked": int(v["attacked"])
            }
            batch.update_or_create(
                report_id=int(self.id),
                player_id=int(k),
                player_name=v["player_name"],
                player_faction_id=int(v["player_faction_id"]),
                player_faction_name=v["player_faction_name"],
                defaults=defaults
            )

        if batch.count():
            batch.run(batch_size=20)

        # set show/hide
        print("{} show hide".format(self))
        self.attacksfaction_set.all().update(show=False)
        self.attacksplayer_set.all().update(show=False)
        for f in json.loads(self.factions):
            self.attacksfaction_set.filter(faction_id=int(f)).update(show=True)
            self.attacksplayer_set.filter(player_faction_id=int(f)).update(show=True)

        # self.fill = tsnow()
        self.save()

    def getMembersBreakdown(self, order=6):
        members = dict({})

        # outgoing
        attacks = self.attackreport_set.filter(defender_faction__in=json.loads(self.factions))
        for attack in attacks:
            # n = [0 leave, 1 mug, 2 hosp, 3 war, 4 win, 5 lost, 6 total]
            n = members[attack.attacker_id]["out"] if attack.attacker_id in members else [0, 0, 0, 0, 0, 0, 0]
            addOne = []
            if attack.result in ["Attacked", "Special"]:
                addOne.append(0)
                addOne.append(4)
            elif attack.result in ["Mugged"]:
                addOne.append(1)
                addOne.append(4)
            elif attack.result in ["Hospitalized"]:
                addOne.append(2)
                addOne.append(4)
            elif attack.result in ["Stalemate", "Assist", "Lost", "Timeout", "Escape"]:
                addOne.append(5)
            else:
                print(attack.result)

            if attack.war > 1:
                addOne.append(3)

            addOne.append(6)
            for i in addOne:
                n[i] = n[i] + 1
            members[attack.attacker_id] = {"name": attack.attacker_name, "out": n, "in": [0, 0, 0, 0, 0, 0, 0]}

        # incoming
        attacks = self.attackreport_set.filter(attacker_faction__in=json.loads(self.factions))
        for attack in attacks:
            # n = [0 leave, 1 mug, 2 hosp, 3 war, 4 win, 5 lost, 6 total]
            n = members[attack.defender_id]["in"] if attack.defender_id in members else [0, 0, 0, 0, 0, 0, 0]
            addOne = []
            if attack.result in ["Attacked", "Special"]:
                addOne.append(0)
                addOne.append(4)
            elif attack.result in ["Mugged"]:
                addOne.append(1)
                addOne.append(4)
            elif attack.result in ["Hospitalized"]:
                addOne.append(2)
                addOne.append(4)
            elif attack.result in ["Stalemate", "Assist", "Lost", "Timeout", "Escape"]:
                addOne.append(5)
            else:
                print(attack.result)

            if attack.war > 1:
                addOne.append(3)

            addOne.append(6)
            for i in addOne:
                n[i] = n[i] + 1
            if attack.defender_id in members:
                members[attack.defender_id]["in"] = n
            else:
                members[attack.defender_id] = {"name": attack.defender_name, "in": n, "out": [0, 0, 0, 0, 0, 0, 0]}

        type = "in" if order > 6 else "out"
        o1 = order % 7
        o2 = 0 if o1 == 6 else 6
        return sorted(members.items(), key=lambda x: (-x[1][type][o1], -x[1][type][o2]))

    def get_war(self):
        print(type(self.war))
        return json.loads(self.war)

class AttacksFaction(models.Model):
    report = models.ForeignKey(AttacksReport, on_delete=models.CASCADE)

    # faction_id_pk = models.IntegerField(default=0)

    faction_id = models.IntegerField(default=0)
    faction_name = models.CharField(default="faction_name", max_length=64, null=True, blank=True)

    hits = models.IntegerField(default=0)
    attacks = models.IntegerField(default=0)
    defends = models.IntegerField(default=0)
    attacked = models.IntegerField(default=0)

    show = models.BooleanField(default=False)

    # bulk manager
    objects = BulkManager()

    def __str__(self):
        return "{} [{}]: {} {} {} {}".format(self.faction_name, self.faction_id, self.hits, self.attacks, self.defends, self.attacked)


class AttacksPlayer(models.Model):
    report = models.ForeignKey(AttacksReport, on_delete=models.CASCADE)

    player_id = models.IntegerField(default=0)
    player_name = models.CharField(default="player_name", max_length=16, null=True, blank=True)
    player_faction_id = models.IntegerField(default=0)
    player_faction_name = models.CharField(default="faction_name", max_length=64, null=True, blank=True)

    hits = models.IntegerField(default=0)
    attacks = models.IntegerField(default=0)
    defends = models.IntegerField(default=0)
    attacked = models.IntegerField(default=0)

    show = models.BooleanField(default=False)

    # bulk manager
    objects = BulkManager()

    def __str__(self):
        return "{} [{}]: {} {} {} {}".format(self.player_name, self.player_id, self.hits, self.attacks, self.defends, self.attacked)


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
    respect = models.FloatField(default=0.0)
    respect_gain = models.FloatField(default=0.0)
    respect_lost = models.FloatField(default=0.0)
    raid = models.BooleanField(default=False)
    ranked_war = models.BooleanField(default=False)
    chain = models.IntegerField(default=0)
    code = models.SlugField(default="0", max_length=32)

    # mofifiers
    fair_fight = models.FloatField(default=0.0)
    war = models.IntegerField(default=0)
    retaliation = models.FloatField(default=0.0)
    group_attack = models.FloatField(default=0.0)
    overseas = models.FloatField(default=0.0)
    chain_bonus = models.FloatField(default=0.0)

    objects = BulkManager()

    def __str__(self):
        return "{} -> {}".format(self.attacker_factionname, self.defender_factionname)


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
    factions = models.TextField(default="[]")
    player_filter = models.IntegerField(default=0)
    filter = models.IntegerField(default=0)  # 0: no filters, 10: online, 01: hosp, 11: both
    revivesMade = models.IntegerField(default=0)
    revivesMadeSuccess = models.IntegerField(default=0)
    revivesReceived = models.IntegerField(default=0)
    revivesReceivedSuccess = models.IntegerField(default=0)
    include_failed = models.BooleanField(default=True)
    include_early = models.BooleanField(default=True)
    chance_filter = models.IntegerField(default=0)

    # share ID
    shareId = models.SlugField(default="", null=True, blank=True, max_length=32)

    def __str__(self):
        return format_html("{} revives [{}]".format(self.faction, self.pk))

    def getFilterExt(self):
        if self.filter == 1:
            return "H"
        elif self.filter == 10:
            return "O"
        elif self.filter == 11:
            return "B"
        else:
            return ""

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
        crontab_type = "crontabs_revives_live" if self.live else "crontabs_revives_report"
        if report is None or report.crontab not in getCrontabs(crontab_type):
            cn = {c: len(RevivesReport.objects.filter(crontab=c).only('crontab')) for c in getCrontabs(crontab_type)}
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
        tsl = self.start if lastRevive is None else max(lastRevive.timestamp, self.last)
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
            # self.revive_set.filter(timestamp__gt=weekAgo).delete()
            self.live = False
            self.state = -7
            self.save()
            return -7

        # add + 2 s to the endTS
        tse += 10

        # get existing revives (just the ids)
        revives = [r.tId for r in self.revive_set.all()]
        print("{} {} existing revives".format(self, len(revives)))

        # get the keys and init the attacks dict
        apiRevives = {}
        keys = faction.masterKeys.filter(useFact=True).order_by("lastPulled")
        nKeys = len(keys)

        if not keys:
            print("{} no key".format(self))
            self.computing = False
            self.crontab = 0
            self.revive_set.all().delete()
            self.state = -1
            self.save()
            return -1

        # loop over keys to get the attacks
        for i, key in enumerate(keys):
            print(f"{self} Key #{i}: {key}")

            # prevent cache response
            delay = tsnow() - self.update
            delay = min(tsnow() - faction.lastRevivesPulled, delay)
            if delay < 32:
                sleeptime = 32 - delay
                print("{} last update {}s ago, waiting {} for cache...".format(self, delay, sleeptime))
                time.sleep(sleeptime)

            # make call
            selection = "revives,timestamp&from={}&to={}".format(tsl - 1, tse)
            req = apiCall("faction", faction.tId, selection, key.value, verbose=False)
            key.reason = "Pull revives for report"
            key.lastPulled = tsnow()
            key.save()

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
            nowTS = tsnow()
            cache = abs(nowTS - tornTS)
            print("{} cache = {}s".format(self, cache))
            # in case cache
            if cache > CACHE_RESPONSE:
                print('{} probably cached response... (blank turn)'.format(self))
                self.state = -4
                self.save()
                return -4

            # add revive to global dictionnary
            n = 0
            for id, r in req["revives"].items():
                if id not in apiRevives:
                    apiRevives[id] = r
                    n += 1
                tsl = max(tsl, r["timestamp"])

            print(f'{self}\t adding {n} attacks')
            print(f'{self}\t last time {timestampToDate(tsl)}')
            if not n:
                print(f'{self}\t escape loop because no new revives')
                break

        # in case empty payload
        if not len(apiRevives):
            print('{} empty payload'.format(self))
            self.computing = False
            self.crontab = 0
            self.state = -5
            self.save()
            return -5

        print("{} {} revives from the API".format(self, len(apiRevives)))
        self.update = tsnow()
        faction.lastRevivesPulled = self.update
        faction.save()

        # add attacks
        newEntry = 0
        batch = Revive.objects.bulk_operation()
        for k, v in apiRevives.items():
            ts = int(v["timestamp"])

            # probably because of cache
            before = int(v["timestamp"]) - self.last
            after = int(v["timestamp"]) - tse
            if before < 0 or after > 0:
                print("{} /!\ ts out of bound: before = {} after = {}".format(self, before, after))

            # flatten last action
            v["target_last_action_status"] = v["target_last_action"].get("status", "Unknown")
            v["target_last_action_timestamp"] = v["target_last_action"].get("timestamp", 0)
            del v["target_last_action"]
            # convert restul to bool
            v["result"] = v["result"] == "success"

            batch.update_or_create(tId=int(k), report_id=int(self.id), defaults=v)
            newEntry += 1
            tsl = max(tsl, ts)
            if v["reviver_faction"] == faction.tId:
                self.revivesMade += 1
            else:
                self.revivesReceived += 1

        if batch.count():
            batch.run()
        self.last = tsl

        print("{} last  {}".format(self, timestampToDate(self.last)))
        print("{} progress ({})%".format(self, self.progress()))

        if not newEntry and len(apiRevives) > 1:
            print("{} no new entry with cache = {} [continue]".format(self, cache))
            self.state = -6
            self.save()
            return -6

        if len(apiRevives) < MINIMAL_API_ATTACKS_STOP and not self.live:
            print("{} no api entry for non live chain [stop]".format(self))
            self.computing = False
            self.crontab = 0
            self.state = 1
            self.last = self.end
            self.save()
            return 1

        if len(apiRevives) < 2 and self.live:
            print("{} no api entry for live chain [continue]".format(self))
            self.state = 2
            self.end = self.last
            self.save()
            return 2

        self.state = 3
        self.save()
        return 3

    def fillReport(self):
        print(f"[YATA {datestr()}] {self} fill report")
        allRevives = self.revive_set.filter(chance__gte=self.chance_filter)

        tmp = allRevives.filter(reviver_faction=self.faction.tId)
        self.revivesMade = tmp.count()
        self.revivesMadeSuccess = tmp.filter(result=True).count()

        tmp = allRevives.exclude(reviver_faction=self.faction.tId)
        self.revivesReceived = tmp.count()
        self.revivesReceivedSuccess = tmp.filter(result=True).count()

        print(f'[YATA {datestr()}] {self} include failed: {self.include_failed}')
        if not self.include_failed:
            allRevives = allRevives.exclude(result=False)

        print(f'[YATA {datestr()}] {self} include early: {self.include_early}')
        if not self.include_early:
            allRevives = allRevives.exclude(target_early_discharge=True)

        print(f"[YATA {datestr()}] {self} made {self.revivesMadeSuccess}/{self.revivesMade}")
        print(f"[YATA {datestr()}] {self} received {self.revivesReceivedSuccess}/{self.revivesReceived}")
        print(f"[YATA {datestr()}] {self} set players and factions counts")
        # create factions and players
        f_set = dict({})
        p_set = dict({})
        revives_count_types = ["revivesMade", "revivesMadeH", "revivesMadeO", "revivesMadeB",
                               "revivesReceived", "revivesReceivedH", "revivesReceivedO", "revivesReceivedB"]
        for revive in allRevives:

            online = 1 if revive.target_last_action_status in ["Online"] else 0
            hospitalized = 1 if revive.target_hospital_reason.split(" ")[0] in ["Hospitalized"] else 0
            both = 1 if (hospitalized and online) else 0
            success = revive.result

            # handle reviver faction
            if revive.reviver_faction in f_set:
                n = [f_set[revive.reviver_faction][k] for k in revives_count_types]
                n[0] = n[0] + 1
                n[1] = n[1] + hospitalized
                n[2] = n[2] + online
                n[3] = n[3] + both
                m = [f_set[revive.reviver_faction][f'{k}Success'] for k in revives_count_types]
                m[0] = m[0] + (1 * int(success))
                m[1] = m[1] + (hospitalized * int(success))
                m[2] = m[2] + (online * int(success))
                m[3] = m[3] + (both * int(success))
            else:
                n = [1, hospitalized, online, both, 0, 0, 0, 0]
                m = [1 * int(success), hospitalized * int(success), online * int(success), both * int(success), 0, 0, 0, 0]
            f_set[revive.reviver_faction] = {
                "faction_id": revive.reviver_faction, "faction_name": revive.reviver_factionname,
                "revivesMade": n[0], "revivesMadeH": n[1], "revivesMadeO": n[2], "revivesMadeB": n[3],
                "revivesReceived": n[4], "revivesReceivedH": n[5], "revivesReceivedO": n[6], "revivesReceivedB": n[7],
                "revivesMadeSuccess": m[0], "revivesMadeHSuccess": m[1], "revivesMadeOSuccess": m[2], "revivesMadeBSuccess": m[3],
                "revivesReceivedSuccess": m[4], "revivesReceivedHSuccess": m[5], "revivesReceivedOSuccess": m[6], "revivesReceivedBSuccess": m[7],
            }

            # handle target faction
            if revive.target_faction in f_set:
                n = [f_set[revive.target_faction][k] for k in revives_count_types]
                n[4] = n[4] + 1
                n[5] = n[5] + hospitalized
                n[6] = n[6] + online
                n[7] = n[7] + both
                m = [f_set[revive.target_faction][f'{k}Success'] for k in revives_count_types]
                m[4] = m[4] + (1 * int(success))
                m[5] = m[5] + (hospitalized * int(success))
                m[6] = m[6] + (online * int(success))
                m[7] = m[7] + (both * int(success))
            else:
                n = [0, 0, 0, 0, 1, hospitalized, online, both]
                m = [0, 0, 0, 0, 1 * int(success), hospitalized * int(success), online * int(success), both * int(success)]
            f_set[revive.target_faction] = {
                "faction_id": revive.target_faction, "faction_name": revive.target_factionname,
                "revivesMade": n[0], "revivesMadeH": n[1], "revivesMadeO": n[2], "revivesMadeB": n[3],
                "revivesReceived": n[4], "revivesReceivedH": n[5], "revivesReceivedO": n[6], "revivesReceivedB": n[7],
                "revivesMadeSuccess": m[0], "revivesMadeHSuccess": m[1], "revivesMadeOSuccess": m[2], "revivesMadeBSuccess": m[3],
                "revivesReceivedSuccess": m[4], "revivesReceivedHSuccess": m[5], "revivesReceivedOSuccess": m[6], "revivesReceivedBSuccess": m[7],
            }

            # handle reviver player
            if revive.reviver_id in p_set:
                n = [p_set[revive.reviver_id][k] for k in revives_count_types]
                n[0] = n[0] + 1
                n[1] = n[1] + hospitalized
                n[2] = n[2] + online
                n[3] = n[3] + both
                m = [p_set[revive.reviver_id][f'{k}Success'] for k in revives_count_types]
                m[0] = m[0] + (1 * int(success))
                m[1] = m[1] + (hospitalized * int(success))
                m[2] = m[2] + (online * int(success))
                m[3] = m[3] + (both * int(success))
            else:
                n = [1, hospitalized, online, both, 0, 0, 0, 0]
                m = [1 * int(success), hospitalized * int(success), online * int(success), both * int(success), 0, 0, 0, 0]
            p_set[revive.reviver_id] = {
                "player_id": revive.reviver_id, "player_name": revive.reviver_name,
                "player_faction_id": revive.reviver_faction, "player_faction_name": revive.reviver_factionname,
                "revivesMade": n[0], "revivesMadeH": n[1], "revivesMadeO": n[2], "revivesMadeB": n[3],
                "revivesReceived": n[4], "revivesReceivedH": n[5], "revivesReceivedO": n[6], "revivesReceivedB": n[7],
                "revivesMadeSuccess": m[0], "revivesMadeHSuccess": m[1], "revivesMadeOSuccess": m[2], "revivesMadeBSuccess": m[3],
                "revivesReceivedSuccess": m[4], "revivesReceivedHSuccess": m[5], "revivesReceivedOSuccess": m[6], "revivesReceivedBSuccess": m[7]
            }

            # handle defender player
            if revive.target_id in p_set:
                n = [p_set[revive.target_id][k] for k in revives_count_types]
                n[4] = n[4] + 1
                n[5] = n[5] + hospitalized
                n[6] = n[6] + online
                n[7] = n[7] + both
                m = [p_set[revive.target_id][f'{k}Success'] for k in revives_count_types]
                m[4] = m[4] + (1 * int(success))
                m[5] = m[5] + (hospitalized * int(success))
                m[6] = m[6] + (online * int(success))
                m[7] = m[7] + (both * int(success))
            else:
                n = [0, 0, 0, 0, 1, hospitalized, online, both]
                m = [0, 0, 0, 0, 1 * int(success), hospitalized * int(success), online * int(success), both * int(success)]
            p_set[revive.target_id] = {
                "player_id": revive.target_id, "player_name": revive.target_name,
                "player_faction_id": revive.target_faction, "player_faction_name": revive.target_factionname,
                "revivesMade": n[0], "revivesMadeH": n[1], "revivesMadeO": n[2], "revivesMadeB": n[3],
                "revivesReceived": n[4], "revivesReceivedH": n[5], "revivesReceivedO": n[6], "revivesReceivedB": n[7],
                "revivesMadeSuccess": m[0], "revivesMadeHSuccess": m[1], "revivesMadeOSuccess": m[2], "revivesMadeBSuccess": m[3],
                "revivesReceivedSuccess": m[4], "revivesReceivedHSuccess": m[5], "revivesReceivedOSuccess": m[6], "revivesReceivedBSuccess": m[7]
            }

        print(f"[YATA {datestr()}] {self} update factions")
        batch = RevivesFaction.objects.bulk_operation()
        for k, v in f_set.items():
            batch.update_or_create(report_id=self.id, faction_id=k, defaults=v)
        if batch.count():
            batch.run(batch_size=50)

        print(f"[YATA {datestr()}] {self} update players")
        batch = RevivesPlayer.objects.bulk_operation()
        for k, v in p_set.items():
            batch.update_or_create(report_id=self.id, player_id=k, defaults=v)
        if batch.count():
            batch.run(batch_size=50)

        # set show/hide
        print(f"[YATA {datestr()}] {self} show hide")
        self.revivesfaction_set.all().update(show=False)
        self.revivesplayer_set.all().update(show=False)
        self.revivesfaction_set.filter(faction_id__in=json.loads(self.factions)).update(show=True)
        self.revivesplayer_set.filter(player_faction_id__in=json.loads(self.factions)).update(show=True)

        self.save()


class RevivesFaction(models.Model):
    report = models.ForeignKey(RevivesReport, on_delete=models.CASCADE)

    faction_id = models.IntegerField(default=0)
    faction_name = models.CharField(default="faction_name", max_length=64, null=True, blank=True)

    revivesMade = models.IntegerField(default=0)
    revivesReceived = models.IntegerField(default=0)

    revivesMadeH = models.IntegerField(default=0)
    revivesMadeO = models.IntegerField(default=0)
    revivesMadeB = models.IntegerField(default=0)
    revivesReceivedH = models.IntegerField(default=0)
    revivesReceivedO = models.IntegerField(default=0)
    revivesReceivedB = models.IntegerField(default=0)

    revivesMadeSuccess = models.IntegerField(default=0)
    revivesReceivedSuccess = models.IntegerField(default=0)

    revivesMadeHSuccess = models.IntegerField(default=0)
    revivesMadeOSuccess = models.IntegerField(default=0)
    revivesMadeBSuccess = models.IntegerField(default=0)
    revivesReceivedHSuccess = models.IntegerField(default=0)
    revivesReceivedOSuccess = models.IntegerField(default=0)
    revivesReceivedBSuccess = models.IntegerField(default=0)

    show = models.BooleanField(default=False)

    # bulk manager
    objects = BulkManager()

    def __str__(self):
        return "{} [{}]: {} {}".format(self.faction_name, self.faction_id, self.revivesMade, self.revivesReceived)

    def revivesMadeDisp(self):
        if self.report.filter == 1:
            return f'{self.revivesMadeH:,d} | {self.revivesMadeHSuccess:,d} | {self.revivesMadeH - self.revivesMadeHSuccess:,d}'
        elif self.report.filter == 10:
            return f'{self.revivesMadeO:,d} | {self.revivesMadeOSuccess:,d} | {self.revivesMadeO - self.revivesMadeOSuccess:,d}'
        elif self.report.filter == 11:
            return f'{self.revivesMadeB:,d} | {self.revivesMadeBSuccess:,d} | {self.revivesMadeB - self.revivesMadeBSuccess:,d}'
        else:
            return f'{self.revivesMade:,d} | {self.revivesMadeSuccess:,d} | {self.revivesMade - self.revivesMadeSuccess:,d}'

    def revivesReceivedDisp(self):
        if self.report.filter == 1:
            return f'{self.revivesReceivedH:,d} | {self.revivesReceivedHSuccess:,d} | {self.revivesReceivedH - self.revivesReceivedHSuccess:,d}'
        elif self.report.filter == 10:
            return f'{self.revivesReceivedO:,d} | {self.revivesReceivedOSuccess:,d} | {self.revivesReceivedO - self.revivesReceivedOSuccess:,d}'
        elif self.report.filter == 11:
            return f'{self.revivesReceivedB:,d} | {self.revivesReceivedBSuccess:,d} | {self.revivesReceivedB - self.revivesReceivedBSuccess:,d}'
        else:
            return f'{self.revivesReceived:,d} | {self.revivesReceivedSuccess:,d} | {self.revivesReceived - self.revivesReceivedSuccess:,d}'


class RevivesPlayer(models.Model):
    report = models.ForeignKey(RevivesReport, on_delete=models.CASCADE)

    player_id = models.IntegerField(default=0)
    player_name = models.CharField(default="player_name", max_length=16, null=True, blank=True)
    player_faction_id = models.IntegerField(default=0)
    player_faction_name = models.CharField(default="faction_name", max_length=64, null=True, blank=True)

    revivesMade = models.IntegerField(default=0)
    revivesReceived = models.IntegerField(default=0)

    revivesMadeH = models.IntegerField(default=0)
    revivesMadeO = models.IntegerField(default=0)
    revivesMadeB = models.IntegerField(default=0)
    revivesReceivedH = models.IntegerField(default=0)
    revivesReceivedO = models.IntegerField(default=0)
    revivesReceivedB = models.IntegerField(default=0)

    revivesMadeSuccess = models.IntegerField(default=0)
    revivesReceivedSuccess = models.IntegerField(default=0)

    revivesMadeHSuccess = models.IntegerField(default=0)
    revivesMadeOSuccess = models.IntegerField(default=0)
    revivesMadeBSuccess = models.IntegerField(default=0)
    revivesReceivedHSuccess = models.IntegerField(default=0)
    revivesReceivedOSuccess = models.IntegerField(default=0)
    revivesReceivedBSuccess = models.IntegerField(default=0)

    show = models.BooleanField(default=False)

    # bulk manager
    objects = BulkManager()

    def __str__(self):
        return "{} [{}]: {} {}".format(self.player_name, self.player_id, self.revivesMade, self.revivesReceived)

    def revivesMadeDisp(self):
        if self.report.filter == 1:
            return f'{self.revivesMadeH:,d} | {self.revivesMadeHSuccess:,d} | {self.revivesMadeH - self.revivesMadeHSuccess:,d}'
        elif self.report.filter == 10:
            return f'{self.revivesMadeO:,d} | {self.revivesMadeOSuccess:,d} | {self.revivesMadeO - self.revivesMadeOSuccess:,d}'
        elif self.report.filter == 11:
            return f'{self.revivesMadeB:,d} | {self.revivesMadeBSuccess:,d} | {self.revivesMadeB - self.revivesMadeBSuccess:,d}'
        else:
            return f'{self.revivesMade:,d} | {self.revivesMadeSuccess:,d} | {self.revivesMade - self.revivesMadeSuccess:,d}'

    def revivesReceivedDisp(self):
        if self.report.filter == 1:
            return f'{self.revivesReceivedH:,d} | {self.revivesReceivedHSuccess:,d} | {self.revivesReceivedH - self.revivesReceivedHSuccess:,d}'
        elif self.report.filter == 10:
            return f'{self.revivesReceivedO:,d} | {self.revivesReceivedOSuccess:,d} | {self.revivesReceivedO - self.revivesReceivedOSuccess:,d}'
        elif self.report.filter == 11:
            return f'{self.revivesReceivedB:,d} | {self.revivesReceivedBSuccess:,d} | {self.revivesReceivedB - self.revivesReceivedBSuccess:,d}'
        else:
            return f'{self.revivesReceived:,d} | {self.revivesReceivedSuccess:,d} | {self.revivesReceived - self.revivesReceivedSuccess:,d}'


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
    target_last_action_status = models.CharField(default="Unknown", null=True, blank=True, max_length=16)
    target_last_action_timestamp = models.IntegerField(default=0)
    target_hospital_reason = models.CharField(default="Unknown", null=True, blank=True, max_length=128)
    target_early_discharge = models.BooleanField(default=False)
    chance = models.IntegerField(default=100)
    result = models.BooleanField(default=True)

    objects = BulkManager()

    def __str__(self):
        return "{} -> {}".format(self.reviver_factionname, self.target_factionname)


# Armory Report
class ArmoryReport(models.Model):
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    last = models.IntegerField(default=0)
    live = models.BooleanField(default=True)

    # information for computing
    computing = models.BooleanField(default=True)
    state = models.IntegerField(default=0)
    state_string = models.CharField(default="No reports", max_length=128)
    crontab = models.IntegerField(default=0)
    update = models.IntegerField(default=0)

    # report
    report = models.TextField(default="{}")
    news_ids = models.TextField(default="[]")
    n_news = models.IntegerField(default=0)

    def __str__(self):
        return format_html(f"{self.faction} armory report [{self.pk}]")

    def progress(self):
        end = self.end if self.end else tsnow()
        last = self.last if self.last else self.start
        total = max(end - self.start, 1)
        elaps = last - self.start
        return int((100 * elaps) // float(total))

    def elapsed(self):
        last = "{:.1f} days".format((self.last - self.start) / (60 * 60 * 24)) if self.last else "-"
        end = "{:.1f} days".format((self.end - self.start) / (60 * 60 * 24)) if self.end else "-"
        return "{} / {}".format(last, end)

    def assignCrontab(self):
        # check if already in a crontab
        report = self.faction.armoryreport_set.filter(computing=True).only("crontab").first()
        crontab_type = "crontabs_armory_live" if self.live else "crontabs_armory_report"
        if report is None or report.crontab not in getCrontabs(crontab_type):
            cn = {c: len(ArmoryReport.objects.filter(crontab=c).only('crontab')) for c in getCrontabs(crontab_type)}
            self.crontab = sorted(cn.items(), key=lambda x: x[1])[0][0]
        elif report is not None:
            self.crontab = report.crontab
        self.save()
        return self.crontab

    def displayCrontab(self):
        if self.crontab > 0:
            return "#{}".format(self.crontab)
        elif self.crontab == 0:
            return "No crontab assigned"
        else:
            return "Special crontab you lucky bastard..."

    def getReport(self):
        return json.loads(self.report)

    def updateReport(self):

        # set end of live report to now
        self.end = tsnow() if self.live else self.end
        self.last = max(self.last, self.start)

        # set shorcuts variables
        faction = self.faction
        tss = self.start
        tse = self.end
        tsl = self.last

        print(f"{self} live {self.live}")
        print(f"{self} start {timestampToDate(tss)} ({tss})")
        print(f"{self} last  {timestampToDate(tsl)} ({tsl})")
        print(f"{self} end   {timestampToDate(tse)} ({tse})")

        # add + 10 s to the endTS
        tse += 10

        # get current report and faction keys
        report = json.loads(self.report)
        news_ids = json.loads(self.news_ids)

        keys = faction.masterKeys.filter(useFact=True).order_by("lastPulled")
        nKeys = len(keys)

        if not keys:
            self.computing = False
            self.crontab = 0
            self.state = -1
            self.state_string = REPORTS_STATUS.get(self.state, f"Unknown code {self.state}")
            self.save()
            print(f"{self} {self.state_string}")
            return -1

        # loop over keys to get the news
        api_news = {}
        for i, key in enumerate(keys):
            print(f"{self} Key #{i}: {key}")

            # prevent cache response
            delay = tsnow() - self.update
            delay = min(tsnow() - faction.lastRevivesPulled, delay)
            if delay < 32:
                sleeptime = 32 - delay
                print(f"{self} last update {delay}s ago, waiting {sleeptime} for cache...")
                time.sleep(sleeptime)

            # make call
            selection = f"armorynews,fundsnews,timestamp&from={tsl - 1}&to={tse}"
            req = apiCall("faction", faction.tId, selection, key.value, verbose=True)
            key.reason = "Pull armory for report"
            key.lastPulled = tsnow()
            key.save()

            # in case there is an API error
            if "apiError" in req:
                print('{} api key error: {}'.format(self, req['apiError']))
                if req['apiErrorCode'] in API_CODE_DELETE:
                    print("{} --> deleting {}'s key from faction (blank turn)".format(self, key.player))
                    faction.delKey(key=key)
                    self.state = -2
                    self.state_string = REPORTS_STATUS.get(self.state, f"Unknown code {self.state}")
                    self.update = tsnow()
                    self.save()
                    print(f"{self} {self.state_string}")
                    return -2
                self.state = -3
                self.state_string = REPORTS_STATUS.get(self.state, f"Unknown code {self.state}")
                self.update = tsnow()
                self.save()
                print(f"{self} {self.state_string}")
                return -3

            # try to catch cache response
            tornTS = int(req["timestamp"])
            nowTS = tsnow()
            cache = abs(nowTS - tornTS)
            print("{} cache = {}s".format(self, cache))

            # in case cache
            if cache > CACHE_RESPONSE:
                self.state = -4
                self.state_string = REPORTS_STATUS.get(self.state, f"Unknown code {self.state}")
                self.update = tsnow()
                self.save()
                print(f"{self} {self.state_string}")
                return -4

            # add news to global dictionnary
            new_entries = 0
            new_funds = 0
            new_armory = 0
            # patch buggy API return empty [] instead of {}
            if len(req["armorynews"]) == 0:
                req["armorynews"] = {}
            if len(req["fundsnews"]) == 0:
                req["fundsnews"] = {}

            tsl_armory = tsl
            for id, r in dict(req["armorynews"]).items():
                if r["timestamp"] > tse:
                    print(f"{self}\t armory news {id} ignored because too recent")
                elif r["timestamp"] < tss:
                    print(f"{self}\t armory news {id} ignored because too old")
                elif id in news_ids:
                    # print(f"{self}\t armory news {id} ignored because already reported")
                    continue
                else:
                    api_news[id] = r
                    news_ids.append(id)
                    new_entries += 1
                    new_armory += 1
                    tsl_armory = max(tsl_armory, r["timestamp"])
                    # print(f'{self}\t news {id} new entry {timestampToDate(r["timestamp"])}')

            tsl_funds = tsl
            for id, r in dict(req["fundsnews"]).items():
                if r["timestamp"] > tse:
                    print(f"{self}\t funds news {id} ignored because too recent")
                elif r["timestamp"] < tss:
                    print(f"{self}\t funds news {id} ignored because too old")
                elif id in news_ids:
                    # print(f"{self}\t funds news {id} ignored because already reported")
                    continue
                else:
                    api_news[id] = r
                    news_ids.append(id)
                    new_entries += 1
                    new_funds += 1
                    tsl_funds = max(tsl_funds, r["timestamp"])
                    # print(f'{self}\t news {id} new entry {timestampToDate(r["timestamp"])}')

            print(f'{self}\t tsl_armory {timestampToDate(tsl_armory)} ({tsl_armory})')
            print(f'{self}\t tsl_funds {timestampToDate(tsl_funds)} ({tsl_funds})')

            if tsl_funds == tsl:
                print(f'{self}\t tsl_funds unchanged -> tsl = ts_armory')
                tsl = tsl_armory
            elif tsl_armory == tsl:
                print(f'{self}\t tsl_armory unchanged -> tsl = tsl_funds')
                tsl = tsl_funds
            else:
                print(f'{self}\t tsl_armory and ts_armory changed -> tsl = min(tsl_funds, tsl_armory)')
                tsl = min(tsl_funds, tsl_armory)

            print(f'{self}\t adding {new_entries} news ({new_armory} armory, {new_funds} funds)')
            print(f'{self}\t last time {timestampToDate(tsl)} ({tsl})')
            if not new_entries:
                print(f'{self}\t escape api key loop because no new news')
                break

        # update general information
        self.update = tsnow()
        self.last = tsl
        self.news_ids = json.dumps(news_ids)
        self.n_news = len(news_ids)
        faction.lastAttacksPulled = self.update
        faction.save()

        # debug
        # json.dump(api_news, open('api_news.json', 'w'))
        # json.dump(news_ids, open('news_ids.json', 'w'))
        # api_news = json.load(open('api_news.json', 'r'))
        # news_ids = json.load(open('news_ids.json', 'r'))

        print(f"{self} {len(api_news)} news from the API for a total of {len(news_ids)}")

        ITEM_TYPE = json.loads(BazaarData.objects.first().itemType)
        TRANSACTIONS_HANDLED = [
            "used",  # A member uses an item or a refill
            "deposited",  # A member deposits money, points or an item
            "filled",  # A member fills a blood bag
            "was"  # A member was given money
        ]
        CONVERT_TRANSACTIONS = {
            "used": "took",
            "was": "took",
            "deposited": "gave",
            "filled": "filled"
        }
        TRANSACTIONS_IGNORED = [
            "loaned",  # member loans an item
            "returned",  # member returns an item
            "retrieved",  # member retrieve an item from another member
            "gave",  # member gives an item to another member
            "opened",  # member opens a cache
            "adjusted"  # member adjusts vault balance of another member
        ]
        # update report
        for news in api_news.values():
            news_string = news["news"]
            news_timestamp = news["timestamp"]

            # get member ID
            m = re.search('XID=(\d)+', news_string)
            member_id = m[0].split("=")[1]
            member_id = m[0].split("=")[1]
            m = re.search(f'XID={member_id}"?>([A-Za-z0-9-_])+', news_string)
            member_name = m[0].split(">")[1]

            # get all info and clean html
            news_info = [cleanhtml(_) for _ in news_string.split("</a>")[1].replace("items.", "").split()]
            transaction_type = news_info.pop(0)  # used / deposit / filled

            if transaction_type in TRANSACTIONS_IGNORED: # ignored
                # print(f'{self} WARNING news transaction ignored: {news_string}')
                continue

            elif transaction_type not in TRANSACTIONS_HANDLED: # unkown
                print(f'{self} WARNING news transaction not handeled: {news_string}')
                continue

            else:
                # print(f'{self} WARNING news transaction handeled: {news_string}')
                pass

            # "news": "<a href = http://www.torn.com/profiles.php?XID=2000607>Kivou</a> was given $5,760,000,000 by <a href = http://www.torn.com/profiles.php?XID=517092>Karalynn</a>.",
            if news_info[-1] == "points":  # case: deposited 25 points
                n = news_info[0].replace(",", "")
                transaction_number = int(n)
                item = "point"

            elif news_info[0] == "given":  # case: was given $64,882,742,829 by <a href...
                n = news_info[1].replace("$", "").replace(",", "")
                if n.isdigit():
                    transaction_number = int(n)
                    item = "money"
                else:
                    continue


            elif news_info[0].isdigit():  # case: deposited 1 x Lawyer Business Card or gace
                transaction_number = int(news_info[0])
                item = " ".join(news_info[2:])

            elif news_info[0] == "one":  # case: one of the faction's Bottle of Beer
                transaction_number = 1
                item = " ".join(news_info[4:])

            elif news_info[0].replace("$", "").replace(",", "").isdigit():  # case: deposited $1,000
                transaction_number = int(news_info[0].replace("$", "").replace(",", ""))
                item = "money"

            else:
                print(f'{self} WARNING news item not known: {news_string}')
                continue

            # merge blood bags
            if item == "Empty Blood Bag" and transaction_type == "filled":
                item = "Blood Bag"
            elif item[:9] == "Blood Bag":
                item = "Blood Bag"
            elif item == "the faction's points to refill their energy.":
                item = "point"

            # get item type
            fake_types = {"point": "Points", "money": "$"}
            item_type = dict(ITEM_TYPE, **fake_types).get(item, "Unknown")

            # print(f'type: {item_type:<10} name: {member_name:<16} [{member_id:>10}] transaction: {transaction_type:<10} number: {transaction_number:>5} item: {item}')

            if item_type == "Unknown":
                print(f'{self} item type not known: {news_string} {item}')
                # continue

            # fill report
            if item_type not in report:
                report[item_type] = {}

            if item not in report[item_type]:
                report[item_type][item] = {}

            if member_id not in report[item_type][item]:
                report[item_type][item][member_id] = {CONVERT_TRANSACTIONS[k]: 0 for k in TRANSACTIONS_HANDLED}
                report[item_type][item][member_id]["name"] = member_name
                report[item_type][item][member_id]["last"] = news_timestamp
                report[item_type][item][member_id]["first"] = news_timestamp

            report[item_type][item][member_id][CONVERT_TRANSACTIONS[transaction_type]] += transaction_number
            report[item_type][item][member_id]["last"] = max(report[item_type][item][member_id]["last"], news_timestamp)
            report[item_type][item][member_id]["first"] = min(report[item_type][item][member_id]["first"], news_timestamp)

        # save report
        self.report = json.dumps(report)
        # for item_type, items in report.items():
        #     print(item_type)
        #     for item, members in items.items():
        #         print(f'\t{item}')
        #         for member_id, transaction in members.items():
        #             print(f'\t\t{member_id:>9}: {transaction}')


        # check if not running for too long
        if self.last - self.start > (HISTORY_TIMES.get(faction.armoryHist)):
            self.computing = False
            self.crontab = 0
            self.live = False
            self.state = -5
            self.state_string = REPORTS_STATUS.get(self.state, f"Unknown code {self.state}")
            self.save()
            print(f"{self} {self.state_string}")
            return -5

        # no new news
        if not len(api_news):
            if self.live:
                print(f"{self} no api entry for live chain [continue]")
                self.state = 2
                self.state_string = REPORTS_STATUS.get(self.state, f"Unknown code {self.state}")
                self.end = self.last
                self.save()
                print(f"{self} {self.state_string}")
                return 2
            else:
                print(f"{self} no api entry for non live report [stop]")
                self.computing = False
                self.crontab = 0
                self.state = 1
                self.state_string = REPORTS_STATUS.get(self.state, f"Unknown code {self.state}")
                self.last = self.end
                self.save()
                print(f"{self} {self.state_string}")
                return 1

        self.state = 3
        self.state_string = REPORTS_STATUS.get(self.state, f"Unknown code {self.state}")
        print(f"{self} {self.state_string}")
        self.save()
        return 3


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
    slots = models.IntegerField(default=0)
    daily_respect = models.IntegerField(default=0)
    faction = models.IntegerField(default=0)
    coordinate_x = models.FloatField(default=0)
    coordinate_y = models.FloatField(default=0)
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

    # war
    war = models.BooleanField(default=False)
    assaulting_faction = models.IntegerField(default=0)
    # assaulting_faction_name = models.CharField(default="Faction", max_length=64)
    defending_faction = models.IntegerField(default=0)
    # defending_faction_name = models.CharField(default="Faction", max_length=64)
    started = models.IntegerField(default=0)
    ends = models.IntegerField(default=0)

    def __str__(self):
        return "Racket {} [{}]".format(self.tId, self.faction)


# Faction data
class FactionData(models.Model):
    territoryUpda = models.IntegerField(default=0)
    crontabs = models.TextField(default="[1,2,3]")
    crontabs_chain_live = models.TextField(default="[1,2,3,4]")
    crontabs_chain_report = models.TextField(default="[5]")
    crontabs_attacks_live = models.TextField(default="[1,2]")
    crontabs_attacks_report = models.TextField(default="[3]")
    crontabs_revives_live = models.TextField(default="[1]")
    crontabs_revives_report = models.TextField(default="[2]")
    crontabs_armory_live = models.TextField(default="[1]")
    crontabs_armory_report = models.TextField(default="[2]")
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


class Event(models.Model):
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)

    timestamp = models.IntegerField(default=0)
    title = models.CharField(default="Title", max_length=64)
    description = models.CharField(default="Short description", max_length=256, null=True, blank=True)
    stack = models.BooleanField(default=False)
    reset = models.BooleanField(default=False)

    def __str__(self):
        return format_html("{} event {}".format(self.faction, self.title))


class Crimes(models.Model):
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)

    tId = models.IntegerField(default=0)
    crime_id = models.IntegerField(default=0)
    crime_name = models.CharField(default="Crime Name", max_length=64)
    time_started = models.IntegerField(default=0)
    time_ready = models.IntegerField(default=0)
    time_left = models.IntegerField(default=0)
    time_completed = models.IntegerField(default=0)
    initiated_by = models.IntegerField(default=0)
    planned_by = models.IntegerField(default=0)
    money_gain = models.IntegerField(default=0)
    respect_gain = models.IntegerField(default=0)
    initiated = models.BooleanField(default=0)
    success = models.BooleanField(default=0)

    # custom
    participants = models.CharField(default="[]", max_length=512)
    team_id = models.IntegerField(default=0)
    ready = models.BooleanField(default=0)

    objects = BulkManager()

    def __str__(self):
        return format_html("{} {} [{}]".format(self.faction, self.crime_name, self.tId))

    def get_initiated_by(self):
        member = self.faction.member_set.filter(tId=self.initiated_by).first()
        if member is None:
            return "Player", self.initiated_by
        else:
            return member.name, self.initiated_by

    def get_planned_by(self):
        member = self.faction.member_set.filter(tId=self.planned_by).first()
        if member is None:
            return "Player", self.planned_by
        else:
            return member.name, self.planned_by

    def get_participants(self):
        participants = []
        for id in json.loads(self.participants):
            member = self.faction.member_set.filter(tId=int(id)).first()
            if member is None:
                name = "Player"
                nnb = 0
                arson = 0
                rank = 0
            else:
                name = member.name
                nnb = member.nnb
                arson = member.arson
                rank = member.crimesRank
            participants.append([id, name, nnb, arson, rank])
        return participants

    def get_team_id(self):
        import hashlib
        h = hash(tuple(sorted([p[0] for p in self.get_participants()])))
        return int(hashlib.sha256(str(h).encode("utf-8")).hexdigest(), 16) % 10**8


# Spy database
class SpyDatabase(models.Model):
    master_id = models.IntegerField(default=0)
    factions = models.ManyToManyField(Faction)
    name = models.CharField(default="My spy database", max_length=64)
    secret = models.CharField(default="x", max_length=16)
    n_spies = models.IntegerField(default=0)
    update = models.IntegerField(default=0)
    use_api = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} [{self.pk}]'

    def change_name(self):
        from xkcdpass import xkcd_password as xp
        wordfile = xp.locate_wordfile()
        words = xp.generate_wordlist(wordfile=wordfile, min_length=3, max_length=6)
        self.name = xp.generate_xkcdpassword(words, acrostic="torn")
        self.save()

    def get_master_name(self):
        return self.factions.filter(tId=self.master_id).first().name

    def change_secret(self):
        from xkcdpass import xkcd_password as xp
        self.secret = randomSlug(length=16)
        self.save()

    def updateSpies(self, payload=None):
        from faction.functions import optimize_spies

        # get old spies
        all_spies = self.getSpies(cc=True)

        new_spies = {}
        if payload is None and self.use_api:

            # get all factions
            for faction in self.factions.all():
                print(f'{self} {faction}')
                key = faction.getKey()
                if key is None:
                    continue

                req = apiCall("faction", faction.tId, "reports", key.value, verbose=True)
                key.reason = "Update spies"
                key.lastPulled = tsnow()
                key.save()

                if "apiError" in req:
                    print(f'{self} {req["apiError"]}'.format(self, req['apiError']))
                    if req['apiErrorCode'] in API_CODE_DELETE:
                        faction.delKey(key=key)
                    continue

                for v in req["reports"]:

                    # ignore non stats reports
                    if v["type"] != "stats":
                        continue

                    # ignore empty reports
                    if v["report"] is None:
                        continue

                    # refactor dictionnary
                    strength = v["report"].get("strength", -1)
                    speed = v["report"].get("speed", -1)
                    defense = v["report"].get("defense", -1)
                    dexterity = v["report"].get("dexterity", -1)
                    total = v["report"].get("total", -1)
                    tmp = {
                        "strength": strength,
                        "speed": speed,
                        "defense": defense,
                        "dexterity": dexterity,
                        "total": total,
                        "strength_timestamp": v["timestamp"] if strength + 1 else 0,
                        "speed_timestamp": v["timestamp"] if speed + 1 else 0,
                        "defense_timestamp": v["timestamp"] if defense + 1 else 0,
                        "dexterity_timestamp": v["timestamp"] if dexterity + 1 else 0,
                        "total_timestamp": v["timestamp"] if total + 1 else 0,
                    }
                    new_spies[v["target"]] = optimize_spies(tmp, spy_2=new_spies.get(v["target"], False))

            print(f'{self} Spies from API: {len(new_spies)}')

        elif payload is not None:
            new_spies = {}
            for target_id, spy in payload.items():
                new_spies[target_id] = optimize_spies(spy, spy_2=new_spies.get(target_id, False))
            print(f'{self} Spies from imports: {len(new_spies)}')


        # compare old and new
        batch = Spy.objects.bulk_operation()
        for target_id, new_spy in new_spies.items():
            old_spy = all_spies.get(target_id, False)
            opt_spy = optimize_spies(new_spy, old_spy)

            # if not in databse -> update_or_create
            if not old_spy or new_spy != old_spy:
                batch.update_or_create(database_id=self.pk, target_id=target_id, defaults=opt_spy)

            # add to all spies for cache
            all_spies[target_id] = opt_spy

        print(f'{self} batch size: {batch.count()}')
        if batch.count():
            batch.run(batch_size=100)

        self.n_spies = len(all_spies)
        self.update = int(time.time())
        self.save()

        # set new cache
        cache.set(f"spy-db-{self.secret}", all_spies, 3600)

        return all_spies

    def getSpies(self, cc=False):
        all_spies = cache.get(f"spy-db-{self.secret}")
        if all_spies is None or cc or settings.DEBUG:
            print(f'[getSpies] database cached: no')
            all_spies = {}
            for spy in self.spy_set.all():
                all_spies[spy.target_id] = spy.dictionnary()
            cache.set(f"spy-db-{self.secret}", all_spies, 3600)
        else:
            print(f'[getSpies] database cached: yes')

        return all_spies


# Spies
class Spy(models.Model):
    database = models.ForeignKey(SpyDatabase, on_delete=models.CASCADE)

    # direct report data
    target_id = models.IntegerField(default=0, db_index=True)
    strength = models.BigIntegerField(default=0)
    speed = models.BigIntegerField(default=0)
    defense = models.BigIntegerField(default=0)
    dexterity = models.BigIntegerField(default=0)
    total = models.BigIntegerField(default=0)
    strength_timestamp = models.IntegerField(default=0)
    speed_timestamp = models.IntegerField(default=0)
    defense_timestamp = models.IntegerField(default=0)
    dexterity_timestamp = models.IntegerField(default=0)
    total_timestamp = models.IntegerField(default=0)
    update = models.IntegerField(default=0)

    # extra report data
    target_name = models.CharField(default="Player", max_length=32)
    target_faction_name = models.CharField(default="Faction", max_length=64)
    target_faction_id = models.IntegerField(default=0)

    # bulk manager
    objects = BulkManager()

    def __str__(self):
        return f'Spy {self.target_name} [{self.target_id}]'


    def dictionnary(self):
        v = {
            "strength": self.strength,
            "speed": self.speed,
            "defense": self.defense,
            "dexterity": self.dexterity,
            "total": self.total,
            "strength_timestamp": self.strength_timestamp,
            "speed_timestamp": self.speed_timestamp,
            "defense_timestamp": self.defense_timestamp,
            "dexterity_timestamp": self.dexterity_timestamp,
            "total_timestamp": self.total_timestamp,
            "update": self.update,
            "target_name": self.target_name,
            "target_faction_name": self.target_faction_name,
            "target_faction_id": self.target_faction_id
        }
        return v
