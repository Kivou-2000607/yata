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
import numpy

from yata.handy import apiCall
from yata.handy import tsnow
from yata.handy import isProxyKey
# from awards.functions import updatePlayerAwards
# from faction.models import Faction
# from awards.models import AwardsData


SECTION_CHOICES = (
    ('B', 'bazaar'),
    ('F', 'faction'),
    ('T', 'target'),
    ('A', 'awards'),
    ('S', 'stock'),
    ('C', 'company'),
    ('L', 'loot'))


class Player(models.Model):
    # user information: basic
    tId = models.IntegerField(default=4, unique=True)
    name = models.CharField(default="Duke", max_length=200)
    # apikey = models.CharField(default="AAAA", max_length=16)

    # BooleanField states
    active = models.BooleanField(default=True)
    validKey = models.BooleanField(default=True)

    # user information: faction
    factionId = models.IntegerField(default=0)
    factionAA = models.BooleanField(default=False)
    factionNa = models.CharField(default="My Faction", max_length=64)

    # company
    companyId = models.IntegerField(default=0)
    companyTy = models.IntegerField(default=0)
    companyDi = models.BooleanField(default=False)
    companyNa = models.CharField(default="My Company", max_length=64)
    wint = models.IntegerField(default=0)
    wend = models.IntegerField(default=0)
    wman = models.IntegerField(default=0)

    # user last update
    lastUpdateTS = models.IntegerField(default=0)
    lastActionTS = models.IntegerField(default=0)

    # info for chain APP
    chainInfo = models.CharField(default="N/A", max_length=255)
    chainJson = models.TextField(default="{}")
    chainUpda = models.IntegerField(default=0)

    # info for target APP
    targetInfo = models.CharField(default="N/A", max_length=255)
    attacksUpda = models.IntegerField(default=0)
    revivesUpda = models.IntegerField(default=0)

    # info for target APP
    bazaarInfo = models.CharField(default="N/A", max_length=255)
    bazaarJson = models.TextField(default="{}")
    bazaarUpda = models.IntegerField(default=0)

    # info for awards APP
    # awardsInfo = models.CharField(default="N/A", max_length=255)
    # awardsJson = models.TextField(default="{}")
    awardsUpda = models.IntegerField(default=0)
    # awardsRank = models.IntegerField(default=99999)
    awardsScor = models.IntegerField(default=0)  # int(10000 x score in %)
    awardsNumb = models.IntegerField(default=0)  # number of awards
    awardsPinn = models.CharField(default="[]", max_length=32)

    # info for stocks APP
    stocksInfo = models.CharField(default="N/A", max_length=255)
    stocksJson = models.TextField(default="{}")
    stocksUpda = models.IntegerField(default=0)

    # discord id and permission to give the bot the right to pull information
    dId = models.BigIntegerField(default=0)
    # botPerm = models.BooleanField(default=False)
    activateNotifications = models.BooleanField(default=False)
    notifications = models.TextField(default="{}")

    def __str__(self):
        return "{} [{}]".format(self.name, self.tId)

    def nameAligned(self):
        return "{:15} [{:07}]".format(self.name, self.tId)

    def getSpinner(self):
        spinner = Spinner.objects.filter(factionId=self.factionId).first()
        return "" if (spinner is None or spinner.spinner is None) else "-{}".format(spinner.spinner)

    def getKey(self, value=True):
        key = self.key_set.first()
        if key is None:
            return False
        else:
            return key.value if value else key

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

    def usingProxyKey(self):
        key = self.getKey()
        # test in case getKey return False
        if isinstance(key, str):
            return isProxyKey(self.getKey())
        else:
            False

    def getAwards(self, userInfo=dict({}), force=False):
        from awards.models import AwardsData
        from awards.functions import AWARDS_CAT
        from awards.functions import createAwards

        # get torn awards
        awardsTorn = AwardsData.objects.first().loadAPICall()
        error = False

        if self.tId > 0:

            if not len(userInfo):
                dbInfo = self.tmpreq_set.filter(type="awards").first()
                if dbInfo is not None:
                    userInfo = json.loads(dbInfo.req)

                else:
                    userInfo = dict({})
                    error = {'apiError': "Your data can't be found in the database."}

            if not len(userInfo) or force:
                req = apiCall('user', '', 'personalstats,crimes,education,battlestats,workstats,perks,gym,networth,merits,profile,medals,honors,icons,bars,weaponexp,hof', self.getKey())
                if 'apiError' not in req:
                    self.awardsUpda = tsnow()
                    defaults = {"req": json.dumps(req), "timestamp": tsnow()}
                    try:
                        self.tmpreq_set.update_or_create(type="awards", defaults=defaults)
                    except BaseException as e:
                        self.tmpreq_set.filter(type="awards").delete()
                        self.tmpreq_set.update_or_create(type="awards", defaults=defaults)

                    userInfo = req
                    error = False

                else:
                    error = req

        medals = awardsTorn["medals"]
        honors = awardsTorn["honors"]
        remove = [k for k, v in honors.items() if v["type"] == 1]
        for k in remove:
            del honors[k]
        myMedals = userInfo.get("medals_awarded", [])
        myHonors = userInfo.get("honors_awarded", [])

        awards = dict()
        summaryByType = dict({})
        for type in AWARDS_CAT:
            awardsTmp, awardsSummary = createAwards(awardsTorn, userInfo, type)
            summaryByType[type.title()] = awardsSummary["All awards"]
            awards.update(awardsTmp)

        # get pinned
        pinnedAwards = {k: dict({}) for k in json.loads(self.awardsPinn)}

        # delete completed pinned awared
        todel = []
        for aid in pinnedAwards:
            if aid[0] == "m" and aid[2:].isdigit() and int(aid[2:]) in myMedals:
                todel.append(aid)
            if aid[0] == "h" and aid[2:].isdigit() and int(aid[2:]) in myHonors:
                todel.append(aid)
        for aid in todel:
            del pinnedAwards[aid]
        self.awardsPinn = json.dumps([k for k in pinnedAwards])
        i = len(pinnedAwards)
        for type, awardsTmp in awards.items():
            for id in pinnedAwards:
                if id in awardsTmp:
                    pinnedAwards[id] = awardsTmp[id]
                    i -= 1
            if not i:
                break

        summaryByType["AllAwards"] = {"nAwarded": len(myHonors) + len(myMedals), "nAwards": len(honors) + len(medals)}
        summaryByType["AllHonors"] = {"nAwarded": len(myHonors), "nAwards": len(honors)}
        summaryByType["AllMedals"] = {"nAwarded": len(myMedals), "nAwards": len(medals)}

        rScorePerso = 0.0
        for k, v in awardsTorn["honors"].items():
            if v.get("achieve", 0) == 1:
                rScorePerso += v.get("rScore", 0)
        for k, v in awardsTorn["medals"].items():
            if v.get("achieve", 0) == 1:
                rScorePerso += v.get("rScore", 0)

        awardsPlayer = {"userInfo": userInfo,
                        "awards": awards,
                        "pinnedAwards": pinnedAwards,
                        "summaryByType": dict({k: v for k, v in sorted(summaryByType.items(), key=lambda x: x[1]['nAwarded'], reverse=True)})}

        if self.tId > 0 and not error:
            self.awardsScor = int(rScorePerso * 10000)
            self.awardsNumb = len(myMedals) + len(myHonors)
            self.save()

        return awardsPlayer, awardsTorn, error

    def awardsInfo(self):
        return "{:.4f}".format(self.awardsScor / 10000.)

    def getMerits(self, req=None, init=False):
        if req is None:
            return dict({})

        merits = dict({})

        for k, v in req.items():
            if isinstance(v, list):
                merits[k] = {"level": v[0], "fix": v[1]}
            else:
                merits[k] = {"level": v, "fix": v}
            if k == "Nerve Bar":
                merits[k]["description"] = ["Increases maximum nerve bar by", 1, "", " points."]
            elif k == "Critical Hit Rate":
                merits[k]["description"] = ["Increases critical hit rate by", 1, "%", "."]
            elif k == "Life Points":
                merits[k]["description"] = ["Constantly modifies life by", 5, "%", "."]
            elif k == "Crime Experience":
                merits[k]["description"] = ["Increases crime success ability by", 3, "%", "."]
            elif k == "Education Length":
                merits[k]["description"] = ["Decreases education course length by", 2, "%", "."]
            elif k == "Awareness":
                merits[k]["description"] = ["Increases ability to find items.", 0, "", ""]
            elif k == "Bank Interest":
                merits[k]["description"] = ["Increases bank interest by", 5, "%", "."]
            elif k == "Masterful Looting":
                merits[k]["description"] = ["Increases money gained from mugging by", 5, "%", "."]
            elif k == "Stealth":
                merits[k]["description"] = ["Increases ability to do stealth attacks.", 0, "", "."]
            elif k == "Hospitalizing":
                merits[k]["description"] = ["Increases time when hospitalizing people by", 10, "", " minutes."]
            elif k in ["Brawn", "Protection", "Sharpness", "Evasion"]:
                b = {"Brawn": "strength", "Protection": "defense", "Evasion": "dexterity", "Sharpness": "speed"}
                merits[k]["description"] = ["Passive bonus of", 3, "%", " in {}.".format(b.get(k))]
            elif k.split(" ")[-1] == "Mastery":
                merits[k]["description"] = ["Increases damage and accuracy of {}".format(k.replace(" Mastery", "").lower()), 0.2, "", " in accuracy and damage."]

        return merits


    def getPersonalstats(self, req=None):
        from player.personalstats_dic import d as personalstats_dic
        if req is None:
            return dict({})

        personnalstats = dict({})

        for k, v in req.items():
            s = personalstats_dic.get(k, {"category": "Unkown", "sub": "default", "type": "integer", "name": k})
            if s["category"] not in personnalstats:
                personnalstats[s["category"]] = [[], dict({})]
            if s["sub"] == "default":
                personnalstats[s["category"]][0].append([s["name"], v, s["type"]])
            else:
                if s["sub"] not in personnalstats[s["category"]][1]:
                    personnalstats[s["category"]][1][s["sub"]] = []
                personnalstats[s["category"]][1][s["sub"]].append([s["name"], v, s["type"]])

            if s["category"] == "Unkown":
                print(k, v)

        return personnalstats

