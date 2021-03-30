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

from django.utils import timezone

from yata.gyms import *
from yata.handy import tsnow

import random

from awards.honors import d as honorsId

AWARDS_CAT = ["crimes", "drugs", "attacks", "faction", "items", "travel", "work", "gym", "money", "competitions", "commitment", "miscellaneous"]

HONORS_UNREACH = [263, 306, 311, 263, 214, 224, 225, 278, 223, 476]

HOF_SIZE = 50


def computeRarity(c):
    import math
    # Omega = 0.567143290409783872999968662210
    # return math.log(Omega*(c + 1))
    return float(c)


def honorId2Img(i):
    from awards.honors import d

    id = d.get(i)
    if id is None:
        url = None
        # print("honor number {}: not in dictionnary".format(i))
    elif not id:
        url = None
        # print("honor number {}: value 0".format(i))
    else:
        url = "https://awardimages.torn.com/{}.png".format(id)

    return url


def createAwardsSummary(awards):
    awardsSummary = dict()
    nAwardedTot = 0
    nAwardsTot = 0
    for k, v in awards.items():
        nAwarded = 0
        for l, w in v.items():
            if w["achieve"] == 1:
                nAwarded += 1
        nAwards = len(v)
        awardsSummary[k] = {"nAwarded": nAwarded, "nAwards": nAwards}
        nAwardedTot += nAwarded
        nAwardsTot += nAwards
    awardsSummary["All awards"] = {"nAwarded": nAwardedTot, "nAwards": nAwardsTot}

    return awardsSummary


