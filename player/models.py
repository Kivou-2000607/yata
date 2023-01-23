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

import json
import time

from django.core.cache import cache
from django.db import models

from yata.handy import apiCall, tsnow

SECTION_CHOICES = (
    ("all", "all"),
    ("player", "player"),
    ("bazaar", "bazaar"),
    ("faction", "faction"),
    ("target", "target"),
    ("awards", "awards"),
    ("stock", "stock"),
    ("company", "company"),
    ("loot", "loot"),
)

LEVEL_CHOICES = (("notice", "notice"), ("warning", "warning"), ("error", "error"))


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
    bazaarList = models.TextField(default="[]")

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

    # key access level
    # -1: no keys
    # 0: key error or unkown level
    # 1: Public
    # 2: Minimal
    # 3: Limited
    # 4: Full
    key_level = models.IntegerField(default=0)
    key_last_code = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        # add to cache
        cache.set(f"player-by-id-{self.tId}", self, 3600)
        super().save(*args, **kwargs)

    def __str__(self):
        return "{} [{}]".format(self.name, self.tId)

    def nameAligned(self):
        return "{:15} [{:07}]".format(self.name, self.tId)

    def getKey(self, value=True):
        key = self.key_set.first()
        if key is None:
            return False
        else:
            return key.value if value else key

    def addKey(self, key):
        print("[player.addKey] start")
        playerKey = self.key_set.first()
        print(f"[player.addKey] get key {playerKey}")
        if playerKey is None:
            self.key_set.create(value=key, tId=self.tId)
        else:
            playerKey.value = key
            playerKey.save()
        # temporary for the bot...
        self.apikey = key
        self.updateKeyLevel()
        self.save()
        return

    def updateKeyLevel(self):
        # key levels
        # -2: not valid key because of inactivity
        # -1: key deleted because of major error
        # 0: Unkown or custom key level
        # 1: Public
        # 2: Minimal
        # 3: Limited
        # 4: Full Access

        # get API key
        key = self.key_set.first()

        if not key:
            print(f"[updateKeyLevel] {self}: no keys found")
            self.key_level = -1
            self.validKey = False
            self.save()
            return

        # get api Key Info
        key_data = apiCall("key", "", "info", key.value)

        if "apiError" in key_data:
            # 0 => Unknown error : Unhandled error, should not occur.
            # 1 => Key is empty : Private key is empty in current request.
            # 2 => Incorrect Key : Private key is wrong/incorrect format.
            # 3 => Wrong type : Requesting an incorrect basic type.
            # 4 => Wrong fields : Requesting incorrect selection fields.
            # 5 => Too many requests : Requests are blocked for a small period of time because of too many requests per user (max 100 per minute).
            # 6 => Incorrect ID : Wrong ID value.
            # 7 => Incorrect ID-entity relation : A requested selection is private (For example, personal data of another user / faction).
            # 8 => IP block : Current IP is banned for a small period of time because of abuse.
            # 9 => API disabled : Api system is currently disabled.
            # 10 => Key owner is in federal jail : Current key can't be used because owner is in federal jail.
            # 11 => Key change error : You can only change your API key once every 60 seconds.
            # 12 => Key read error : Error reading key from Database.
            # 13 => The key is temporarily disabled due to owner inactivity : The key owner hasn't been online for more than 7 days.
            # 14 => Daily read limit reached : Too many records have been pulled today by this user from our cloud services.
            # 15 => Temporary error : An error code specifically for testing purposes that has no dedicated meaning.
            # 16 => Access level of this key is not high enough : A selection is being called of which this key does not have permission to access.

            if key_data["apiErrorCode"] in [1, 2, 10]:
                print(f'[updateKeyLevel] {self}: delete key (error code {key_data["apiErrorCode"]})')
                self.key_level = -1
                self.validKey = False
                key.delete()
                self.save()
                return

            elif key_data["apiErrorCode"] in [13]:
                print(f'[updateKeyLevel] {self}: inactive key (error code {key_data["apiErrorCode"]})')
                self.key_level = -2
                self.validKey = False
                key.delete()
                self.save()
                return

            else:
                print(f'[updateKeyLevel] {self}: keep key (error code {key_data["apiErrorCode"]})')
                return

            # self.key_level = 0
            # self.validKey = False
            # key.access_level = 0
            # key.access_type = "Unkown"

        else:
            self.key_level = key_data["access_level"]
            key.access_level = key_data["access_level"]
            key.access_type = key_data["access_type"]

        # print(f'[updateKeyLevel] {self}: {key_data.get("access_type")}')

        key.save()
        self.save()

    def update_discord_id(self):
        error = False
        discord = apiCall("user", "", "discord", self.getKey())
        if "apiError" in discord:
            error = {"apiErrorSub": discord["apiError"]}
        else:
            dId = discord.get("discord", {"discordID": ""})["discordID"]
            self.dId = 0 if dId in [""] else dId
            self.save()

        return error

    def getInventory(self, force=False):
        if self.tId < 0:
            return {}

        # try to get cache
        inventory = cache.get(f"bazaar-inventory-{self.tId}", False)
        if inventory and not force:
            print("[getInventory] return cached inventory")
            return inventory

        inventory = {}
        if self.key_level < 2:
            print("[getInventory] key access not high enough")
            return inventory

        print("[getInventory] build inventory")
        invtmp = apiCall("user", "", "inventory,display,bazaar", self.getKey())
        for k, v in invtmp.items():
            if v is None:
                invtmp[k] = dict({})
        if "apiError" in invtmp:
            cache.set(f"bazaar-inventory-{self.tId}", inventory, 60)
            return invtmp
        else:
            inventory["inventory"] = {str(v["ID"]): [v.get("quantity", 0), 0] for v in invtmp.get("inventory", dict({}))}
            inventory["bazaar"] = {str(v["ID"]): [v.get("quantity", 0), v.get("price", 0)] for v in invtmp.get("bazaar", dict({}))}
            inventory["display"] = {str(v["ID"]): [v.get("quantity", 0), 0] for v in invtmp.get("display", dict({}))}
            cache.set(f"bazaar-inventory-{self.tId}", inventory, 60)

        return inventory

    def getAwards(self, userInfo=dict({}), force=False):
        from awards.functions import AWARDS_CAT, createAwards
        from awards.models import AwardsData

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
                    error = {"apiError": "Your data can't be found in the database."}

            if not len(userInfo) or force:
                req = apiCall(
                    "user",
                    "",
                    "personalstats,crimes,education,battlestats,workstats,skills,perks,gym,networth,merits,profile,medals,honors,icons,bars,weaponexp,hof",
                    self.getKey(),
                )
                if "apiError" not in req:
                    self.awardsUpda = tsnow()
                    defaults = {"req": json.dumps(req), "timestamp": tsnow()}
                    try:
                        self.tmpreq_set.update_or_create(type="awards", defaults=defaults)
                    except BaseException:
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

        summaryByType["AllAwards"] = {
            "nAwarded": len(myHonors) + len(myMedals),
            "nAwards": len(honors) + len(medals),
        }
        summaryByType["AllHonors"] = {"nAwarded": len(myHonors), "nAwards": len(honors)}
        summaryByType["AllMedals"] = {"nAwarded": len(myMedals), "nAwards": len(medals)}

        rScorePerso = 0.0
        for k, v in awardsTorn["honors"].items():
            if v.get("achieve", 0) == 1:
                rScorePerso += v.get("rScore", 0)
        for k, v in awardsTorn["medals"].items():
            if v.get("achieve", 0) == 1:
                rScorePerso += v.get("rScore", 0)

        awardsPlayer = {
            "userInfo": userInfo,
            "awards": awards,
            "pinnedAwards": pinnedAwards,
            "summaryByType": dict(
                {
                    k: v
                    for k, v in sorted(
                        summaryByType.items(),
                        key=lambda x: x[1]["nAwarded"],
                        reverse=True,
                    )
                }
            ),
        }

        if self.tId > 0 and not error:
            self.awardsScor = int(rScorePerso * 10000)
            self.awardsNumb = len(myMedals) + len(myHonors)
            self.save()

        return awardsPlayer, awardsTorn, error

    def awardsInfo(self):
        return "{:.4f}".format(self.awardsScor / 10000.0)

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
                merits[k]["description"] = [
                    "Increases maximum nerve bar by",
                    [1],
                    [""],
                    " points.",
                ]
            elif k == "Critical Hit Rate":
                merits[k]["description"] = [
                    "Increases critical hit rate by",
                    [0.5],
                    ["%"],
                    ".",
                ]
            elif k == "Life Points":
                merits[k]["description"] = [
                    "Constantly modifies life by",
                    [5],
                    ["%"],
                    ".",
                ]
            elif k == "Crime Experience":
                merits[k]["description"] = [
                    "Increases crime success ability by",
                    [3],
                    ["%"],
                    ".",
                ]
            elif k == "Education Length":
                merits[k]["description"] = [
                    "Decreases education course length by",
                    [2],
                    ["%"],
                    ".",
                ]
            elif k == "Awareness":
                merits[k]["description"] = [
                    "Increases frequency of items appearing in the city by",
                    [20],
                    ["%"],
                    ".",
                ]
            elif k == "Bank Interest":
                merits[k]["description"] = [
                    "Increases bank interest by",
                    [5],
                    ["%"],
                    ".",
                ]
            elif k == "Masterful Looting":
                merits[k]["description"] = [
                    "Increases money gained from mugging by",
                    [5],
                    ["%"],
                    ".",
                ]
            elif k == "Stealth":
                merits[k]["description"] = [
                    "Increases stealth during outgoing attacks by",
                    [0.2],
                    [""],
                    ".",
                ]
            elif k == "Hospitalizing":
                merits[k]["description"] = [
                    "Increases hospitalization time by",
                    [5],
                    ["%"],
                    ".",
                ]
            elif k == "Addiction Mitigation":
                merits[k]["description"] = [
                    "Reduces the negative effects of addiction by",
                    [2],
                    ["%"],
                    ".",
                ]
            elif k == "Employee Effectiveness":
                merits[k]["description"] = [
                    "Increases employee effectiveness by",
                    [1],
                    [""],
                    ".",
                ]
            elif k in ["Brawn", "Protection", "Sharpness", "Evasion"]:
                b = {
                    "Brawn": "strength",
                    "Protection": "defense",
                    "Evasion": "dexterity",
                    "Sharpness": "speed",
                }
                merits[k]["description"] = [
                    "Passive bonus of",
                    [3],
                    ["%"],
                    " in {}.".format(b.get(k)),
                ]
            elif k.split(" ")[-1] == "Mastery":
                # merits[k]["description"] = ["Increases damage and accuracy of {} by".format(k.replace(" Mastery", "").lower()), [1, 0.2], ["%", ""], " respectively."]
                merits[k]["description"] = [
                    "Increases damage and accuracy by",
                    [1, 0.2],
                    ["%", ""],
                    ".",
                ]

        # Critical Hit Rate - *Increases critical hit rate by 0.5%*
        # Awareness - *Increases frequency of items appearing in the city by *20%
        # Stealth - *Increases stealth during outgoing attacks by +0.2*
        # Hospitalizing - *Increases hospitalization time by 5%*

        return merits

    def getPersonalstats(self, req=None):
        from player.personalstats_dic import d as personalstats_dic

        if req is None:
            return dict({})

        personnalstats = dict({})

        for k, v in req.items():
            s = personalstats_dic.get(
                k,
                {
                    "category": "New entries",
                    "sub": "default",
                    "type": "integer",
                    "name": k,
                },
            )
            if s["category"] not in personnalstats:
                personnalstats[s["category"]] = [[], dict({})]
            if s["sub"] == "default":
                personnalstats[s["category"]][0].append([s["name"], v, s["type"]])
            else:
                if s["sub"] not in personnalstats[s["category"]][1]:
                    personnalstats[s["category"]][1][s["sub"]] = []
                personnalstats[s["category"]][1][s["sub"]].append([s["name"], v, s["type"]])

            if s["category"] == "Unknown":
                print(k, v)

        return personnalstats