# class News(models.Model):
#     player = models.ManyToManyField(Player, blank=True)
#     type = models.CharField(default="Info", max_length=16)
#     text = models.TextField()
#     authorId = models.IntegerField(default=2000607)  # hopefully it will be relevent not to put this as default some day...
#     authorName = models.CharField(default="Kivou", max_length=32)
#     date = models.DateTimeField(default=timezone.now)
#
#     def __str__(self):
#         return "{} of {:%Y/%M/%d} by {}".format(self.type, self.date, self.authorName)
#
#     def read(self):
#         return len(self.player.all())


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
    uidBan = models.TextField(default="[]")

    def updateNumberOfPlayers(self):
        players = Player.objects.only("tId", "active", "validKey", "lastActionTS").exclude(tId=-1)

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
    value = models.SlugField(default="aaaa", max_length=32)  # key
    lastPulled = models.IntegerField(default=0)  # ts when last pulled
    reason = models.CharField(default="-", max_length=64)  # reason why it was pulled

    # player can decide to tell YATA not use their key
    useSelf = models.BooleanField(default=True)
    useFact = models.BooleanField(default=True)

    def __str__(self):
        return "Key of {}".format(self.player)


class Error(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)  # player
    timestamp = models.IntegerField(default=0)
    short_error = models.CharField(default="-", max_length=128)
    long_error = models.TextField(default="-")
    fixed = models.BooleanField(default=False)