def createAwards(tornAwards, userInfo, category, pinned=False):
    from itertools import chain
    from stock.models import Stock

    # needed in most cases
    honors_awarded = [int(k) for k in userInfo.get("honors_awarded", [])]
    honors_time = [int(k) for k in userInfo.get("honors_time", [])]
    medals_awarded = [int(k) for k in userInfo.get("medals_awarded", [])]
    medals_time = [int(k) for k in userInfo.get("medals_time", [])]
    daysOld = max(float(userInfo.get("age", 1)), 1.0)

    # convert energy to time
    eBar = userInfo.get("energy", {"maximum": 0})["maximum"]
    # natural, refill, 3 xan, 3 xan + refill
    eDay = [0, 0, 0, 0]
    eDay[0] = 480 if eBar == 100 else 720
    eDay[1] = eDay[0] + eBar
    eDay[2] = eDay[0] + 3 * 250
    eDay[3] = eDay[0] + eBar + 3 * 250

    def dLeftE(energy, r=None, c=None, perks=None):
        # try:
        # days
        try:
            d = [energy / ed for ed in eDay]
            # tootlip with details
            if energy == -1:
                return -1, ""
            elif r is not None:
                tt = "With a current ratio of <i>{:,.2g} {}</i><br>".format(r, c)
            elif c is not None:
                tt = "<i>{}</i><br>".format(c)
            elif perks is not None:
                tt = 'Prediction of energy needed (<i>courtesy of JTS <3</i>)<br>\
                       - Happy: {:.0f}<br>\
                       - Perks: {:.2f}%<br>\
                       - Gym: x{:.2f} ({})<br><br>'.format(*perks)
            else:
                tt = ""

            tt += 'Total energy needed: <i>{:,}</i><br>\
                    - natural energy: <b>{:.2f}</b> days<br>\
                    - daily refill: <b>{:.2f}</b> days<br>\
                    - 3 xanax / day: <b>{:.2f}</b> days<br>\
                    - both: <b>{:.2f}</b> days'.format(int(energy), *d)
            return d[0], tt
        except BaseException:
            return energy, energy

    if category == "crimes":

        crimeBridgeMedal2App = {
            "Computer": "Computer crimes",
            "Murder": "Murder",
            "Grand theft auto": "Auto theft",
            "Theft": "Theft",
            "Drug dealing": "Drug deals",
            "Fraud": "Fraud crimes"}

        crimeBridgeApp2API = {
            "Computer crimes": "computer_crimes",
            "Illegal products": "selling_illegal_products",
            "Murder": "murder",
            "Auto theft": "auto_theft",
            "Theft": "theft",
            "Drug deals": "drug_deals",
            "Fraud crimes": "fraud_crimes",
            "Other crimes": "other",
            "Total": "total"}

        forComment = {
            "Computer crimes": [9, 0.75],
            "Illegal products": [3, 1.0],
            "Murder": [10, 0.75],
            "Auto theft": [12, 0.7],
            "Theft": [4, 1.0],
            "Drug deals": [8, 0.8],
            "Fraud crimes": [11, 0.95],
            "Other crimes": [2, 1.0],
            "Total": [2, 1.0]}

        awards = dict({
            "Illegal products": dict(),
            "Theft": dict(),
            "Auto theft": dict(),
            "Drug deals": dict(),
            "Computer crimes": dict(),
            "Murder": dict(),
            "Fraud crimes": dict(),
            "Other crimes": dict(),
            "Organised crimes": dict(),
            "Jail": dict(),
            "Total": dict()})

        # totalNumberOfBusts = userInfo.get("personalstats", dict({})).get("peoplebusted", 0) + userInfo.get("personalstats", dict({})).get("failedbusts", 0)

        # nerve gain with one refill for 24h
        ngain = userInfo.get("nerve", {"maximum": 0})["maximum"]
        # nerve gain with one refill for 5min
        ngain5 = ngain / float(24 * 60 / 5)
        # time to get 1 nerve counting refill
        timeToGet1nerveRefi = 5 / float(1 + ngain5)

        # nerve gain with one beer for 1h
        pub = True if "+ 50% bottle of alcohol boost" in userInfo.get("company_perks", []) else False
        ngain = 1.5 if pub else 1
        # nerve gain with one beer for 5min
        ngain5 = ngain / float(1 * 60 / 5)
        # time to get 1 nerve counting beers
        timeToGet1nerveBeer = 5 / float(1 + ngain5)

        # nerve gain with 24 beers and 1 refill for 24h
        ngain = 1.5 * 24 if pub else 24
        ngain += int(userInfo.get("nerve", {"maximum": 0})["maximum"])
        # nerve gain with 24 beers and 1 refill for 5min
        ngain5 = ngain / float(24 * 60 / 5)
        # time to get 1 nerve counting beers
        timeToGet1nerveBoth = 5 / float(1 + ngain5)

        def dLeftN(nerve):
            d = [0, 0, 0, 0]
            d[0] = nerve * 5 / (60 * 24)
            d[1] = nerve * timeToGet1nerveRefi / (60 * 24)
            d[2] = nerve * timeToGet1nerveBeer / (60 * 24)
            d[3] = nerve * timeToGet1nerveBoth / (60 * 24)

            tt = "With an arbitrary <i>success rate of {:,.0f}%</i><br>\
                  Total Nerve needed: <i>{:,.0f}</i><br>\
                  - Expected time: <b>{:.1f}</b> days<br>\
                  - With daily refill: <b>{:.1f}</b> days<br>\
                  - With 24 beers a day: <b>{:.1f}</b> days<br>\
                  - With both: <b>{:.1f}</b> days{}".format(100 * forComment[type][1], nerve, *d, "<br><i>while working in a pub</i>" if pub else "")

            return d[0], tt

        for k, v in tornAwards["honors"].items():
            if v["type"] in [5, 15]:
                vp = v
                # vp["left"] = 0
                # vp["comment"] = ["", int(k)]
                vp["awardType"] = "Honor"
                vp["img"] = str(honorsId.get(int(k), 0))
                if int(k) in honors_awarded:
                    vp["awarded_time"] = int(honors_time[honors_awarded.index(int(k))])
                else:
                    vp["awarded_time"] = 0

                if int(k) in [2, 25, 154, 157, 158]:
                    type = "Theft"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("criminalrecord", dict({})).get(crimeBridgeApp2API[type], 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    nerve = max(forComment[type][0] * (vp["goal"] - vp["current"]) / forComment[type][1], 0)
                    n = dLeftN(nerve)
                    vp["left"] = n[0]
                    vp["comment"] = n[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [6]:
                    type = "Other crimes"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("criminalrecord", dict({})).get(crimeBridgeApp2API[type], 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    nerve = max(forComment[type][0] * (vp["goal"] - vp["current"]) / forComment[type][1], 0)
                    n = dLeftN(nerve)
                    vp["left"] = n[0]
                    vp["comment"] = n[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [24]:
                    type = "Fraud crimes"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("criminalrecord", dict({})).get(crimeBridgeApp2API[type], 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    nerve = max(forComment[type][0] * (vp["goal"] - vp["current"]) / forComment[type][1], 0)
                    n = dLeftN(nerve)
                    vp["left"] = n[0]
                    vp["comment"] = n[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [152]:
                    type = "Illegal products"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("criminalrecord", dict({})).get(crimeBridgeApp2API[type], 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    nerve = max(forComment[type][0] * (vp["goal"] - vp["current"]) / forComment[type][1], 0)
                    n = dLeftN(nerve)
                    vp["left"] = n[0]
                    vp["comment"] = n[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [153]:
                    type = "Drug deals"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("criminalrecord", dict({})).get(crimeBridgeApp2API[type], 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    nerve = max(forComment[type][0] * (vp["goal"] - vp["current"]) / forComment[type][1], 0)
                    n = dLeftN(nerve)
                    vp["left"] = n[0]
                    vp["comment"] = n[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [155, 161]:
                    type = "Computer crimes"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("criminalrecord", dict({})).get(crimeBridgeApp2API[type], 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    nerve = max(forComment[type][0] * (vp["goal"] - vp["current"]) / forComment[type][1], 0)
                    n = dLeftN(nerve)
                    vp["left"] = n[0]
                    vp["comment"] = n[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [159]:
                    type = "Murder"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("criminalrecord", dict({})).get(crimeBridgeApp2API[type], 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    nerve = max(forComment[type][0] * (vp["goal"] - vp["current"]) / forComment[type][1], 0)
                    n = dLeftN(nerve)
                    vp["left"] = n[0]
                    vp["comment"] = n[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [160]:
                    type = "Auto theft"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("criminalrecord", dict({})).get(crimeBridgeApp2API[type], 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    nerve = max(forComment[type][0] * (vp["goal"] - vp["current"]) / forComment[type][1], 0)
                    n = dLeftN(nerve)
                    vp["left"] = n[0]
                    vp["comment"] = n[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [251]:
                    type = "Total"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("criminalrecord", dict({})).get(crimeBridgeApp2API[type], 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["left"] = max(forComment[type][0] * (vp["goal"] - vp["current"]) / forComment[type][1], 0)
                    awards[type]["h_" + k] = vp

                elif int(k) in [552]:
                    type = "Organised crimes"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[2].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("organisedcrimes", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp

                elif int(k) in [248, 249, 250]:
                    # 248 {'name': 'Bar Breaker', 'description': 'Make 1,000 busts', 'type': 15, 'circulation': 4454, 'rarity': 'Rare', 'goal': 1000, 'awardType': 'Honor'}
                    type = "Jail"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("peoplebusted", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / daysOld
                    vp["left"] = max((vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    vp["comment"] = "{:.1f} days with a current ratio of {:,.2g} people busted / day".format(vp["left"], ratio)
                    awards[type]["h_" + k] = vp

                elif int(k) in [252]:
                    # 252 {'name': "Freedom Isn't Free", 'description': 'Make 500 bails from jail', 'type': 15, 'circulation': 2032, 'rarity': 'Extraordinary', 'goal': 500, 'awardType': 'Honor'}
                    type = "Jail"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("peoplebought", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratioMoney = vp["current"] / float(max(userInfo.get("personalstats", dict({})).get("peopleboughtspent", 1), 1))
                    ratio = vp["current"] / daysOld
                    vp["left"] = max((vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    vp["comment"] = "{:.1f} days with a current ratio of {:,.2g} people bought / day<br>Current ratio of {:,.2g} k$ / people bought.".format(vp["left"], ratio, 0.001 / ratioMoney if ratioMoney > 0 else 0)
                    awards[type]["h_" + k] = vp

                elif int(k) in [906]:
                    # "906": { "name": "Repeat Offender", "description": "Go to jail 250 times", "type": 15,
                    type = "Jail"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[3].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("jailed", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["left"] = max((vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    awards[type]["h_" + k] = vp

                # else:
                #     vp["comment"] = ["", ""]
                #     vp["left"] = ""

        for k, v in tornAwards["medals"].items():
            vp = v
            # vp["left"] = 0
            # vp["comment"] = ["", int(k)]
            vp["awardType"] = "Medal"
            vp["img"] = k
            if int(k) in medals_awarded:
                vp["awarded_time"] = int(medals_time[medals_awarded.index(int(k))])
            else:
                vp["awarded_time"] = 0

            if v["type"] == "CRM":
                type = crimeBridgeMedal2App[" ".join(v["description"].split(" ")[2:-1])]
                vp["category"] = category
                vp["subcategory"] = type
                vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                vp["current"] = userInfo.get("criminalrecord", dict({})).get(crimeBridgeApp2API[type], 0)
                vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                nerve = max(forComment[type][0] * (vp["goal"] - vp["current"]) / forComment[type][1], 0)
                n = dLeftN(nerve)
                vp["left"] = n[0]
                vp["comment"] = n[1]
                awards[type]["m_" + k] = vp

            elif v["type"] == "OTR":
                if int(k) in [30, 31, 32, 33, 105, 106, 107]:
                    type = "Jail"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("peoplebusted", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / daysOld
                    vp["left"] = max((vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    vp["comment"] = "{:.1f} days with a current ratio of {:,.2g} people busted / day".format(vp["left"], ratio)
                    awards[type]["m_" + k] = vp

    elif category == "drugs":

        # WARNING absolute discusting HACK to avoid type Speed from drug and from gym to mix up
        # (which results in 50 speed no showing up in all awards)
        # There is a white space after avery drug type.

        # minutes of CD
        forComment = dict({
            "Cannabis ": 75,
            "Ecstasy ": 210,
            "Ketamine ": 55,
            "LSD ": 425,
            "Opium ": 215,
            "Shrooms ": 209.5,
            "Speed ": 301,
            "PCP ": 330,
            "Xanax ": 420,
            "Vicodin ": 300})

        awards = dict({
            "Cannabis ": dict(),
            "Ecstasy ": dict(),
            "Ketamine ": dict(),
            "LSD ": dict(),
            "Opium ": dict(),
            "Shrooms ": dict(),
            "Speed ": dict(),
            "PCP ": dict(),
            "Xanax ": dict(),
            "Vicodin ": dict()})

        for k, v in tornAwards["honors"].items():
            if v["type"] == 6:
                vp = v
                # vp["left"] = 0
                # vp["comment"] = ["", int(k)]
                vp["awardType"] = "Honor"
                vp["img"] = str(honorsId.get(int(k), 0))
                if int(k) in honors_awarded:
                    vp["awarded_time"] = int(honors_time[honors_awarded.index(int(k))])
                else:
                    vp["awarded_time"] = 0

                if int(k) in [26]:
                    type = "Cannabis "
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [29, 30, 31, 32, 33, 34, 35, 36, 37, 38]:
                    type = v["description"].split(" ")[-1] + " "
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 50
                    key = type.lower()[:3] + "taken"
                    if key == "ecstaken":
                        key = "exttaken"
                    vp["current"] = userInfo.get("personalstats", dict({})).get(key, 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["comment"] = "With an average of {:.0f} minutes of cooldown".format(forComment[type])
                    vp["left"] = max(forComment[type] * (vp["goal"] - vp["current"]) / 1440.0, 0)
                    awards[type]["h_" + k] = vp

    elif category == "attacks":

        awards = dict({
            "Wins": dict(),
            "Defends": dict(),
            "Escapes": dict(),
            "Kill streak": dict(),
            "Critical hits": dict(),
            "Bounties": dict(),
            "Fire rounds": dict(),
            "Special ammo": dict(),
            "Other Attacks": dict(),
            "Assists": dict(),
            "Damage": dict(),
            "Finishing hits": dict()})

        keysTmp = ["attackswon", "attackslost", "attacksdraw", "attacksassisted"]
        totalNumberOfAttacks = sum([int(userInfo.get("personalstats", dict({})).get(k, 0)) for k in keysTmp])
        keysTmp = ["defendslost", "defendswon", "defendsstalemated", "theyrunaway"]
        totalNumberOfDefends = sum([int(userInfo.get("personalstats", dict({})).get(k, 0)) for k in keysTmp])

        for k, v in tornAwards["honors"].items():
            if int(v["type"]) in [8, 2, 3, 15]:
                vp = v
                # vp["left"] = 0
                # vp["comment"] = ["", int(k)]
                vp["awardType"] = "Honor"
                vp["img"] = str(honorsId.get(int(k), 0))
                if int(k) in honors_awarded:
                    vp["awarded_time"] = int(honors_time[honors_awarded.index(int(k))])
                else:
                    vp["awarded_time"] = 0

                if int(k) in [39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49]:
                    # 39 {'name': 'Woodland Camo', 'description': 'Win 5 awards', 'type': 3, 'circulation': 205626, 'rarity': 'Very Common', 'awardType': 'Honor', 'achieve': 0}
                    type = "Wins"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("attackswon", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / float(max(totalNumberOfAttacks, 1))
                    e = max(25 * (vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    days = dLeftE(e, r=ratio, c="wins / attack")
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [28, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 515]:
                    # 28 {'name': 'Machinist', 'description': 'Achieve 100 finishing hits with mechanical weapons', 'type': 2, 'circulation': 9269, 'rarity': 'Limited', 'awardType': 'Honor', 'achieve': 0}
                    type = "Finishing hits"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    end = " ".join(v["description"].split(" ")[5:])
                    key = end.lower()[:3] + "hits"
                    bridge = {"heahits": "heahits",
                              "mechits": "chahits",
                              "cluhits": "axehits",
                              "temhits": "grehits",
                              "machits": "machits",
                              "pishits": "pishits",
                              "rifhits": "rifhits",
                              "shohits": "shohits",
                              "smghits": "smghits",
                              "piehits": "piehits",
                              "slahits": "slahits",
                              "fishits": "h2hhits"}
                    vp["current"] = userInfo.get("personalstats", dict({})).get(bridge[key], 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / float(max(totalNumberOfAttacks, 1))
                    e = max(25 * (vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    days = dLeftE(e, r=ratio, c="{} / attack".format(key))
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [611]:
                    # "611": {"name": "War Machine", "description": "Achieve 1,000 finishing hits in every category","type": 2,
                    type = "Finishing hits"
                    vp["category"] = category
                    vp["subcategory"] = type
                    nHits = int(v["description"].split(" ")[1].replace(",", ""))
                    bridge = {"heahits": ["Heavy artillery", 0, ""],
                              "chahits": ["Mechanical guns", 0, ""],
                              "axehits": ["Clubbing weapons", 0, ""],
                              "grehits": ["Temporary weapons", 0, ""],
                              "machits": ["Machine guns", 0, ""],
                              "pishits": ["Pistols", 0, ""],
                              "rifhits": ["Rifles", 0, ""],
                              "shohits": ["Shotguns", 0, ""],
                              "smghits": ["Sub machine guns", 0, ""],
                              "piehits": ["Piercing weapons", 0, ""],
                              "slahits": ["Slashing weapons", 0, ""],
                              "h2hhits": ["Hand to hand", 0, ""]}
                    vp["goal"] = nHits * len(bridge)

                    current = 0
                    for fhit in bridge:
                        n = userInfo.get("personalstats", dict({})).get(fhit, 0)
                        current += min(n, nHits)
                        bridge[fhit][1] = n
                        bridge[fhit][2] = "error" if n < nHits else "valid"

                    bridge = sorted(bridge.values(), key=lambda x: -x[1])
                    vp["current"] = current
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["comment"] = "<br>".join(['<b class={}>{}</b>: {:,d} ({:.0f}%)'.format(v[2], v[0], v[1], 100 * min(1, v[1] / nHits)) for v in bridge])
                    awards[type]["h_" + k] = vp

                elif int(k) in [828, 871]:
                    # "828": {"name": "Finale","description": "Defeat someone on the 25th turn of an attack","type": 8,
            		# "871": { "name": "Leonidas", "description": "Achieve a finishing hit with Kick", "type": 2,
                    type = "Finishing hits"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [15, 16, 17]:
                    # 15 {'name': 'Kill Streaker 1', 'description': 'Achieve a best killstreak of 10', 'type': 8, 'circulation': 124231, 'rarity': 'Very Common'}
                    type = "Kill streak"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[-1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("killstreak", 0)
                    vp["achieve"] = 1 if int(k) in honors_awarded else min(1, float(vp["current"]) / float(vp["goal"]))
                    # vp["left"] = userInfo.get("personalstats", dict({})).get("bestkillstreak", 0)
                    # vp["comment"] = ["best kill streak", ""]
                    days = dLeftE(max(25 * (vp["goal"] - vp["current"]), 0))
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [20, 227]:
                    # 20 {'name': 'Precision', 'description': 'Achieve 25 critical hits', 'type': 8, 'circulation': 133458, 'rarity': 'Very Common'}
                    type = "Critical hits"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("attackcriticalhits", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / float(max(totalNumberOfAttacks, 1))
                    e = max(25 * (vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    days = dLeftE(e, r=ratio, c="critical hits / attack")
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [22, 228]:
                    # 22 {'name': 'Self Defense', 'description': 'Win 50 defends', 'type': 8, 'circulation': 31674, 'rarity': 'Common', 'awardType': 'Honor'}
                    # 228 {'name': '007', 'description': 'Achieve 1,000 attacks and 1,000 defends', 'type': 8, 'circulation': 1710, 'rarity': 'Extraordinary', 'awardType': 'Honor'}
                    type = "Defends"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("defendswon", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / daysOld
                    vp["left"] = max((vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    vp["comment"] = "{:.1f} days with a current ratio of {:.2g} defends won / day.".format(vp["left"], ratio)
                    awards[type]["h_" + k] = vp

                elif int(k) in [719]:
                    # "719": {"name": "Invictus", "description": "Successfully defend against someone who has at least double your battle stats", "type": 8,
                    type = "Defends"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [27]:
                    # 27 {'name': 'Night Walker', 'description': 'Make 100 stealthed attacks', 'type': 8, 'circulation': 50474, 'rarity': 'Common', 'awardType': 'Honor'}
                    type = "Other Attacks"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("attacksstealthed", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / float(max(userInfo.get("personalstats", dict({})).get("attackswon", 0), 1))
                    e = max(25 * (vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    days = dLeftE(e, r=ratio, c="stealth / win")
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [903]:
                    # "903": { "name": "Booboo", "description": "Go to hospital 250 times", "type": 15,
                    type = "Other Attacks"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[3].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("hospital", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["left"] = max((vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1

                    awards[type]["h_" + k] = vp

                elif int(k) in [740, 741, 786]:
                    # "740": {"name": "Devastation", "description": "Deal at least 5,000 damage in a single hit", "type": 8,
                    # "741": {"name": "Obliteration", "description": "Deal at least 10,000 damage in a single hit",	"type": 8,
                    # "786": { "name": "Annihilation", "description": "Deal at least 15,000 damage in a single hit", "type": 8,
                    type = "Damage"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[3].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("bestdamage", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp

                elif int(k) in [1001, 1002, 1003, 1004]:
                    # "1001": { "name": "Boom!", "description": "Deal over 10,000,000 total damage", "type": 8,
                    # "1002": { "name": "Bam!", "description": "Deal over 1,000,000 total damage", "type": 8,
                    # "1003": { "name": "Kapow!", "description": "Deal over 100,000,000 total damage", "type": 8,
                    # "1004": { "name": "Wham!", "description": "Deal over 100,000 total damage", "type": 8,
                    type = "Damage"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[2].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("attackdamage", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp

                elif int(k) in [763]:
                    # 763: "name": "Bare", "description": "Win 250 unarmored attacks or defends", "type": 8,
                    type = "Other Attacks"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("unarmoredwon", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / float(max(userInfo.get("personalstats", dict({})).get("attackswon", 0), 1))
                    e = max(25 * (vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    days = dLeftE(e, r=ratio, c="unarmored win / win")
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [140, 151, 834, 836]:
                    # 140 {'name': 'Spray And Pray', 'description': 'Fire 2,500 rounds', 'type': 8, 'circulation': 72720, 'rarity': 'Very Common', 'awardType': 'Honor'}
                    # 140 changed from 2.5k to 1k
                    # "151": {"name": "Two Halves Make A Hole","description": "Fire 10,000 rounds","type": 8,
                    # 151 changed from 25k to 10k
                    # "834": {"name": "Lead Salad","description": "Fire 100,000 rounds","type": 8,
                    # "836": {"name": "Peppered","description": "Fire 1,000,000 rounds","type": 8,
                    type = "Fire rounds"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("roundsfired", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / float(max(totalNumberOfAttacks, 1))
                    e = max(25 * (vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    days = dLeftE(e, r=ratio, c="rounds / attack")
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [800, 793, 791]:
                    # "800": {"name": "Surplus", "description": "Use 100 rounds of special ammunition", "type": 2,
                    # "793": {"name": "Bandolier","description": "Use 1,000 rounds of special ammunition", "type": 2,
                    # "791": { "name": "Quartermaster","description": "Use 10,000 rounds of special ammunition", "type": 2,
                    type = "Special ammo"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("specialammoused", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / float(max(totalNumberOfAttacks, 1))
                    e = max(25 * (vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    days = dLeftE(e, r=ratio, c="rounds / attack")
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [942, 943, 944, 945]:
                    # "942": {"name": "Maimed", "description": "Use 2,500 Hollow Point rounds", "type": 2,
                    # "943": { "name": "Penetrated", "description": "Use 2,500 Piercing rounds", "type": 2,
                    # "944": { "name": "Scorched", "description": "Use 2,500 Incendiary rounds", "type": 2,
                    # "945": { "name": "Marked", "description": "Use 2,500 Tracer rounds", "type": 2,
                    type = "Special ammo"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    ammo_type = v["description"].split(" ")[2].lower()
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["current"] = userInfo.get("personalstats", dict({})).get(f'{ammo_type}ammoused', 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / float(max(totalNumberOfAttacks, 1))
                    e = max(25 * (vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    days = dLeftE(e, r=ratio, c="rounds / attack")
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [951]:
            		# "951": { "name": "Dragon's Breath", "description": "Use a 12 Gauge Incendiary round", "type": 2,
                    type = "Special ammo"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["comment"] = "Equip a shotgun to enable 12 Gauge special ammo spawn"
                    awards[type]["h_" + k] = vp

                elif int(k) in [230, 254, 481, 500, 615, 608, 627, 739, 631, 317, 781, 827, 838, 843, 670, 896, 902, 414, 955]:
                    # 230 {'name': 'Domino Effect', 'description': 'Defeat someone displaying this honor', 'type': 8, 'circulation': 112529, 'rarity': 'Very Common', 'awardType': 'Honor'}
                    # 254 {'name': 'Flatline', 'description': 'Achieve a one hit kill on a target from full life', 'type': 8, 'circulation': 72276, 'rarity': 'Very Common', 'awardType': 'Honor'}
                    # 500 {'name': 'Survivalist', 'description': 'Win an attack with only 1% life remaining', 'type': 8, 'circulation': 5980, 'rarity': 'Limited', 'awardType': 'Honor'}
                    # 481 {'name': 'Semper     Fortis', 'description': 'Defeat someone more powerful than you', 'type': 8, 'circulation': 29809, 'rarity': 'Common', 'awardType': 'Honor'}
                    # 615 {'name': 'Guardian Angel', 'description': 'Defeat someone while they are attacking someone else', 'type': 8, 'circulation': 6228, 'rarity': 'Limited', 'awardType': 'Honor'}
                    # 781 { "name": "Riddled", "description": "Defeat an opponent after hitting at least 10 different body parts in a single attack", "type": 8,
                    # "827": {"name": "Deadly Duo","description": "Attack and defeat an opponent with your spouse","type": 8,
                    # "838": { "name": "Lovestruck", "description": "Defeat a married couple", "type": 8,
                    # "670": { "name": "Giant Slayer", "description": "Receive loot from a defeated NPC", "type": 8,
            		# "896": { "name": "Going Postal", "description": "Defeat a company co-worker", "type": 8,
                    # "902": { "name": "Gone Fishing", "description": "Be defeated by a trout", "type": 2,
                    # "414": { "name": "Triple Tap", "description": "Achieve three headshots in a row", "type": 8,
                    # "955": { "name": "Yoink", "description": "Successfully mug someone who just mugged someone else", "type": 8,
                    type = "Other Attacks"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [778]:
                    # 778 { "name": "Specialist", "description": "Achieve 100% EXP on 25 different weapons",
                    type = "Other Attacks"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[4].replace(",", ""))
                    wexp = userInfo.get("weaponexp", [])[:25]
                    maxExp = 0
                    def exp_to_hits(exp):
                        if exp < 25:
                            return (25 - exp) * 8 + 1800
                        elif exp < 50:
                            return (50 - exp) * 12 + 1500
                        elif exp < 75:
                            return (75 - exp) * 20 + 1000
                        else:
                            return (100 - exp) * 40

                    totalHits = 50000
                    totalHitsMade = 0
                    for we in wexp:
                        we["hits"] = 2000 - exp_to_hits(we["exp"])
                        we["progress"] = 100 * min(1, float(we["hits"]) / 2000.)
                        if we["exp"] == 100:
                            we["class"] = "valid"
                            maxExp += 1
                        elif we["exp"] > 90:
                            we["class"] = "warning"
                        else:
                            we["class"] = "error"

                        totalHitsMade += we["hits"]

                    sup5 = [f'<span class={w["class"]}>{i + 1:02d} {w["name"]}</span>: {w["progress"]:,.0f}% {2000 - w["hits"] if int(w["exp"]) < 100 else ""}' for i, w in enumerate(wexp)]
                    vp["current"] = maxExp
                    vp["achieve"] = min(1, float(totalHitsMade) / float(totalHits))
                    if len(sup5):
                        sup5.insert(0, "<b>List of the first 25 highest experienced weapons</b><br>with progress and remaining hits:<br>")
                        sup5.append(f'<br>Total hits made {totalHitsMade:,d} / {totalHits:,d} ({100 * vp["achieve"]:,.0f}%).')
                        sup5.append(f'Total remaining hits {totalHits - totalHitsMade:,d}.')
                        sup5.append(f"<br><i>The progress is based on hits made so it is different from the weapon experience.</i>")
                        vp["comment"] = "<br>".join(sup5)
                    awards[type]["h_" + k] = vp

                elif int(k) in [232]:
                    # 232 {'name': 'Bounty Hunter', 'description': 'Collect 250 bounties', 'type': 8, 'circulation': 3942, 'rarity': 'Rare', 'awardType': 'Honor'}
                    type = "Bounties"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("bountiescollected", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    days = dLeftE(max(25 * (vp["goal"] - vp["current"]), 0))
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [236]:
                    # 236 {'name': 'Dead Or Alive', 'description': 'Earn $10,000,000 from bounty hunting', 'type': 8, 'circulation': 12012, 'rarity': 'Uncommon', 'awardType': 'Honor'}
                    type = "Bounties"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", "").replace("$", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("totalbountyreward", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["head"] = "$"
                    ratio = vp["current"] / float(max(userInfo.get("personalstats", dict({})).get("bountiescollected", 0), 1))
                    e = max(25 * (vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    days = dLeftE(e, r=ratio, c="$ / bounty")
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [247]:
                    # 247 {'name': 'Blood Money', 'description': 'Make $1,000,000 from a single mugging', 'type': 8, 'circulation': 32879, 'rarity': 'Common', 'awardType': 'Honor'}
                    type = "Other Attacks"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", "").replace("$", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("largestmug", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["head"] = "$"
                    awards[type]["h_" + k] = vp

                elif int(k) in [270]:
                    # 270 {'name': 'Deadlock', 'description': 'Stalemate 100 times', 'type': 8, 'circulation': 5194, 'rarity': 'Rare', 'awardType': 'Honor'}
                    type = "Other Attacks"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("attacksdraw", 0) + userInfo.get("personalstats", dict({})).get("defendsstalemated", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    days = dLeftE(max(25 * (vp["goal"] - vp["current"]), 0))
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [639, 665]:
                    # 639 {'name': 'Double Dragon', 'description': 'Assist in a single attack', 'type': 8, 'circulation': 5413, 'rarity': 'Rare', 'awardType': 'Honor'}
                    # "665": { "name": "Boss Fight", "description": "Participate in the defeat of Duke",
                    type = "Assists"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    days = dLeftE(max(25 * (vp["goal"] - vp["current"]), 0))
                    awards[type]["h_" + k] = vp

                elif int(k) in [490]:
                    # 490 {'name': 'Sidekick', 'description': 'Assist in 250 attacks', 'type': 8, 'circulation': 59, 'rarity': 'Extremely Rare', 'awardType': 'Honor'}
                    type = "Assists"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[2].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("attacksassisted", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    days = dLeftE(max(25 * (vp["goal"] - vp["current"]), 0))
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [517]:
                    # 517 {'name': 'Pressure Point', 'description': 'Achieve 100 one hit kills', 'type': 8, 'circulation': 13351, 'rarity': 'Uncommon', 'awardType': 'Honor'}
                    type = "Other Attacks"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("onehitkills", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / float(max(totalNumberOfAttacks, 1))
                    e = max(25 * (vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    days = dLeftE(e, r=ratio, c="one hit kill / attack")
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [601]:
                    # 601 {'name': 'Fury', 'description': 'Achieve 10,000 hits', 'type': 8, 'circulation': 8172, 'rarity': 'Limited', 'awardType': 'Honor'}
                    type = "Other Attacks"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("attackhits", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / float(max(totalNumberOfAttacks, 1))
                    e = max(25 * (vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    days = dLeftE(e, r=ratio, c="hit / attack")
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["h_" + k] = vp

        for k, v in tornAwards["medals"].items():
            if v["type"] == "ATK":
                vp = v
                # vp["left"] = 0
                # vp["comment"] = ["", int(k)]
                vp["awardType"] = "Medal"
                vp["img"] = k
                if int(k) in medals_awarded:
                    vp["awarded_time"] = int(medals_time[medals_awarded.index(int(k))])
                else:
                    vp["awarded_time"] = 0

                if int(k) in [174, 175, 176, 177, 178]:
                    # 174 {'name': 'Anti Social', 'description': 'Win 50 attacks', 'type': 'ATK'}
                    type = "Wins"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("attackswon", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / float(max(totalNumberOfAttacks, 1))
                    e = max(25 * (vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    days = dLeftE(e, r=ratio, c="wins / attack")
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["m_" + k] = vp

                elif int(k) in [179, 180, 181, 182, 183]:
                    # 179 {'name': 'Bouncer', 'description': 'Successfully defend against 50 attacks', 'type': 'ATK', 'awardType': 'Medals'}
                    type = "Defends"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[-2].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("defendswon", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / daysOld
                    vp["left"] = max((vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    vp["comment"] = "{:.1f} days with a current ratio of {:.2g} defends won / day.".format(vp["left"], ratio)
                    awards[type]["m_" + k] = vp

                elif int(k) in [184, 185, 186]:
                    # 184 {'name': 'Close Escape', 'description': 'Successfully escape from 50 foes', 'type': 'ATK', 'awardType': 'Medal'}
                    type = "Escapes"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[-2].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("yourunaway", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    days = dLeftE(max(25 * (vp["goal"] - vp["current"]), 0))
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["m_" + k] = vp

                elif int(k) in [187, 188, 189]:
                    # 187 {'name': 'Ego Smashing', 'description': 'Have 50 enemies escape from you during an attack', 'type': 'ATK', 'awardType': 'Medal'}
                    type = "Escapes"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("theyrunaway", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / daysOld
                    vp["left"] = max((vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    vp["comment"] = "With a current ratio of {:.2g} escapes / day.".format(ratio)
                    awards[type]["m_" + k] = vp

                elif int(k) in [190, 191, 192, 193, 194]:
                    # 190 {'name': 'Strike', 'description': 'Acquire a kill streak of 25', 'type': 'ATK', 'awardType': 'Medal'}
                    type = "Kill streak"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[-1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("killstreak", 0)
                    vp["achieve"] = 1 if int(k) in userInfo.get("medals_awarded", []) else min(1, float(vp["current"]) / float(vp["goal"]))
                    # vp["left"] = userInfo.get("personalstats", dict({})).get("bestkillstreak", 0)
                    # vp["comment"] = ["best kill streak", ""]
                    days = dLeftE(max(25 * (vp["goal"] - vp["current"]), 0))
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["m_" + k] = vp

                elif int(k) in [195, 196, 197]:
                    # 195 {'name': 'Boom Headshot', 'description': 'Deal 500 critical hits to enemies during combat', 'type': 'ATK', 'awardType': 'Medal'}
                    type = "Critical hits"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("attackcriticalhits", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / float(max(totalNumberOfAttacks, 1))
                    e = max(25 * (vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    days = dLeftE(e, r=ratio, c="critical hits / attack")
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["m_" + k] = vp

                elif int(k) in [201, 202, 203]:
                    # 201 {'name': 'Hired Gun', 'description': 'Collect 25 bounties', 'type': 'ATK', 'awardType': 'Medal', 'goal': 25, 'current': 160, 'achieve': 1}
                    type = "Bounties"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("bountiescollected", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    days = dLeftE(max(25 * (vp["goal"] - vp["current"]), 0))
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["m_" + k] = vp

    elif category == "faction":

        awards = dict({
            "Respect": dict(),
            "Chains": dict(),
            "Other Faction": dict(),
            "Commitment": dict(),
            "Dirty bomb": dict()})

        for k, v in tornAwards["honors"].items():
            if int(v["type"]) in [0, 8, 2]:
                vp = v
                # vp["left"] = 0
                # vp["comment"] = ["", int(k)]
                vp["awardType"] = "Honor"
                vp["img"] = str(honorsId.get(int(k), 0))
                if int(k) in honors_awarded:
                    vp["awarded_time"] = int(honors_time[honors_awarded.index(int(k))])
                else:
                    vp["awarded_time"] = 0

                if int(k) in [253, 255, 257, 475, 476, 641, 916]:
                    # 253 {'name': 'Chainer 1', 'description': 'Participate in a 10 length chain', 'type': 8, 'circulation': 39418, 'rarity': 'Common', 'awardType': 'Honor'}
                    # "641": { "name": "Strongest Link", "description": "Make 100 hits in a single chain", "type": 8,
            		# "916": { "name": "Chain Saver", "description": "Save a 100+ chain 10 seconds before it breaks", "type": 8,
                    type = "Chains"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [256, 477, 478]:
                    # 256 {'name': 'Carnage', 'description': 'Make a single hit that earns your faction 10 or more respect', 'type': 8, 'circulation': 19716, 'rarity': 'Uncommon', 'awardType': 'Honor'}
                    type = "Respect"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [605, 488]:
                    # "605": {"name": "Friendly Fire", "description": "Defeat a fellow faction member", "type": 8,
                    # "488": {"name": "Vengeance", "description": "Successfully perform a faction retaliation hit","type": 8,
                    type = "Other Faction"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [14, 156, 231]:
                    # 14 {'name': 'Slow Bomb', 'description': 'Use a dirty bomb', 'type': 0, 'circulation': 27, 'rarity': 'Extremely Rare', 'awardType': 'Honor', 'img': None, 'title': 'Slow Bomb [14]: Extremely Rare (27)'}
                    # 231 {'name': 'Discovery', 'description': 'Be in a faction which starts making a dirty bomb', 'type': 0, 'circulation': 4566, 'rarity': 'Rare', 'awardType': 'Honor', 'img': 175241290, 'title': 'Discovery [231]: Rare (4566)'}
                    # 156 {'name': 'RDD', 'description': 'Use a dirty bomb', 'type': 0, 'circulation': 27, 'rarity': 'Extremely Rare', 'awardType': 'Honor', 'img': None, 'title': 'RDD [156]: Extremely Rare (27)'}
                    type = "Dirty bomb"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

        for k, v in tornAwards["medals"].items():
            if v["type"] in ["ATK", "CMT"]:
                vp = v
                # vp["left"] = 0
                # vp["comment"] = ["", int(k)]
                vp["awardType"] = "Medal"
                vp["img"] = k
                if int(k) in medals_awarded:
                    vp["awarded_time"] = int(medals_time[medals_awarded.index(int(k))])
                else:
                    vp["awarded_time"] = 0

                if int(k) in [215, 216, 217, 218, 219, 220, 221, 222, 223, 224]:
                    # 215 {'name': 'Recruit', 'description': 'Earn 100 respect for your faction', 'type': 'ATK', 'awardType': 'Medal'}
                    type = "Respect"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("respectforfaction", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    keysTmp = ["attackswon", "attackslost", "attacksdraw", "attacksassisted"]
                    totalNumberOfAttacks = sum([int(userInfo.get("personalstats", dict({})).get(k, 0)) for k in keysTmp])
                    ratio = vp["current"] / float(max(totalNumberOfAttacks, 1))
                    e = max(25 * (vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    days = dLeftE(e, r=ratio, c="respect / attack")
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["m_" + k] = vp

                elif int(k) in [26, 27, 28, 29, 108, 109, 148, 149, 150, 151]:
                    # 26 {'name': 'Apprentice Faction Member', 'description': 'Serve 100 days in a single faction', 'type': 'CMT', 'awardType': 'Medal'}
                    type = "Commitment"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("faction", {"days_in_faction": 0}).get("days_in_faction", 0)
                    vp["achieve"] = 1 if int(k) in userInfo.get("medals_awarded", []) else min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["left"] = max((vp["goal"] - vp["current"]), 0)
                    vp["comment"] = "{:.1f} days".format(vp["left"])
                    awards[type]["m_" + k] = vp

    elif category == "items":

        awards = dict({
            "City": dict(),
            "Medical items": dict(),
            "Other Items": dict(),
            "Pranks": dict(),
            "Consume": dict()})

        for k, v in tornAwards["honors"].items():
            if int(v["type"]) in [0, 15, 16]:
                vp = v
                # vp["left"] = 0
                # vp["comment"] = ["", int(k)]
                vp["awardType"] = "Honor"
                vp["img"] = str(honorsId.get(int(k), 0))
                if int(k) in honors_awarded:
                    vp["awarded_time"] = int(honors_time[honors_awarded.index(int(k))])
                else:
                    vp["awarded_time"] = 0

                if int(k) in [398, 418]:
                    # 398 {'name': 'Anaemic', 'description': 'Fill 1,000 empty blood bags', 'type': 15, 'circulation': 3823, 'rarity': 'Rare', 'awardType': 'Honor', 'goal': 1000, 'current': 0, 'achieve': 0.0}
                    type = "Medical items"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("bloodwithdrawn", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["left"] = max(3 * (vp["goal"] - vp["current"]) / 24, 0)
                    vp["comment"] = "3h cooldown / blood bag filled"

                    awards[type]["h_" + k] = vp

                elif int(k) in [367, 406, 882]:
                    # 406 {'name': 'Vampire', 'description': 'Random chance upon using a blood bag', 'type': 15, 'circulation': 10562, 'rarity': 'Limited', 'awardType': 'Honor', 'achieve': 0}
                    # 367 {'name': 'Clotted', 'description': 'Suffer from an acute haemolytic reaction, or be immune to it', 'type': 15, 'circulation': 11247, 'rarity': 'Uncommon', 'awardType': 'Honor', 'achieve': 0}
                    # "882": { "name": "Radaway", "description": "Use a Neumune Tablet to reduce radiation poisoning", "type": 16,
                    type = "Medical items"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [7]:
                    # 7 {'name': 'Magical Veins', 'description': 'Use 5,000 medical items', 'type': 15, 'circulation': 4686, 'rarity': 'Rare', 'awardType': 'Honor', 'achieve': 0}
                    type = "Medical items"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("medicalitemsused", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["left"] = max((vp["goal"] - vp["current"]) / 24, 0)
                    vp["comment"] = "Using 1h cooldown blood bags"
                    awards[type]["h_" + k] = vp

                elif int(k) in [1]:
                    # 1 {'name': "I'm Watching You", 'description': 'Find 50 items in the city', 'type': 16, 'circulation': 26943, 'rarity': 'Common', 'awardType': 'Honor', 'achieve': 0}
                    type = "City"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("cityfinds", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / daysOld
                    vp["left"] = max((vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    vp["comment"] = "With a current ratio of {:.2g} finds / day.".format(ratio)
                    awards[type]["h_" + k] = vp

                elif int(k) in [238]:
                    # 238 {'name': 'Optimist', 'description': 'Find 1,000 items in the dump', 'type': 16, 'circulation': 5850, 'rarity': 'Limited', 'awardType': 'Honor', 'achieve': 0}
                    type = "City"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("dumpfinds", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    days = dLeftE(max(5 * (vp["goal"] - vp["current"]), 0))
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [271]:
                    # 271 {'name': 'Eco Friendly', 'description': 'Trash 5,000 items', 'type': 16, 'circulation': 14796, 'rarity': 'Uncommon', 'awardType': 'Honor', 'achieve': 0}
                    type = "City"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("itemsdumped", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["left"] = max((vp["goal"] - vp["current"]), 0)
                    awards[type]["h_" + k] = vp

                elif int(k) in [743]:
                    # "name": "Lavish", "description": "Dump an item with a current market value of at least $1,000,000", "type": 16,
                    type = "City"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [699]:
                    # "699": {"name": "Collector","description": "Maintain an impressive display case of collectible items", "type": 16,
                    type = "Other Items"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [273]:
                    # 273 {'name': 'Bargain Hunter', 'description': 'Win 10 auctions', 'type': 16, 'circulation': 8415, 'rarity': 'Limited', 'awardType': 'Honor', 'achieve': 0}
                    type = "Other Items"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("auctionswon", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp

                elif int(k) in [216]:
                    # 216 {'name': 'Silicon Valley', 'description': 'Code 100 viruses', 'type': 0, 'circulation': 3627, 'rarity': 'Rare', 'awardType': 'Honor', 'img': 539384064, 'title': 'Silicon Valley [216]: Rare (3627)'}
                    type = "Other Items"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("virusescoded", 0)
                    c = 1.
                    coding_perks = []
                    for p in userInfo.get("education_perks", []):
                        if "virus coding time" == p[6:].lower():
                            split_perk = p.strip().split(" ")
                            r = float(split_perk[1].replace("%", "")) / 100.
                            c *= (1. - r)
                            coding_perks.append("education ({}%)".format(int(r * 100)))
                            break
                    for p in userInfo.get("company_perks", []):
                        if "virus coding time reduction" == p[6:].lower():
                            c *= 0.5
                            coding_perks.append("job (50%)")
                            break
                    for p in userInfo.get("stock_perks", []):
                        if "(IIL)" == p.strip().split(" ")[-1]:
                            c *= 0.5
                            coding_perks.append("stock (50%)")
                            break
                    t = max(1, int(c * 10))
                    coding_perks = ", ".join(coding_perks) if len(coding_perks) else "no perks"
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["left"] = max(t * (vp["goal"] - vp["current"]), 0)
                    s1 = "" if vp["left"] == 1 else "s"
                    s2 = "" if t == 1 else "s"
                    vp["comment"] = "{:.1f} days coding simple viruses in {} day{} ({})".format(vp["left"], t, s2, coding_perks)
                    awards[type]["h_" + k] = vp

                elif int(k) in [527]:
                    # 527 {'name': 'Worth it', 'description': 'Use a stat enhancer', 'type': 16, 'circulation': 698, 'rarity': 'Extraordinary', 'awardType': 'Honor', 'achieve': 0}
                    type = "Consume"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["current"] = userInfo.get("personalstats", dict({})).get("statenhancersused", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp

                elif int(k) in [534]:
                    # 534 {'name': 'Alcoholic', 'description': 'Drink 500 bottles of alcohol', 'type': 16, 'circulation': 7842, 'rarity': 'Limited', 'awardType': 'Honor', 'achieve': 0}
                    type = "Consume"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("alcoholused", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["left"] = max(0.5 * (vp["goal"] - vp["current"]) / 24, 0)
                    vp["comment"] = "Using 1h cooldown bottles"
                    awards[type]["h_" + k] = vp

                elif int(k) in [537]:
                    # 537 {'name': 'Diabetic', 'description': 'Eat 500 bags of candy', 'type': 16, 'circulation': 7948, 'rarity': 'Limited', 'awardType': 'Honor', 'achieve': 0}
                    type = "Consume"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("candyused", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["left"] = max(0.5 * (vp["goal"] - vp["current"]) / 24, 0)
                    vp["comment"] = "Using 30min cooldown sweets"
                    awards[type]["h_" + k] = vp

                elif int(k) in [538]:
                    # 538 {'name': 'Sodaholic', 'description': 'Drink 500 cans of energy drink', 'type': 16, 'circulation': 898, 'rarity': 'Extraordinary', 'awardType': 'Honor', 'achieve': 0}
                    type = "Consume"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("energydrinkused", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["left"] = max(2 * (vp["goal"] - vp["current"]) / 24, 0)
                    vp["comment"] = "Using 2h cooldown cans"
                    awards[type]["h_" + k] = vp

                elif int(k) in [539]:
                    # 539 {'name': 'Bibliophile', 'description': 'Read 10 books', 'type': 16, 'circulation': 384, 'rarity': 'Extraordinary', 'awardType': 'Honor', 'achieve': 0}
                    type = "Consume"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    icons = userInfo.get("icons")
                    bookIcon = icons.get("icon68", False) if isinstance(icons, dict) else False
                    if bookIcon:
                        tmp = bookIcon.split("-")[-1].strip().split(",")
                        currentBook = 31. - float(tmp[0].split()[0]) + float(tmp[1].split()[0]) / 24. + float(tmp[2].split()[0]) / 24. / 60.
                    else:
                        currentBook = 0
                    vp["current"] = userInfo.get("personalstats", dict({})).get("booksread", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["left"] = max(31 * (vp["goal"] - vp["current"]) - currentBook, 0)
                    vp["comment"] = "Currently reading {:.02f} days of a book".format(currentBook)
                    awards[type]["h_" + k] = vp

                elif int(k) in [678, 716, 717]:
                    # "678": {"name": "Stinker", "description": "Successfully prank someone with Stink Bombs", "type": 16}
                    # "716": {"name": "Wipeout", "description": "Successfully prank someone with Toilet Paper", "type": 16,
                    # "717": { "name": "Foul Play", "description": "Successfully prank someone with Dog Poop", "type": 16 }
                    type = "Pranks"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

        for k, v in tornAwards["medals"].items():
            if v["type"] == "OTR":
                vp = v
                # vp["left"] = 0
                # vp["comment"] = ["", int(k)]
                vp["awardType"] = "Medal"
                vp["img"] = k
                if int(k) in medals_awarded:
                    vp["awarded_time"] = int(medals_time[medals_awarded.index(int(k))])
                else:
                    vp["awarded_time"] = 0

                if int(k) in [204, 205, 206]:
                    # 204 {'name': 'Watchful', 'description': 'Find 10 items in the city', 'type': 'OTR', 'awardType': 'Medal', 'goal': 10, 'current': 0, 'achieve': 0.0}
                    type = "City"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("cityfinds", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / daysOld
                    vp["left"] = max((vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    vp["comment"] = "With a current ratio of {:.2g} finds / day.".format(ratio)
                    awards[type]["m_" + k] = vp

                elif int(k) in [198, 199, 200]:
                    # 198 {'name': 'Pin Cushion', 'description': 'Use 500 medical items', 'type': 'OTR', 'awardType': 'Medal', 'goal': 500, 'current': 0, 'achieve': 0.0}
                    type = "Medical items"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("medicalitemsused", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["left"] = max((vp["goal"] - vp["current"]) / 24, 0)
                    vp["comment"] = "Using 1h cooldown blood bags"
                    awards[type]["m_" + k] = vp

    elif category == "travel":

        awards = dict({
            "Destinations": dict(),
            "Time": dict(),
            "Import items": dict(),
            "Attacks abroad": dict(),
            "Hunting": dict()})

        pilot = 0.7 if "+ Access to airstrip" in userInfo.get("property_perks", []) else 1.0

        flightTimes = {
            "mextravel": 26,
            "caytravel": 35,
            "cantravel": 41,
            "hawtravel": 134,
            "lontravel": 159,
            "argtravel": 167,
            "switravel": 175,
            "japtravel": 225,
            "chitravel": 242,
            "dubtravel": 271,
            "soutravel": 297}

        for k, v in tornAwards["honors"].items():
            if int(v["type"]) in [3, 7]:
                vp = v
                # vp["left"] = 0
                # vp["comment"] = ["", int(k)]
                vp["awardType"] = "Honor"
                vp["img"] = str(honorsId.get(int(k), 0))
                if int(k) in honors_awarded:
                    vp["awarded_time"] = int(honors_time[honors_awarded.index(int(k))])
                else:
                    vp["awarded_time"] = 0

                if int(k) in [11, 165]:
                    # 11 {'name': 'Mile High Club', 'description': 'Travel 100 times', 'type': 7, 'circulation': 31338, 'rarity': 'Common', 'awardType': 'Honor', 'img': 241952085, 'title': 'Mile High Club [11]: Common (31338)'}
                    type = "Time"
                    vp["category"] = category
                    vp["subcategory"] = type
                    if 36 in medals_awarded:
                        daysSince15 = (tsnow() - int(medals_time[medals_awarded.index(36)])) / (3600. * 24)
                        vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                        vp["current"] = userInfo.get("personalstats", dict({})).get("traveltimes", 0)
                        vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                        ratio = vp["current"] / daysSince15
                        vp["left"] = max((vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                        vp["comment"] = "Current ratio of {:.2g} travels / day.".format(ratio)
                    else:
                        vp["current"] = 0
                        vp["achieve"] = 0
                        vp["comment"] = "You need to reach level 15 first"
                    awards[type]["h_" + k] = vp

                elif int(k) in [549, 567, 557]:
                    # 549 {'name': 'Tourist', 'description': 'Spend 7 days in the air', 'type': 7, 'circulation': 16881, 'rarity': 'Uncommon', 'awardType': 'Honor', 'img': 724568067, 'title': 'Tourist [549]: Uncommon (16881)'}
                    type = "Time"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    if 36 in medals_awarded:
                        daysSince15 = (tsnow() - int(medals_time[medals_awarded.index(36)])) / (3600. * 24)
                        secondsOfFlight = int(userInfo.get("personalstats", dict({})).get("traveltime", 0))
                        hoursOfFlight = float(secondsOfFlight / 3600.)
                        daysOfFlight = float(hoursOfFlight / 24.0)
                        vp["current"] = float("{:.1f}".format(daysOfFlight))
                        vp["achieve"] = min(1, daysOfFlight / float(vp["goal"]))
                        ratio = daysOfFlight / daysSince15
                        vp["left"] = float("{:.1f}".format(max(float(vp["goal"] - daysOfFlight) / ratio, 0.0)) if ratio > 0 else -1)
                        vp["comment"] = "Current ratio of {:.2g} hours / day<br>Current state {:.1f} / {} hours".format(ratio * 24, hoursOfFlight, vp["goal"] * 24)
                    else:
                        vp["current"] = 0
                        vp["achieve"] = 0
                        vp["comment"] = "You need to reach level 15 first"
                    awards[type]["h_" + k] = vp

                elif int(k) in [130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 272]:
                    # 130 {'name': 'Maradona', 'description': 'Travel to Argentina 50 times', 'type': 7, 'circulation': 10543, 'rarity': 'Limited', 'awardType': 'Honor', 'img': 697523940, 'title': 'Maradona [130]: Limited (10543)'}
                    type = "Destinations"
                    vp["category"] = category
                    vp["subcategory"] = type
                    if 36 in medals_awarded:
                        weirdkeys = {"135": "lontravel", "132": "dubtravel"}
                        key = v["description"].split(" ")[2].lower()[:3] + "travel"
                        key = weirdkeys.get(k, key)
                        vp["goal"] = int(v["description"].split(" ")[-2].replace(",", ""))
                        vp["current"] = int(userInfo.get("personalstats", dict({})).get(key, 0))
                        vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                        vp["left"] = max(2 * flightTimes[key] * pilot * (vp["goal"] - vp["current"]) / 1440., 0)
                        vp["comment"] = "With a one way travel of {:.0f} minutes".format(flightTimes[key] * pilot)
                    else:
                        vp["current"] = 0
                        vp["achieve"] = 0
                        vp["comment"] = "You need to reach level 15 first"
                    awards[type]["h_" + k] = vp

                elif int(k) in [50, 51, 52]:
                    # "50": {"name": "Zebra Skin", "description": "Achieve 50 skill in hunting", "type": 3, "circulation": 12118, "rarity": "Uncommon" },
                    type = "Hunting"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    # if int(k) == 50:
                    #     vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    #     vp["current"] = 1 if int(k) in honors_awarded else 0
                    #     vp["left"] = 0 if int(k) in honors_awarded else 13100
                    #     vp["comment"] = ["energy needed", "to go from 0 to 50"]
                    #
                    # elif int(k) == 51:
                    #     vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    #     vp["current"] = 1 if int(k) in honors_awarded else 0
                    #     if 50 in honors_awarded:
                    #         vp["left"] = 0 if int(k) in honors_awarded else 29700 - 13000
                    #         vp["comment"] = ["energy needed", "to go from 50 to 75"]
                    #     else:
                    #         vp["left"] = 0 if int(k) in honors_awarded else 29700
                    #         vp["comment"] = ["energy needed", "to go from 0 to 75"]
                    #
                    # elif int(k) == 52:
                    #     vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    #     vp["current"] = 1 if int(k) in honors_awarded else 0
                    #     if 51 in honors_awarded:
                    #         vp["left"] = 0 if int(k) in honors_awarded else 164800 - 29700
                    #         vp["comment"] = ["energy needed", "to go from 75 to 100"]
                    #     elif 50 in honors_awarded:
                    #         vp["left"] = 0 if int(k) in honors_awarded else 164800 - 13000
                    #         vp["comment"] = ["energy needed", "to go from 50 to 100"]
                    #     else:
                    #         vp["left"] = 0 if int(k) in honors_awarded else 164800
                    #         vp["comment"] = ["energy needed", "to go from 0 to 100"]
                    awards[type]["h_" + k] = vp

                elif int(k) in [541, 542, 543]:
                    # "541": { "name": "Mule", "description": "Import 100 items from abroad", "type": 7},
                    type = "Import items"
                    vp["category"] = category
                    vp["subcategory"] = type
                    if 36 in medals_awarded:
                        daysSince15 = (tsnow() - int(medals_time[medals_awarded.index(36)])) / (3600. * 24)
                        vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                        vp["current"] = int(userInfo.get("personalstats", dict({})).get("itemsboughtabroad", 0))
                        vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                        ratio = vp["current"] / daysOld
                        vp["left"] = max((vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                        vp["comment"] = "current ratio of {:.2g} items / day.".format(ratio)
                    else:
                        vp["current"] = 0
                        vp["achieve"] = 0
                        vp["comment"] = "You need to reach level 15 first"
                    awards[type]["h_" + k] = vp

                elif int(k) in [853]:
                    # "853": { "name": "Souvenir", "description": "Purchase the perfect souvenir abroad", "type": 7,
                    souvenir = {
                         0: "Mayan Statue (Mexico)",
                         1: "Hockey Stick (Canada)",
                         2: "Pele Charm (Hawaii)",
                         3: "Soccer Ball (Argentina)",
                         4: "Jade Buddha (China)",
                         5: "Maneki Neko (Japan)",
                         6: "Elephant Statue (South Africa)",
                         7: "Afro Comb (South Africa)",
                         8: "Compass (Argentina)",
                         9: "Sextant (UK)",
                        10: "Yucca Plant (Mexico)",
                        11: "Fire Hydrant (Canada)",
                        12: "Model Space Ship (UK)",
                        13: "Ship in a Bottle (UK)",
                        14: "Paper Weight (UK)",
                        15: "Tailors Dummy (UK)",
                        16: "Sumo Doll (Japan)",
                        17: "Chopsticks (Japan)",
                        18: "Dart Board (UK)",
                        19: "Crazy Straw (Mexico)",
                        20: "Sensu (Japan)",
                        21: "Yakitori Lantern (Japan)",
                        22: "Snowboard (Switzerland)",
                        23: "Steel Drum (Caymans)",
                        24: "Nodding Turtle (Caymans)",
                    }
                    id = int(userInfo.get("player_id", -1))
                    if id > 0:
                        vp["comment"] = "The perfect souvenir for you is: {}".format(souvenir[id % 25])

                    type = "Import items"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [846]:
                    # "846": { "name": "International", "description": "Defeat 100 people while abroad", "type": 7,
                    type = "Attacks abroad"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("attackswonabroad", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp

        for k, v in tornAwards["medals"].items():
            if v["type"] == "OTR":
                vp = v
                # vp["left"] = 0
                # vp["comment"] = ["", int(k)]
                vp["awardType"] = "Medal"
                vp["img"] = k
                if int(k) in medals_awarded:
                    vp["awarded_time"] = int(medals_time[medals_awarded.index(int(k))])
                else:
                    vp["awarded_time"] = 0

                if int(k) in [207, 208, 209]:
                    # 207 {'name': 'Frequent Flyer', 'description': 'Travel abroad 25 times', 'type': 'OTR', 'awardType': 'Medal', 'achieve': 0}
                    type = "Time"
                    vp["category"] = category
                    vp["subcategory"] = type
                    if 36 in medals_awarded:
                        daysSince15 = (tsnow() - int(medals_time[medals_awarded.index(36)])) / (3600. * 24)
                        vp["goal"] = int(v["description"].split(" ")[2].replace(",", ""))
                        vp["current"] = userInfo.get("personalstats", dict({})).get("traveltimes", 0)
                        vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                        ratio = vp["current"] / daysSince15
                        vp["left"] = max((vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                        vp["comment"] = "current ratio of {:.2g} travels / day.".format(ratio)
                    else:
                        vp["current"] = 0
                        vp["achieve"] = 0
                        vp["comment"] = "You need to reach level 15 first"
                    awards[type]["m_" + k] = vp

    elif category == "work":
        from awards.educations import educations

        awards = dict({
            "Bachelors": dict(),
            "Courses": dict(),
            "Working stats": dict(),
            "Job points": dict(),
            "City jobs": dict()})

        for k, v in tornAwards["honors"].items():
            if int(v["type"]) in [0, 4, 15]:
                vp = v
                # vp["left"] = 0
                # vp["comment"] = ["", int(k)]
                vp["awardType"] = "Honor"
                vp["img"] = str(honorsId.get(int(k), 0))
                if int(k) in honors_awarded:
                    vp["awarded_time"] = int(honors_time[honors_awarded.index(int(k))])
                else:
                    vp["awarded_time"] = 0

                # get time reduction
                educationTimeReduction = 1.0
                edu_red_perks = []
                for perks_string in ["merit_perks", "stock_perks", "job_perks"]:
                    edu_red_perks += [int(perk.replace("- ", "").split("%")[0]) for perk in [_ for _ in userInfo.get(perks_string, []) if 'Education length' in _]]

                for red in edu_red_perks:
                    educationTimeReduction *= (1. - float(red) / 100.)

                if int(k) in [53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64]:
                    # 53 {'name': 'Biology Bachelor', 'description': 'Complete all classes in Biology', 'type': 4, 'circulation': 28936, 'rarity': 'Common', 'awardType': 'Honor', 'img': None, 'title': 'Biology Bachelor [53]: Common (28936)'}
                    type = "Bachelors"
                    vp["category"] = category
                    vp["subcategory"] = type

                    eduBridge = {
                        "Biology": "Biology",
                        "Business": "Commerce",
                        "Combat": "Military Arts and Science",
                        "ICT": "Computer Science",
                        "Defense": "Self Defense",
                        "General": "General Studies",
                        "Fitness": "Health Sciences",
                        "History": "History",
                        "Law": "Law",
                        "Mathematics": "Mathematics",
                        "Psychology": "Psychological Sciences",
                        "Sports": "Sports Science"}

                    eduDic = {
                        "Commerce": list(range(1, 14)),
                        "History": list(range(14, 22)),
                        "Mathematics": list(chain([22], range(24, 34))),
                        "Biology": list(chain(range(34, 43), [127])),
                        "Sports Science": list(chain(range(43, 52), [126])),
                        "Computer Science": list(range(52, 63)),
                        "Psychological Sciences": list(range(63, 70)),
                        "Self Defense": list(range(70, 78)),
                        "Military Arts and Science": list(chain(range(78, 88), [125])),
                        "Law": list(range(88, 103)),
                        "Health Sciences": list(range(103, 112)),
                        "General Studies": list(range(112, 124))}

                    name = v["name"].split(" ")[0]
                    educationCompleted = userInfo.get("education_completed", [])
                    numberOfClasses = len(eduDic[eduBridge[name]])
                    numberOfClassesDone = 0
                    timeLeft = 0
                    for v in eduDic[eduBridge[name]]:
                        if int(v) in educationCompleted:
                            numberOfClassesDone += 1
                        else:
                            timeLeft += educations[str(v)]["duration"]
                    vp["goal"] = numberOfClasses
                    vp["current"] = numberOfClassesDone
                    vp["achieve"] = 1 if int(k) in honors_awarded else numberOfClassesDone / float(numberOfClasses)
                    vp["left"] = max(educationTimeReduction * timeLeft / (24. * 3600.), 0)
                    vp["comment"] = "{:.1f} days with {:.0f}% education length reduction".format(vp["left"], (1. - educationTimeReduction) * 100.)
                    awards[type]["h_" + k] = vp

                elif int(k) in [653, 659, 651, 656]:
                    # 653 {'name': 'Smart Alec', 'description': 'Complete 10 education courses', 'type': 4, 'circulation': 150699, 'rarity': 'Very Common', 'awardType': 'Honor', 'img': 872280837, 'title': 'Smart Alec [653]: Very Common (150699)'}
                    type = "Courses"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = len(userInfo.get("education_completed", []))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    i = 0
                    timeLeft = 0
                    edLeft = []
                    for a, b in sorted(educations.items(), key=lambda x: x[1]['duration'], reverse=False):
                        if int(a) not in userInfo.get("education_completed", []):
                            if i >= vp["goal"] - vp["current"]:
                                break
                            i += 1
                            timeLeft += educationTimeReduction * b["duration"]
                            edLeft.append("{} (tier {})".format(b.get('name', '?'), b.get('tier', 0)))
                    vp["left"] = max(educationTimeReduction * timeLeft / (24. * 3600.), 0)
                    vp["comment"] = "{:.1f} days taking the shortest courses left with {:.0f}% education length reduction: <br>- {}".format(vp["left"], (1. - educationTimeReduction) * 100., "<br>- ".join(edLeft))

                    awards[type]["h_" + k] = vp

                elif int(k) in [4, 164, 742]:
                    # "742": { "name": "Overtime", "description": "Use 10,000 job points", "type": 0, "circulation": 0, "rarity": "Unknown Rarity" },
                    type = "Job points"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("jobpointsused", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp

                elif int(k) in [220]:
                    # 220 {'name': 'The Affronted', 'description': 'Infuriate all interviewers in starter jobs', 'type': 0, 'circulation': 4630, 'rarity': 'Rare', 'awardType': 'Honor', 'img': 384148528, 'title': 'The Affronted [220]: Rare (4630)'}
                    type = "City jobs"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [525, 530, 533]:
                    # 525 {'name': 'Tireless', 'description': 'Attain 100,000 endurance', 'type': 4, 'circulation': 8731, 'rarity': 'Limited', 'awardType': 'Honor', 'img': None, 'title': 'Tireless [525]: Limited (8731)'}
                    # 530 {'name': 'Talented', 'description': 'Attain 100,000 intelligence', 'type': 4, 'circulation': 11171, 'rarity': 'Uncommon', 'awardType': 'Honor', 'img': None, 'title': 'Talented [530]: Uncommon (11171)'}
                    # 533 {'name': 'Tough', 'description': 'Attain 100,000 manual labour', 'type': 4, 'circulation': 7204, 'rarity': 'Limited', 'awardType': 'Honor', 'img': None, 'title': 'Tough [533]: Limited (7204)'}
                    type = "Working stats"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    key = "_".join(v["description"].split(" ")[2:]).replace("ou", "o")
                    vp["current"] = userInfo.get(key, 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["left"] = max((vp["goal"] - vp["current"]) / 50., 0)
                    vp["comment"] = "{:.1f} days if single daily train as primary stat".format(vp["left"])
                    awards[type]["h_" + k] = vp

                elif int(k) in [844]:
                    # "844": {"name": "Worker Bee","description": "Achieve 10,000 in any working stat","type": 4,
                    type = "Working stats"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = 0
                    for key in ["endurance", "intelligence", "manual_labor"]:
                        vp["current"] = max(vp["current"], userInfo.get(key, 0))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["left"] = max((vp["goal"] - vp["current"]) / 50., 0)
                    vp["comment"] = "{:.1f} days if single daily train as primary stat".format(vp["left"])
                    awards[type]["h_" + k] = vp

    elif category == "gym":

        gym_happy = get_happy(userInfo)
        gym_dot, gym_name = get_gym(userInfo)
        gym_bonus = get_bonus(userInfo)

        awards = dict({
            "Memberships": dict(),
            "Other Gym": dict(),
            "Defense": dict(),
            "Dexterity": dict(),
            "Speed": dict(),
            "Strength": dict(),
            "Total stats": dict()})

        # link to the 100m honor to track beginning of linear behaviour
        bridge = {"Total stats": 679,
                  "Defense": 640,
                  "Dexterity": 629,
                  "Speed": 506,
                  "Strength": 646}

        for k, v in tornAwards["honors"].items():
            if int(v["type"]) in [0, 10]:
                vp = v
                # vp["left"] = 0
                # vp["comment"] = ["", int(k)]
                vp["awardType"] = "Honor"
                vp["img"] = str(honorsId.get(int(k), 0))
                if int(k) in honors_awarded:
                    vp["awarded_time"] = int(honors_time[honors_awarded.index(int(k))])
                else:
                    vp["awarded_time"] = 0

                if int(k) in [240, 241, 242, 243, 297, 497, 505, 506, 635, 640, 643, 646, 686, 687, 694, 720, 723, 708, 629, 679, 721, 647, 550, 638, 498, 690, 704]:
                    # 240 {'name': 'Behemoth', 'description': 'Gain 1,000,000 defense', 'type': 10, 'circulation': 20913, 'rarity': 'Uncommon', 'awardType': 'Honor', 'img': 362146978, 'title': 'Behemoth [240]: Uncommon (20913)'}
                    type = "zzz".join(v["description"].split(" ")[2:]).title().replace("zzz", " ")
                    vp["category"] = category
                    vp["subcategory"] = type
                    stat = v["description"].split(" ")[2].lower()
                    # si = int(userInfo.get(stat, "0.0").split(".")[0])
                    si = int(str(userInfo.get(stat, 0)).replace(",", ""))
                    sf = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = si
                    vp["goal"] = sf
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))

                    if si < sf:
                        if stat == "total":
                            tmpBonus = 0.0
                            for tmpKey in ["speed", "strength", "dexterity", "defense"]:
                                if (1.0 + gym_bonus[tmpKey]) * gym_dot[tmpKey] > tmpBonus:
                                    key = tmpKey
                                    tmpBonus = (1.0 + gym_bonus[tmpKey]) * gym_dot[tmpKey]
                        else:
                            key = stat

                        if not round(gym_dot[key]):
                            vp["comment"] = "Impossible to train {} in this {}.".format(key, gym_name)
                        else:
                            energy_to_spend = bs_e(si, sf, H=gym_happy, B=gym_bonus[key], G=gym_dot[key])
                            perks = [gym_happy, 100 * gym_bonus[key], gym_dot[key], gym_name]
                            days = dLeftE(energy_to_spend, perks=perks)
                            vp["left"] = days[0]
                            vp["comment"] = days[1]

                    awards[type]["h_" + k] = vp

                elif int(k) in [233, 234, 235]:
                    # 233 {'name': 'Bronze Belt', 'description': 'Own all lightweight gym memberships', 'type': 10, 'circulation': 61239, 'rarity': 'Common', 'awardType': 'Honor', 'img': 439667520, 'title': 'Bronze Belt [233]: Common (61239)'}
                    type = "Memberships"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [888]:
                    # "888": { "name": "Nice", "description": "Nice", "type": 0,
                    type = "Other Gym"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    vp["comment"] = "<b>Current guess</b><br/>You need to have 5 instances of <tt>69</tt> or <tt>420</tt> in the digits of your battle stats with at least one of each.<br>Credit goes to them for figuring that out: https://www.torn.com/forums.php#/p=threads&f=2&t=16174336"
                    awards[type]["h_" + k] = vp

    elif category == "money":

        awards = dict({
            "Stocks": dict(),
            "Bank": dict(),
            "Estate": dict(),
            "Networth": dict(),
            "Casino": dict(),
            "Donations": dict(),
            "Other Money": dict()})

        for k, v in tornAwards["honors"].items():
            if int(v["type"]) in [0, 9, 14, 16]:
                vp = v
                # vp["left"] = 0
                # vp["comment"] = ["", int(k)]
                vp["awardType"] = "Honor"
                vp["img"] = str(honorsId.get(int(k), 0))
                if int(k) in honors_awarded:
                    vp["awarded_time"] = int(honors_time[honors_awarded.index(int(k))])
                else:
                    vp["awarded_time"] = 0

                if int(k) in [546]:
                    # 546 {'name': 'Dividend', 'description': 'Receive 100 stock payouts ', 'type': 14, 'circulation': 8295, 'rarity': 'Limited', 'awardType': 'Honor', 'img': 543547927, 'title': 'Dividend [546]: Limited (8295)'}
                    type = "Stocks"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("stockpayouts", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp

                elif int(k) in [3, 19, 546]:
                    # 3 {'name': 'Moneybags', 'description': 'Achieve excellent success in the stock market', 'type': 14, 'circulation': 20747, 'rarity': 'Uncommon', 'awardType': 'Honor', 'img': 234842928, 'title': 'Moneybags [3]: Uncommon (20747)'}
                    # 19 {'name': 'Stock Analyst', 'description': 'Buy and sell shares actively in the stock market', 'type': 14, 'circulation': 2446, 'rarity': 'Rare', 'awardType': 'Honor', 'img': 890959235, 'title': 'Stock Analyst [19]: Rare (2446)'}
                    type = "Stocks"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [869]:
            		# "869": { "name": "Monopoly", "description": "Own every stock benefit at the same time", "type": 14,
                    type = "Stocks"
                    vp["category"] = category
                    vp["subcategory"] = type

                    allStocks = {s.tAcronym: [s.tName, s.tRequirement, s.tCurrentPrice] for s in Stock.objects.filter(tId__gt=0)}
                    holdStock = [b.split("(")[1].replace(")", "").strip() for b in userInfo.get("stock_perks", [])]
                    lst = []
                    totalMoney = 0
                    requiredMoney = 0
                    for stock_id, v in allStocks.items():
                        cl = "valid" if stock_id in holdStock else "error"
                        bbPrice = v[1] * v[2]
                        totalMoney += v[1] * v[2]
                        if stock_id not in holdStock:
                            requiredMoney += v[1] * v[2]

                        lst.append('<span class={}>{}</span>: ${:,.0f}'.format(cl, stock_id, bbPrice))
                    vp["comment"] = "<br>".join(lst)

                    vp["goal"] = int(totalMoney)
                    vp["current"] = int(totalMoney) - int(requiredMoney)
                    vp["achieve"] = 1 if int(k) in honors_awarded else min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["head"] = "$"
                    awards[type]["h_" + k] = vp

                elif int(k) in [10]:
                    # 10 {'name': 'Green, Green Grass', 'description': 'Make an investment in the city bank of over $1,000,000,000', 'type': 14, 'circulation': 21990, 'rarity': 'Uncommon', 'awardType': 'Honor', 'img': 927018892, 'title': 'Green, Green Grass [10]: Uncommon (21990)'}
                    type = "Bank"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[-1].replace(",", "").replace("$", ""))
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = userInfo.get("networth", dict({})).get("bank", 0)
                    vp["head"] = "$"
                    awards[type]["h_" + k] = vp

                elif int(k) in [12]:
                    # 12 {'name': 'Pocket Money', 'description': 'Make an investment in the city bank', 'type': 14, 'circulation': 182442, 'rarity': 'Very Common', 'awardType': 'Honor', 'img': 533285823, 'title': 'Pocket Money [12]: Very Common (182442)'}
                    type = "Bank"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [8]:
                    # 8 {'name': 'Loan Shark', 'description': 'Achieve a high credit score with Duke', 'type': 14, 'circulation': 10499, 'rarity': 'Limited', 'awardType': 'Honor', 'img': 602403620, 'title': 'Loan Shark [8]: Limited (10499)'}
                    type = "Other Money"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [9, 258, 860]:
                    # 9 {'name': 'Luxury Real Estate', 'description': 'Buy an airstrip for a property', 'type': 0, 'circulation': 22735, 'rarity': 'Common', 'awardType': 'Honor', 'img': 442995373, 'title': 'Luxury Real Estate [9]: Common (22735)'}
                    # 258 {'name': 'The High Life', 'description': 'Own a yacht', 'type': 0, 'circulation': 9173, 'rarity': 'Limited', 'awardType': 'Honor', 'img': 780858042, 'title': 'The High Life [258]: Limited (9173)'}
                    # "860": { "name": "Landlord", "description": "Lease one of your properties to someone", "type": 0,
                    type = "Estate"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [239]:
                    # 239 {'name': 'Middleman', 'description': 'Have 100 customers buy from your bazaar', 'type': 16, 'circulation': 27683, 'rarity': 'Common', 'awardType': 'Honor', 'achieve': 0}
                    type = "Other Money"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("bazaarcustomers", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp

                elif int(k) in [268]:
                    # 268 {'name': 'Wholesaler', 'description': 'Sell 1,000 points on the market', 'type': 0, 'circulation': 29688, 'rarity': 'Common', 'awardType': 'Honor', 'img': 517070365, 'title': 'Wholesaler [268]: Common (29688)'}
                    type = "Other Money"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("pointssold", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp

                elif int(k) in [237, 269, 275, 276, 326, 327, 338, 427, 431, 437, 513, 519]:
                    # 237 {'name': 'Poker King', 'description': 'Earn a poker score of 10,000,000', 'type': 9, 'circulation': 2267, 'rarity': 'Rare', 'awardType': 'Honor', 'img': '/static/honors/tsimg/NQ5Yy.png', 'title': 'Poker King [237]: Rare (2267)'}
                    type = "Casino"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [520, 521, 523, 522]:
                    # 316 {'name': 'Forgiven', 'description': 'Be truly forgiven for all of your sins', 'type': 11, 'circulation': 5434, 'rarity': 'Rare', 'awardType': 'Honor', 'img': 240827340, 'title': 'Forgiven [316]: Rare (5434)'}
                    # "520": {"name": "Pious", "description": "Donate a total of $100,000 to the church", "type": 14, "circulation": 6088, "rarity": "Limited" },
                    type = "Donations"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

        for k, v in tornAwards["medals"].items():
            if v["type"] == "NTW":
                vp = v
                # vp["left"] = 0
                # vp["comment"] = ["", int(k)]
                vp["awardType"] = "Medal"
                vp["img"] = k
                if int(k) in medals_awarded:
                    vp["awarded_time"] = int(medals_time[medals_awarded.index(int(k))])
                else:
                    vp["awarded_time"] = 0

                if int(k) in [89, 90, 91, 92, 93, 94, 95, 96, 236, 237, 238, 239, 240, 241]:
                    # 89 {'name': 'Apprentice', 'description': 'Have a recorded networth value of $100,000 for at least 3 days', 'type': 'NTW', 'awardType': 'Medal'}
                    type = "Networth"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[6].replace(",", "").replace("$", ""))
                    vp["current"] = userInfo.get("networth", dict({})).get("total", 0)
                    vp["achieve"] = 1 if int(k) in userInfo.get("medals_awarded", []) else min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["wait"] = 1 if int(k) in userInfo.get("medals_awarded", []) else 0
                    vp["head"] = "$"
                    awards[type]["m_" + k] = vp

    elif category == "competitions":

        awards = dict({
            "Elimination": dict(),
            "Other Comp": dict(),
            "Token shop": dict(),
            "TC endurance": dict(),
            "Torn of the dead": dict(),
            "Trick or treats": dict(),
            "Dog tag": dict()})

        for k, v in tornAwards["honors"].items():
            if int(v["type"]) in [13]:
                vp = v
                # vp["left"] = 0
                # vp["comment"] = ["", int(k)]
                vp["awardType"] = "Honor"
                vp["img"] = str(honorsId.get(int(k), 0))
                if int(k) in honors_awarded:
                    vp["awarded_time"] = int(honors_time[honors_awarded.index(int(k))])
                else:
                    vp["awarded_time"] = 0

                if int(k) in [213, 222, 330]:
                    # 213 {'name': 'Allure', 'description': 'Participate in the Mr & Ms Torn competition', 'type': 13, 'circulation': 3928, 'rarity': 'Rare', 'awardType': 'Honor', 'img': 576433461, 'title': 'Allure [213]: Rare (3928)'}
                    # 222 {'name': 'Good Friday', 'description': 'Exchange all eggs for a gold one in the Easter egg hunt competition', 'type': 13, 'circulation': 14880, 'rarity': 'Uncommon', 'awardType': 'Honor', 'img': 566217580, 'title': 'Good Friday [222]: Uncommon (14880)'}
                    # 330 {'name': 'Champion', 'description': '', 'type': 13, 'circulation': 106, 'rarity': 'Extremely Rare', 'awardType': 'Honor', 'img': None, 'title': 'Champion [330]: Extremely Rare (106)'}
                    type = "Other Comp"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [964, 966, 969]:
            		# "964": { "name": "Something Humerus", "description": "Upgrade your Halloween Basket to Terrifying", "type": 13,
            		# "966": { "name": "Oh My Gourd!", "description": "Upgrade your Halloween Basket to Nightmarish", "type": 13,
            		# "969": { "name": "Phantastic", "description": "Upgrade your Halloween Basket to Frightful", "type": 13,
                    type = "Trick or treats"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [263, 306, 311]:
                    # 263 {'name': 'Survivor', 'description': 'Finish the Torn of the Dead competition as a civilian', 'type': 13, 'circulation': 1342, 'rarity': 'Extraordinary', 'awardType': 'Honor', 'img': None, 'title': 'Survivor [263]: Extraordinary (1342)'}
                    # 306 {'name': 'Resistance', 'description': 'Attack 50 zombies in the Torn of the Dead competition', 'type': 13, 'circulation': 3213, 'rarity': 'Rare', 'awardType': 'Honor', 'img': 412574893, 'title': 'Resistance [306]: Rare (3213)'}
                    # 311 {'name': 'Brainz', 'description': 'Infect 50 civilians in the Torn of the Dead competition', 'type': 13, 'circulation': 509, 'rarity': 'Extraordinary', 'awardType': 'Honor', 'img': None, 'title': 'Brainz [311]: Extraordinary (509)'}
                    type = "Torn of the dead"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [214, 224, 225, 278]:
                    # 214 {'name': 'Jack Of All Trades', 'description': 'Complete the 4th stage of the TC endurance challenge', 'type': 13, 'circulation': 12742, 'rarity': 'Uncommon', 'awardType': 'Honor', 'img': 241772067, 'title': 'Jack Of All Trades [214]: Uncommon (12742)'}
                    # 224 {'name': 'Proven Capacity', 'description': 'Complete the 5th stage of the TC endurance challenge', 'type': 13, 'circulation': 6144, 'rarity': 'Limited', 'awardType': 'Honor', 'img': None, 'title': 'Proven Capacity [224]: Limited (6144)'}
                    # 225 {'name': 'Master Of One', 'description': 'Complete the endurance challenge bonus task', 'type': 13, 'circulation': 5286, 'rarity': 'Rare', 'awardType': 'Honor', 'img': None, 'title': 'Master Of One [225]: Rare (5286)'}
                    # 278 {'name': 'Globally Effective', 'description': 'Complete the 6th stage of the TC endurance challenge', 'type': 13, 'circulation': 4941, 'rarity': 'Rare', 'awardType': 'Honor', 'img': None, 'title': 'Globally Effective [278]: Rare (4941)'}
                    type = "TC endurance"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [215, 281, 283, 284, 294, 297, 298, 308, 313, 315, 318, 321, 729, 730]:
                    # 215 {'name': 'Labyrinth', 'description': 'Purchased from the Token Shop', 'type': 13, 'circulation': 4542, 'rarity': 'Rare', 'awardType': 'Honor', 'img': 431217843, 'title': 'Labyrinth [215]: Rare (4542)'}
                    type = "Token shop"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0

                    token = {
                        "Globule": 3,
                        "Retro": 4,
                        "Acute": 4,
                        "Serenity": 5,
                        "Futurity": 6,
                        "Constellations": 7,
                        "Parallel": 8,
                        "Labyrinth": 9,
                        "Glimmer": 10,
                        "Supernova": 12,
                        "Pepperoni": 13,
                        "Electric Dream": 15,
                        "Hairy": 5,
                        "Backdrop": 3}

                    # vp["left"] = (1 - vp["achieve"]) * token[v["name"]]
                    vp["comment"] = "Costs {} tokens".format(token[v["name"]])
                    awards[type]["h_" + k] = vp

                elif int(k) in [221, 277]:
                    # 221 {'name': 'KIA', 'description': 'Get 50 or more tags in the Dog Tag competition', 'type': 13, 'circulation': 5513, 'rarity': 'Rare', 'awardType': 'Honor', 'img': 844457156, 'title': 'KIA [221]: Rare (5513)'}
                    # 277 {'name': 'Departure', 'description': 'Get 250 or more tags in the Dog Tag competition', 'type': 13, 'circulation': 1279, 'rarity': 'Extraordinary', 'awardType': 'Honor', 'img': None, 'title': 'Departure [277]: Extraordinary (1279)'}
                    type = "Dog tag"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [226, 280, 279, 212]:
                    # 226 {'name': 'Purple Heart', 'description': 'Achieve 50 attacks against enemy team members in the Elimination competition', 'type': 13, 'circulation': 15101, 'rarity': 'Uncommon', 'awardType': 'Honor', 'img': 783491253, 'title': 'Purple Heart [226]: Uncommon (15101)'}
                    # 280 {'name': 'Supremacy', 'description': 'Finish the Elimination competition within the top 5% of attacking players in your team', 'type': 13, 'circulation': 4491, 'rarity': 'Rare', 'awardType': 'Honor', 'img': 790762265, 'title': 'Supremacy [280]: Rare (4491)'}
                    # 279 {'name': 'Domination', 'description': 'Finish the Elimination competition with your team in 1st place', 'type': 13, 'circulation': 2481, 'rarity': 'Rare', 'awardType': 'Honor', 'img': None, 'title': 'Domination [279]: Rare (2481)'}
                    # 212 {'name': 'Mission Accomplished', 'description': 'Finish the Elimination competition with your team in 1st, 2nd or 3rd', 'type': 13, 'circulation': 28864, 'rarity': 'Common', 'awardType': 'Honor', 'img': 153743487, 'title': 'Mission Accomplished [212]: Common (28864)'}
                    type = "Elimination"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

    elif category == "commitment":

        awards = dict({
            "Spouse": dict(),
            "Donator": dict(),
            "Age": dict(),
            "Level": dict(),
            "Rank": dict(),
            # "Faction": dict(),
            "Other Commitment": dict()})

        for k, v in tornAwards["honors"].items():
            if int(v["type"]) in [0, 11, 12]:
                vp = v
                # vp["left"] = 0
                # vp["comment"] = ["", int(k)]
                vp["awardType"] = "Honor"
                vp["img"] = str(honorsId.get(int(k), 0))
                if int(k) in honors_awarded:
                    vp["awarded_time"] = int(honors_time[honors_awarded.index(int(k))])
                else:
                    vp["awarded_time"] = 0

                if int(k) in [163, 162, 166]:
                    # 163 {'name': 'Fascination', 'description': 'Stay married for 250 days', 'type': 11, 'circulation': 75114, 'rarity': 'Very Common', 'awardType': 'Honor', 'img': 431464057, 'title': 'Fascination [163]: Very Common (75114)'}
                    # 162 {'name': 'Chasm', 'description': 'Stay married for 750 days', 'type': 11, 'circulation': 48240, 'rarity': 'Common', 'awardType': 'Honor', 'img': 636752583, 'title': 'Chasm [162]: Common (48240)'}
                    # 166 {'name': 'Stairway To Heaven', 'description': 'Stay married for 1,500 days', 'type': 11, 'circulation': 27557, 'rarity': 'Common', 'awardType': 'Honor', 'img': 507297243, 'title': 'Stairway To Heaven [166]: Common (27557)'}
                    type = "Spouse"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[-2].replace(",", ""))
                    vp["current"] = userInfo.get("married", dict({})).get("duration", 0)
                    vp["achieve"] = 1 if int(k) in honors_awarded else min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["left"] = max((vp["goal"] - vp["current"]), 0)
                    vp["comment"] = "{:.0f} days left... Hold on to your spouse.".format(vp["left"])
                    awards[type]["h_" + k] = vp

                elif int(k) in [245]:
                    # 245 {'name': 'Couch Potato', 'description': 'Achieve 1,000 hours of activity on Torn', 'type': 11, 'circulation': 8396, 'rarity': 'Limited', 'awardType': 'Honor', 'img': 965199742, 'title': 'Couch Potato [245]: Limited (8396)'}
                    type = "Other Commitment"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = int(userInfo.get("personalstats", dict({})).get("useractivity", 0) / 3600)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / daysOld
                    vp["left"] = max((vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    vp["comment"] = "With a current ratio of {:.2g} hours / day.".format(ratio)
                    awards[type]["h_" + k] = vp

                elif int(k) in [312]:
                    # 312 {'name': 'Time Traveller', 'description': 'Survive a Torn City restore', 'type': 0, 'circulation': 24165, 'rarity': 'Common', 'awardType': 'Honor', 'img': 834531746, 'title': 'Time Traveller [312]: Common (24165)'}
                    type = "Other Commitment"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [873]:
                    # "873": { "name": "Welcome", "description": "Be online every day for 100 days", "type": 11,
                    type = "Other Commitment"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 100
                    vp["current"] = int(userInfo.get("personalstats", dict({})).get("activestreak", 0))
                    vp["achieve"] = 1 if int(k) in honors_awarded else min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["comment"] = "Best streak: {:d}.".format(int(userInfo.get("personalstats", dict({})).get("bestactivestreak", 0)))
                    awards[type]["h_" + k] = vp

                elif int(k) in [3, 19, 546]:
                    type = "Spouse"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [13, 18, 259, 264, 265]:
                    # 18 {'name': 'Another Brick In The Wall', 'description': 'Reach level 10', 'type': 12, 'circulation': 197925, 'rarity': 'Very Common', 'awardType': 'Honor', 'img': 978797305, 'title': 'Another Brick In The Wall [18]: Very Common (197925)'}
                    type = "Level"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[-1])
                    vp["current"] = userInfo.get("level", 1)
                    vp["achieve"] = min(1, vp["current"] / float(vp["goal"]))
                    # vp["left"] = max(vp["goal"] - vp["current"], 0)
                    # vp["comment"] = ["level left", ""]
                    awards[type]["h_" + k] = vp

        for k, v in tornAwards["medals"].items():
            if v["type"] in ["CMT", "LVL", "RNK"]:
                vp = v
                # vp["left"] = 0
                # vp["comment"] = ["", int(k)]
                vp["awardType"] = "Medal"
                vp["img"] = k
                if int(k) in medals_awarded:
                    vp["awarded_time"] = int(medals_time[medals_awarded.index(int(k))])
                else:
                    vp["awarded_time"] = 0

                if int(k) in [74, 75, 76, 77, 78, 79, 80, 110, 111, 112, 113, 114, 115, 116, 156, 157, 158, 159, 160, 161, 162]:
                    # 74 {'name': 'Silver Anniversary', 'description': 'Stay married to a single person for 50 days without divorce', 'type': 'CMT', 'awardType': 'Medal'}
                    type = "Spouse"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[-4].replace(",", ""))
                    vp["current"] = userInfo.get("married", dict({})).get("duration", 0)
                    vp["achieve"] = 1 if int(k) in userInfo.get("medals_awarded", []) else min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["left"] = max((vp["goal"] - vp["current"]), 0)
                    vp["comment"] = "{:.0f} days left... Hold on to your spouse.".format(vp["left"])
                    awards[type]["m_" + k] = vp

                elif int(k) in [210, 211, 212, 213, 214]:
                    # 210 {'name': 'Citizenship', 'description': 'Be a donator for 30 days', 'type': 'CMT', 'awardType': 'Medal'}
                    type = "Donator"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[-2].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("daysbeendonator", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["left"] = max((vp["goal"] - vp["current"]), 0)
                    vp["comment"] = "{:.0f} days left.".format(vp["left"])
                    awards[type]["m_" + k] = vp

                elif int(k) in [225, 226, 227, 228, 229, 230, 231, 232, 234, 235]:
                    # 225 {'name': 'One Year of Service', 'description': 'Live in Torn for one year', 'type': 'CMT', 'awardType': 'Medal'}
                    type = "Age"
                    vp["category"] = category
                    vp["subcategory"] = type
                    str2int = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
                    vp["goal"] = str2int[v["description"].split(" ")[-2]]
                    tmp = daysOld / 365.
                    vp["achieve"] = min(1, tmp / float(vp["goal"]))
                    vp["current"] = float("{:.2f}".format(tmp))
                    vp["left"] = max(365 * vp["goal"] - daysOld, 0)
                    vp["comment"] = "{:.0f} days left man... No more, no less.".format(vp["left"])
                    awards[type]["m_" + k] = vp

                elif int(k) in [34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53]:
                    # 34 {'name': 'Level Five', 'description': 'Reach level Five', 'type': 'LVL', 'awardType': 'Medal'}
                    type = "Level"
                    vp["category"] = category
                    vp["subcategory"] = type
                    str2int = {"Five": 5, "Ten": 10, "Fifteen": 15, "Twenty": 20, "Twenty Five": 25, "Thirty": 30, "Thirty Five": 35, "Forty": 40, "Forty Five": 45, "Fifty": 50,
                               "Fifty Five": 55, "Sixty": 60, "Sixty Five": 65, "Seventy": 70, "Seventy Five": 75, "Eighty": 80, "Eighty Five": 85, "Ninety": 90, "Ninety Five": 95, "One Hundred": 100}
                    vp["goal"] = str2int[" ".join(v["description"].split(" ")[2:])]
                    vp["current"] = userInfo.get("level", 0)
                    vp["achieve"] = min(1, vp["current"] / float(vp["goal"]))
                    # vp["left"] = max(vp["goal"] - vp["current"], 0)
                    # vp["comment"] = ["level left", ""]
                    awards[type]["m_" + k] = vp

                elif int(k) in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]:
                    # 1 {'name': 'Beginner', 'description': 'Reach the rank of "Beginner"', 'type': 'RNK', 'awardType': 'Medal'}
                    type = "Rank"
                    vp["category"] = category
                    vp["subcategory"] = type
                    # vp["img"] = "https://www.torn.com/images/v2/main/medals/rank_slice.png"
                    # shift = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
                    # vp["shift"] = shift.index(int(k))
                    # vp["init"] = [0, 0]
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in [int(a) for a in userInfo.get("medals_awarded", [])] else 0
                    vp["current"] = 1 if int(k) in [int(a) for a in userInfo.get("medals_awarded", [])] else 0
                    awards[type]["m_" + k] = vp

                # elif int(k) in [26, 27, 28, 29, 108, 109, 148, 149, 150, 151]:
                #     # 26 {'name': 'Apprentice Faction Member', 'description': 'Serve 100 days in a single faction', 'type': 'CMT', 'awardType': 'Medal'}
                #     type = "Faction"
                vp["category"] = category
                vp["subcategory"] = type
                #     vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                #     vp["current"] = userInfo.get("faction", dict({})).get("days_in_faction", 0)
                #     vp["achieve"] = 1 if int(k) in userInfo.get("medals_awarded", []) else min(1, float(vp["current"]) / float(vp["goal"]))
                #     vp["left"] = max((vp["goal"] - vp["current"]), 0)
                #     vp["comment"] = vp["left"]
                #     awards[type]["m_" + k] = vp

    elif category == "miscellaneous":

        awards = dict({
            "Social": dict(),
            "Points": dict(),
            "Perks": dict(),
            "Racing": dict(),
            "Awards": dict(),
            "Missions": dict(),
            "Maximum": dict(),
            "Revives": dict(),
            "Events": dict(),
            "Other Misc": dict()})

        for k, v in tornAwards["honors"].items():
            if int(v["type"]) in [0, 2, 11, 14, 15, 17]:
                vp = v
                # vp["left"] = 0
                # vp["comment"] = ["", int(k)]
                vp["awardType"] = "Honor"
                vp["img"] = str(honorsId.get(int(k), 0))
                if int(k) in honors_awarded:
                    vp["awarded_time"] = int(honors_time[honors_awarded.index(int(k))])
                else:
                    vp["awarded_time"] = 0

                if int(k) in [5, 167, 217, 218, 219, 223, 246]:
                    # 5 {'name': 'Journalist', 'description': 'Have an article accepted in the newspaper', 'type': 0, 'circulation': 138, 'rarity': 'Extremely Rare', 'awardType': 'Honor', 'img': None, 'title': 'Journalist [5]: Extremely Rare (138)'}
                    # 167 {'name': 'Velutinous', 'description': 'Have a comic accepted in the newspaper', 'type': 0, 'circulation': 114, 'rarity': 'Extremely Rare', 'awardType': 'Honor', 'img': 363324386, 'title': 'Velutinous [167]: Extremely Rare (114)'}
                    # 217 {'name': "Two's Company", 'description': 'Refer one friend to Torn', 'type': 11, 'circulation': 13121, 'rarity': 'Uncommon', 'awardType': 'Honor', 'img': 438803717, 'title': "Two's Company [217]: Uncommon (13121)"}
                    # 218 {'name': "Three's a Crowd", 'description': 'Refer two friends to Torn', 'type': 11, 'circulation': 5404, 'rarity': 'Rare', 'awardType': 'Honor', 'img': 294488415, 'title': "Three's a Crowd [218]: Rare (5404)"}
                    # 219 {'name': 'Social Butterfly', 'description': 'Refer three friends to Torn', 'type': 11, 'circulation': 3037, 'rarity': 'Rare', 'awardType': 'Honor', 'img': 534607883, 'title': 'Social Butterfly [219]: Rare (3037)'}
                    # 223 {'name': 'The Socialist', 'description': 'Achieve level 5 on facebook Torn', 'type': 11, 'circulation': 16222, 'rarity': 'Uncommon', 'awardType': 'Honor', 'img': 350797134, 'title': 'The Socialist [223]: Uncommon (16222)'}
                    # 246 {'name': 'Pyramid Scheme', 'description': 'Have one of your referrals refer 5 Other players', 'type': 11, 'circulation': 1041, 'rarity': 'Extraordinary', 'awardType': 'Honor', 'img': 536984897, 'title': 'Pyramid Scheme [246]: Extraordinary (1041)'}
                    type = "Social"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [23, 267]:
                    # 23 {'name': 'Florence Nightingale', 'description': 'Revive 500 people', 'type': 15, 'circulation': 1053, 'rarity': 'Extraordinary', 'awardType': 'Honor', 'img': None, 'title': 'Florence Nightingale [23]: Extraordinary (1053)'}
                    type = "Revives"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("revives", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    er = 75
                    for perk in userInfo.get("faction_perks", []):
                        start, end = " ".join(perk.split(" ")[:-1]), perk.split(" ")[-1]
                        er = float(end) if start == "+ Reduces the energy used while reviving to" else er
                    days = dLeftE(max(er * (vp["goal"] - vp["current"]), 0), c="With {} energy / revive".format(er))
                    vp["left"] = days[0]
                    vp["comment"] = days[1]
                    awards[type]["h_" + k] = vp

                elif int(k) in [322, 870, 863]:
                    # 322: {"name": "Miracle Worker","description": "Revive 10 people within 10 minutes","type": 15,
                    # "870": { "name": "Resurrection", "description": "Revive someone you've just defeated", "type": 15,
                    # "863": { "name": "Crucifixion", "description": "Defeat someone you've just revived", "type": 15,
                    type = "Revives"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [316, 845]:
                    # 316 {'name': 'Forgiven', 'description': 'Be truly forgiven for all of your sins', 'type': 11, 'circulation': 5434, 'rarity': 'Rare', 'awardType': 'Honor', 'img': 240827340, 'title': 'Forgiven [316]: Rare (5434)'}
                    # "845": {"name": "Historian", "description": "Read a chronicle", "type": 0,
                    type = "Other Misc"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [839]:
                    # "839": {"name": "RNG","description": "Who knows?","type": 0,
                    type = "Other Misc"
                    vp["category"] = category
                    vp["subcategory"] = type
                    if int(k) in honors_awarded:
                        vp["goal"] = 1
                        vp["current"] = 1
                        vp["achieve"] = 1
                    else:
                        rng = random.randint(1, 41)
                        vp["goal"] = 42
                        vp["current"] = rng
                        vp["achieve"] = rng / 42.0
                        npcs = ["Amanda [7]", "Jimmy [19]", "Leslie [15]", "Duke [4]"]
                        lst = ["<b>Kivou's 4 steps to RNG:</b>",
                               "1. Read the description and learn what RNG means",
                               "2. Send ${:,d} to {}".format(random.randint(1, 10000), random.choice(npcs)),
                               "3. Look at your progress change on YATA",
                               "4. Pause and ponder",
                               "<i>You might need to do these steps a couple of times.</i>"]
                        vp["comment"] = "<br>".join(lst)
                    awards[type]["h_" + k] = vp

                elif int(k) in [700]:
                    # "700": {"name": "Leaderboard","description": "Achieve top 250 in one of the personal Hall of Fame leaderboards","type": 0,"circulation": 0,
                    type = "Other Misc"
                    vp["category"] = category
                    vp["subcategory"] = type

                    top = int(vp["description"].split(" ")[2].replace(",", ""))

                    hof = userInfo.get("halloffame")
                    if hof is not None:
                        todel = []
                        for key, v in hof.items():
                            if not v["rank"] or key in ["respect"]:
                                todel.append(key)
                        for key in todel:
                            del hof[key]
                        hof = sorted(hof.items(), key=lambda x: -x[1]['rank'], reverse=True)

                    if hof is not None and len(hof):
                        vp["goal"] = top
                        vp["current"] = 1 if int(k) in honors_awarded else hof[0][1]["rank"]
                        vp["achieve"] = 1 if int(k) in honors_awarded else min(1, float(vp["goal"]) / float(vp["current"]))

                        vp["comment"] = "<br>".join(['<b class={}>{}</b>: #{:,d} ({:,d})'.format("error" if i else "valid", k.title(), v["rank"], v["value"]) for i, (k, v) in enumerate(hof)])

                    else:
                        vp["achieve"] = 1 if int(k) in honors_awarded else 0
                        vp["current"] = 1 if int(k) in honors_awarded else 0

                    awards[type]["h_" + k] = vp

                elif int(k) in [309, 443, 459, 375, 731]:
                    # 309 {'name': 'Christmas in Torn', 'description': 'Login on Christmas Day', 'type': 11,
                    # 443 {'name': 'Trick or Treat', 'description': 'Login on Halloween', 'type': 11,
                    # 459 {'name': 'Torniversary', 'description': 'Login on November 15th', 'type': 11,
                    # "375": { "name": "Resolution", "description": "Login on New Year's Day", "type": 11,
                    # "731": {"name": "Tornication", "description": "Login on Valentine's Day", "type": 11,
                    type = "Events"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [229, 606, 614]:
                    # 229 {'name': 'Seeker', 'description': 'Achieve 250 total awards', 'type': 0, 'circulation': 5633, 'rarity': 'Limited', 'awardType': 'Honor', 'img': 486362984, 'title': 'Seeker [229]: Limited (5633)'}
                    type = "Awards"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = len(honors_awarded) + len(userInfo.get("medals_awarded", []))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp

                elif int(k) in [274, 734]:
                    # 274 {'name': 'Redline', 'description': 'Win 250 races with a single car', 'type': 0, 'circulation': 3513, 'rarity': 'Rare', 'awardType': 'Honor', 'img': 739693375, 'title': 'Redline [274]: Rare (3513)'}
                    type = "Racing"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [572]:
                    # 572 {'name': 'Motorhead', 'description': 'Reach a racing skill of 10', 'type': 0, 'circulation': 1960, 'rarity': 'Extraordinary', 'awardType': 'Honor', 'img': None, 'title': 'Motorhead [572]: Extraordinary (1960)'}
                    type = "Racing"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 10
                    vp["current"] = userInfo.get("personalstats", dict({})).get("racingskill", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / daysOld
                    vp["left"] = max((vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    vp["comment"] = "With a current ratio of {:.2g} racing skills / day".format(ratio)
                    awards[type]["h_" + k] = vp

                elif int(k) in [581]:
                    # "581": {"name": "On Track", "description": "Earn 2,500 racing points","type": 0,
                    type = "Racing"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 2500
                    vp["current"] = userInfo.get("personalstats", dict({})).get("racingpointsearned", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / daysOld
                    vp["left"] = max((vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    vp["comment"] = "With a current ratio of {:.2g} racing points / day".format(ratio)
                    awards[type]["h_" + k] = vp

                elif int(k) in [571]:
                    # "571": { "name": "Chequered Past", "description": "Win 100 races", "type": 0,
                    type = "Racing"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("raceswon", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / daysOld
                    vp["left"] = max((vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    vp["comment"] = "With a current ratio of {:.2g} races won / day".format(ratio)
                    awards[type]["h_" + k] = vp

                elif int(k) in [21]:
                    # 21 {'name': 'Driving Elite', 'description': 'Reach racing class A', 'type': 0, 'circulation': 15853, 'rarity': 'Uncommon', 'awardType': 'Honor', 'img': 819611004, 'title': 'Driving Elite [21]: Uncommon (15853)'}
                    type = "Racing"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 475
                    vp["current"] = userInfo.get("personalstats", dict({})).get("racingpointsearned", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / daysOld
                    vp["left"] = max((vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    classes = {"D": 25, "C": 100, "B": 250, "A": 475}
                    cl = "E"
                    if vp["current"] > 24:
                        cl = "D"
                    if vp["current"] > 99:
                        cl = "C"
                    if vp["current"] > 249:
                        cl = "B"
                    if vp["current"] > 474:
                        cl = "A"
                    left = "<br>".join(["- Class {} ({} points): {} left".format(k, v, v - vp["current"]) for k, v in classes.items()])
                    vp["comment"] = "You're currently in class {}<br>with a current ratio of {:.2g} points / day<br>{}".format(cl, ratio, left)
                    awards[type]["h_" + k] = vp

                elif int(k) in [380, 395]:
                    # 380 {'name': 'Ecstatic', 'description': 'Achieve the maximum of 99,999 happiness', 'type': 0, 'circulation': 2153, 'rarity': 'Extraordinary', 'awardType': 'Honor', 'img': 462192588, 'title': 'Ecstatic [380]: Extraordinary (2153)'}
                    # 395 {'name': 'Energetic', 'description': 'Achieve the maximum of 1,000 energy', 'type': 0, 'circulation': 20651, 'rarity': 'Uncommon', 'awardType': 'Honor', 'img': 579593508, 'title': 'Energetic [395]: Uncommon (20651)'}
                    type = "Maximum"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [617]:
                    # 617 {'name': '10-Stack', 'description': 'Increase a merit upgrade to its maximum', 'type': 0, 'circulation': 33547, 'rarity': 'Common', 'awardType': 'Honor', 'img': 312084767, 'title': '10-Stack [617]: Common (33547)'}
                    type = "Maximum"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 10
                    n = 0
                    for _, nMerits in userInfo.get("merits", dict({})).items():
                        n = nMerits if int(nMerits) > n else n
                    vp["current"] = n
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [266, 334, 566]:
                    # 566 {'name': "You've Got Some Nerve", 'description': 'Refill your nerve bar 250 times', 'type': 0, 'circulation': 812, 'rarity': 'Extraordinary', 'awardType': 'Honor', 'img': 572050307, 'title': "You've Got Some Nerve [566]: Extraordinary (812)"}
                    # 266 {'name': 'Energize', 'description': 'Refill your energy bar 250 times', 'type': 0, 'circulation': 10237, 'rarity': 'Limited', 'awardType': 'Honor', 'img': 400884239, 'title': 'Energize [266]: Limited (10237)'}
                    # "334": { "name": "Compulsive", "description": "Refill your casino tokens 250 times", "type": 0,
                    type = "Points"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[-2].replace(",", ""))
                    splt = v["description"].split(" ")[2]
                    if splt == "nerve":
                        key = "nerverefills"
                    elif splt in "energy":
                        key = "refills"
                    elif splt in "casino":
                        key = "tokenrefills"
                    else:
                        key = "???"
                    vp["current"] = userInfo.get("personalstats", dict({})).get(key, 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["left"] = max(vp["goal"] - vp["current"], 0)
                    vp["comment"] = "With {} days of daily refill".format(vp["left"])
                    awards[type]["h_" + k] = vp

                elif int(k) in [288]:
                    # "288": { "name": "Fresh Start", "description": "Reset your merits", "type": 0,
                    type = "Points"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [244, 607, 620]:
                    # 607 {'name': 'Buffed', 'description': 'Achieve 50 personal perks', 'type': 0, 'circulation': 18274, 'rarity': 'Uncommon', 'awardType': 'Honor', 'img': 210452243, 'title': 'Buffed [607]: Uncommon (18274)'}
                    # 244 {'name': 'Web Of Perks', 'description': 'Achieve 100 personal perks', 'type': 0, 'circulation': 7466, 'rarity': 'Limited', 'awardType': 'Honor', 'img': 411243367, 'title': 'Web Of Perks [244]: Limited (7466)'}
                    # 620 {'name': 'OP', 'description': 'Achieve 150 personal perks', 'type': 0, 'circulation': 282, 'rarity': 'Extraordinary', 'awardType': 'Honor', 'img': None, 'title': 'OP [620]: Extraordinary (282)'}
                    type = "Perks"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    n = 0
                    for key_perk, perks in userInfo.items():
                        if key_perk.split("_")[-1] == "perks":
                            n += len(perks)
                    vp["current"] = n
                    vp["achieve"] = 1 if int(k) in honors_awarded else min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp

                elif int(k) in [371, 491, 851]:
                    # 371 {'name': 'Protege', 'description': 'Complete the mission Introduction: Duke', 'type': 17, 'circulation': 44516, 'rarity': 'Common', 'awardType': 'Honor', 'img': 668653618, 'title': 'Protege [371]: Common (44516)'}
                    # "491": { "name": "Modded","description": "Equip two high-tier mods to a weapon",
                    # "851": { "name": "Mod Boss", "description": "Own at least 20 weapon mods", "type": 2,
                    type = "Missions"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in honors_awarded else 0
                    vp["achieve"] = 1 if int(k) in honors_awarded else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [664]:
                    # "664": {"name": "Mercenary", "description": "Complete 1,000 contracts", "type": 17},
                    type = "Missions"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("contractscompleted", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / daysOld
                    vp["left"] = max((vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    vp["comment"] = "{:.1f} days with current ratio of {:.2g} contracts / day.".format(vp["left"], ratio)
                    awards[type]["h_" + k] = vp
                elif int(k) in [636]:
                    # "636": {"name": "Task Master", "description": "Earn 10,000 mission credits", "type": 17, "circulation": 3, "rarity": "Unknown Rarity"},
                    type = "Missions"
                    vp["category"] = category
                    vp["subcategory"] = type
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = userInfo.get("personalstats", dict({})).get("missioncreditsearned", 0)
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    ratio = vp["current"] / float(max(userInfo.get("personalstats", dict({})).get("contractscompleted", 0), 1))
                    vp["left"] = max((vp["goal"] - vp["current"]) / ratio, 0) if ratio > 0 else -1
                    vp["comment"] = "{:.1f} days with current ratio of {:.2g} credits / contract".format(vp["left"], ratio)
                    awards[type]["h_" + k] = vp

    # create summary
    awardsSummary = dict()
    nAwardedTot = 0
    nAwardsTot = 0
    for k, v in awards.items():
        nAwarded = 0
        for l, w in v.items():
            if w["achieve"] == 1:
                nAwarded += 1
        nAwards = len(v)
        awardsSummary[k] = {"nAwarded": nAwarded, "nAwards": nAwards}
        nAwardedTot += nAwarded
        nAwardsTot += nAwards
    awardsSummary["All awards"] = {"nAwarded": nAwardedTot, "nAwards": nAwardsTot}

    # handle double merits and next crimes
    doubled = []
    nextNerve = 9999999999  # lowest nerve left
    nextCrime = []  # list of next crime (if same lowest nerve)
    for subcat, aw in awards.items():
        for k1, v1 in aw.items():
            # special case for dirty bomb
            if k1 == "h_14":
                awards[subcat]["h_14"]["double"] = True
                awards[subcat]["h_156"]["double"] = True

            # special case for triple lvl 100
            if k1 == "h_264":
                awards[subcat]["h_264"]["triple"] = True
                awards[subcat]["h_265"]["triple"] = True
                awards[subcat]["m_53"]["triple"] = True

            for k2, v2 in aw.items():
                # if(k1 != k2 and v1.get("goal") == v2.get("goal") and v1.get("left") == v2.get("left") and k2 not in doubled and v1["awardType"] != v2["awardType"]):
                if(k1 != k2 and v1.get("goal") == v2.get("goal") and v1.get("left") == v2.get("left") and k2 not in doubled and v1["awardType"] != v2["awardType"]):
                    # ignore some honors
                    if k1 in ["h_906"] or k2 in ["h_906"]:
                        continue

                    awards[subcat][k1]["double"] = True
                    awards[subcat][k2]["double"] = True

                    if subcat == "crimes":
                        try:
                            awards[subcat][k1]["left"] /= 2.0
                            awards[subcat][k2]["left"] /= 2.0
                            awards[subcat][k1]["comment"][1] += "<br><i>Note: nerve needed / 2</i>"
                            awards[subcat][k2]["comment"][1] += "<br><i>Note: nerve needed / 2</i>"
                        except BaseException:
                            pass

                    doubled.append(k1)

            # next crime
            if v1["category"] == "crimes":
                if subcat != "Jail" and int(1000 * v1.get("left", 0)):
                    # multiply by 1000 in order to compare int and not floats
                    # so with a precision of E-3
                    if int(1000 * v1["left"]) < nextNerve:
                        nextCrime = [(subcat, k1)]
                        nextNerve = int(1000 * v1["left"])
                    elif int(1000 * v1["left"]) == nextNerve:
                        nextNerve = int(1000 * v1["left"])
                        nextCrime.append((subcat, k1))

    if category == "crimes":
        for (c, k) in nextCrime:
            awards[c][k]["next"] = True

    return awards, awardsSummary


def updatePlayerAwards(player, tornAwards, userInfo):
    import json

    medals = tornAwards["medals"]
    honors = tornAwards["honors"]
    remove = [k for k, v in honors.items() if v["type"] == 1]
    for k in remove:
        del honors[k]
    myMedals = userInfo.get("medals_awarded", [])
    myHonors = userInfo.get("honors_awarded", [])

    awards = dict()
    summaryByType = dict({})
    for type in AWARDS_CAT:
        awardsTmp, awardsSummary = createAwards(tornAwards, userInfo, type)
        summaryByType[type.title()] = awardsSummary["All awards"]
        awards.update(awardsTmp)

    summaryByType["AllAwards"] = {"nAwarded": len(myHonors) + len(myMedals), "nAwards": len(honors) + len(medals)}
    summaryByType["AllHonors"] = {"nAwarded": len(myHonors), "nAwards": len(honors)}
    summaryByType["AllMedals"] = {"nAwarded": len(myMedals), "nAwards": len(medals)}

    awardsJson = {"userInfo": userInfo,
                  "awards": awards,
                  "summaryByType": dict({k: v for k, v in sorted(summaryByType.items(), key=lambda x: x[1]['nAwarded'], reverse=True)})
                  }

    rScorePerso = 0.0
    for k, v in tornAwards["honors"].items():
        if v.get("achieve", 0) == 1:
            rScorePerso += v.get("rScore", 0)
    for k, v in tornAwards["medals"].items():
        if v.get("achieve", 0) == 1:
            rScorePerso += v.get("rScore", 0)

    # player.awardsJson = json.dumps(awardsJson)
    # player.awardsInfo = "{:.4f}".format(rScorePerso)
    player.awardsScor = int(rScorePerso * 10000)
    player.awardsUpda = int(timezone.now().timestamp())
    player.save()

    return awardsJson