class Message(models.Model):
    section = models.CharField(default="all", max_length=16, choices=SECTION_CHOICES)
    level = models.CharField(default="notice", max_length=16, choices=LEVEL_CHOICES)
    message = models.TextField()

    def __str__(self):
        return f"Message {self.pk} in {self.section}"


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

    def updateNumberOfPlayers(self):
        players = Player.objects.only("tId", "active", "validKey", "lastActionTS").exclude(tId=-1)

        self.nTotal = len(players)
        self.nValid = len(players.filter(active=True).exclude(validKey=False))
        self.nInact = len(players.filter(active=False))
        self.nInval = len(players.filter(validKey=False))
        self.nPrune = len(players.filter(validKey=False).exclude(active=True))

        t = int(time.time())
        self.nHour = len(players.filter(lastActionTS__gte=(t - (3600))))
        self.nDay = len(players.filter(lastActionTS__gte=(t - (24 * 3600))))
        self.nMonth = len(players.filter(lastActionTS__gte=(t - (31 * 24 * 3600))))

        self.save()


class Key(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)  # player
    tId = models.IntegerField(default=0)
    value = models.SlugField(max_length=32, unique=True)  # key
    lastPulled = models.IntegerField(default=0)  # ts when last pulled
    reason = models.CharField(default="-", max_length=64)  # reason why it was pulled

    # player can decide to tell YATA not use their key
    useSelf = models.BooleanField(default=True)
    useFact = models.BooleanField(default=True)

    # access
    access_level = models.IntegerField(default=0)
    access_type = models.CharField(default="Unkown", max_length=64)

    def __str__(self):
        return "Key of {}".format(self.player)


class Error(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)  # player
    timestamp = models.IntegerField(default=0)
    short_error = models.TextField(default="-")
    long_error = models.TextField(default="-")
    fixed = models.BooleanField(default=False)


class TmpReq(models.Model):
    # needed for "caching" awards
    player = models.ForeignKey(Player, on_delete=models.CASCADE)  # player
    timestamp = models.IntegerField(default=0)
    type = models.CharField(default="None", max_length=16)
    req = models.TextField(default="{}")