class TmpReq(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)  # player
    timestamp = models.IntegerField(default=0)
    type = models.CharField(default="None", max_length=16)
    req = models.TextField(default="{}")


class Spinner(models.Model):
    factionId = models.IntegerField(default=0)
    spinner = models.CharField(default="", max_length=64, null=True, blank=True)


# class Gym(models.Model):
#     timestamp = models.IntegerField(default=0)
#
#     # stat
#     stat_type = models.CharField(default="?", max_length=16)
#     stat_before = models.BigIntegerField(default=0)
#     stat_after = models.BigIntegerField(default=0)
#
#     # energy
#     energy_used = models.IntegerField(default=0)
#
#     # happy
#     happy_before = models.IntegerField(default=0)
#     happy_after = models.IntegerField(default=0)
#
#     # gym
#     gym_id = models.IntegerField(default=1)
#     gym_dot = models.IntegerField(default=0)
#
#     # perks
#     perks_faction = models.IntegerField(default=0)
#     perks_property = models.IntegerField(default=0)
#     perks_education = models.IntegerField(default=0)
#     perks_book = models.IntegerField(default=0)
#     perks_company = models.IntegerField(default=0)

class TrainFull(models.Model):
    # for debug
    id_key = models.CharField(default="x", max_length=32)
    timestamp = models.IntegerField(default=0)
    time_diff = models.IntegerField(default=0)

    # happy
    happy_before = models.IntegerField(default=0)
    happy_after = models.IntegerField(default=0)
    happy_delta = models.IntegerField(default=0)

    # energy
    energy_used = models.IntegerField(default=0)
    single_train = models.IntegerField(default=False)

    # stat
    stat_type = models.CharField(default="None", max_length=16)
    stat_before = models.FloatField(default=0.0)
    stat_after = models.FloatField(default=0.0)
    stat_delta = models.FloatField(default=0.0)

    # gym
    gym_id = models.IntegerField(default=1)
    gym_dot = models.IntegerField(default=0)

    # gains perks
    perks_faction = models.IntegerField(default=0)
    perks_property = models.IntegerField(default=0)
    perks_education_stat = models.IntegerField(default=0)
    perks_education_all = models.IntegerField(default=0)
    perks_company = models.IntegerField(default=0)
    perks_company_happy_red = models.IntegerField(default=0)

    # books
    perks_gym_book = models.IntegerField(default=0)
    perks_happy_book = models.IntegerField(default=0)

    # error
    error = models.FloatField(default=0.0)

    # tmp for debug
    req = models.TextField(default="{}")

    def stat_before_cap(self):
        return min(self.stat_before, 50000000)

    def stat_after_cap(self):
        return min(self.stat_after, 50000000)

    def happy(self):
        return self.happy_before

    def bonus(self, type="x"):
        if type == "+":
            perks_list = [self.perks_faction, self.perks_property, self.perks_education_stat + self.perks_education_all, self.perks_company, self.perks_gym_book]
        else:
            perks_list = [self.perks_faction, self.perks_property, self.perks_education_stat, self.perks_education_all, self.perks_company, self.perks_gym_book]
        b_perks = [1 + p / 100. for p in perks_list]
        return numpy.prod(b_perks) - 1.

    def gym(self):
        return self.gym_dot / 10.

    def vladar(self):
        # coefficients
        a = 0.0000003480061091
        b = 250.
        c = 0.000003091619094
        d = 0.0000682775184551527
        e = -0.0301431777

        # states coefficients
        alpha = (a * numpy.log(self.happy() + b) + c) * (1. + self.bonus()) * self.gym()
        beta = (d * (self.happy() + b) + e) * (1. + self.bonus()) * self.gym()

        # stat cap
        stat_cap = min(self.stat_before, 50000000.0)

        return (alpha * stat_cap + beta) * self.energy_used

    def vladar_diff(self):
        return self.stat_delta - self.vladar()

    def normalized_gain(self, type="x"):
        return self.stat_delta / (self.gym() * (1. + self.bonus(type=type)) * float(self.energy_used))

    def current(self):
        # stat cap
        stat_cap = min(self.stat_before, 50000000.0)

        # normalization
        norm = (1. + self.bonus()) * self.gym() * self.energy_used / 200000.
        happy_func = stat_cap * numpy.round(1 + 0.07 * numpy.round(numpy.log(1. + self.happy() / 250.), decimals=4), decimals=4) + 8 * numpy.power(self.happy(), 1.05)
        return happy_func * norm

    def current_diff(self):
        return self.stat_delta - self.current()

    def set_single_train(self):
        from yata.gyms import gyms
        self.single_train = gyms.get(self.gym_id, {"energy": 0})["energy"] == self.energy_used
        self.save()

    def set_error(self):
        self.error = abs(self.current_diff())
        self.save()
