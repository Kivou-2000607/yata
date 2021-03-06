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

from yata.handy import *
from faction.models import *
from player.models import Player

import requests
import time
import numpy
import json
import random


# global bonus hits
BONUS_HITS = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000]
API_CODE_DELETE = [2, 7, 13]
OC_EFFICIENCY = {1: {"money": 5000, "respect": 1.0}, 2: {"money": 8750, "respect": 1.25}, 3: {"money": 16667, "respect": 1.11}, 4: {"money": 30000, "respect": 1.2}, 5: {"money": 141667, "respect": 1.17}, 6: {"money": 305556, "respect": 0.89}, 7: {"money": 892857, "respect": 1.79}, 8: {"money": 9375000, "respect": 9.38}}


POSTER_WIDTH = 750

def getBonusHits(hitNumber, ts):
    # new report timestamp based on ched annoncement date
    # https://www.torn.com/forums.php#!p=threads&t=16067103
    import datetime
    import time
    if int(ts) < int(time.mktime(datetime.datetime(2018, 10, 30, 15, 00).timetuple())):
        # bonus respect values are 4.2*2**n
        return 4.2 * 2**(1 + float([i for i, x in enumerate(BONUS_HITS) if x == int(hitNumber)][0]))
    else:
        # bonus respect values are 10*2**(n-1)
        return 10 * 2**(int([i for i, x in enumerate(BONUS_HITS) if x == int(hitNumber)][0]))


def getCrontabs():
    from faction.models import FactionData
    data = FactionData.objects.only("crontabs").first()
    crontabs = [] if data is None else json.loads(data.crontabs)
    return crontabs if len(crontabs) else [1]




# def updateFactionTree(faction, key=None, force=False, reset=False):
#     # it's not possible to delete all memebers and recreate the base
#     # otherwise the target list will be lost
#
#     now = int(timezone.now().timestamp())
#
#     # don't update if less than 24h ago and force is False
#     if not force and (now - faction.treeUpda) < 24 * 3600:
#         print("[function.chain.updateFactionTree] skip update tree")
#         if faction.simuTree in ["{}"]:
#             print("[function.chain.updateFactionTree] set simuTree as faction tree")
#             faction.simuTree = faction.factionTree
#             faction.save()
#         # return faction.faction.all()
#     else:
#
#         # call upgrade Tree
#         tornTree = json.loads(FactionData.objects.first().upgradeTree)
#         # basic needed for respect
#         # upgrades needed for upgrades daaa
#         # stats needed for challenges
#         factionCall = apiCall('faction', faction.tId, 'basic,upgrades,stats', key)
#         if 'apiError' in factionCall:
#             print("[function.chain.updateFactionTree] api key error {}".format(factionCall['apiError']))
#         else:
#             print("[function.chain.updateFactionTree] update faction tree")
#             factionTree = factionCall.get('upgrades')
#             orders = dict({})
#             for i in range(48):
#                 id = str(i + 1)
#
#                 # skip id = 8 for example #blameched
#                 if id not in tornTree:
#                     continue
#
#                 # create branches that are not in faction tree
#                 branch = tornTree[id]["1"]['branch']
#                 if id not in factionTree:
#                     factionTree[id] = {'branch': branch, 'branchorder': 0, 'branchmultiplier': 0, 'name': tornTree[id]["1"]['name'], 'level': 0, 'basecost': 0, 'challengedone': 0}
#
#                 # put core branch to branchorder 1
#                 if branch in ['Core']:
#                     factionTree[id]['branchorder'] = 1
#
#                 # consistency in the branchorder for the
#                 if branch in orders:
#                     orders[branch] = max(factionTree[id]['branchorder'], orders[branch])
#                 else:
#                     orders[branch] = factionTree[id]['branchorder']
#
#                 # set faction progress
#                 sub = "1"
#                 sub = "2" if id == "10" else sub  # chaining 1rt is No challenge
#                 sub = "3" if id == "11" else sub  # capacity 1rt and 2nd is No challenge
#                 sub = "2" if id == "12" else sub  # territory 1rt is No challenge
#                 ch = tornTree[id][sub]['challengeprogress']
#                 if ch[0] in ["age", "best_chain"]:
#                     factionTree[id]["challengedone"] = factionCall.get(ch[0], 0)
#                 elif ch[0] in ["members"]:
#                     factionTree[id]["challengedone"] = len(factionCall.get(ch[0], [1, 2]))
#                 elif ch[0] is None:
#                     factionTree[id]["challengedone"] = 0
#                 else:
#                     factionTree[id]["challengedone"] = factionCall["stats"].get(ch[0], 0)
#
#             for k in factionTree:
#                 factionTree[k]['branchorder'] = orders[factionTree[k]['branch']]
#
#             faction.factionTree = json.dumps(factionTree)
#             if reset:
#                 print("[function.chain.updateFactionTree] set simuTree as faction tree")
#                 faction.simuTree = faction.factionTree
#                 faction.save()
#             faction.treeUpda = now
#             faction.respect = int(factionCall.get('respect', 0))
#             faction.save()
#
#     return json.loads(faction.factionTree), json.loads(faction.simuTree)


def modifiers2lvl1(v):
    for tmpKey in ["fairFight", "war", "retaliation", "groupAttack", "overseas", "chainBonus"]:
        v[tmpKey] = float(v["modifiers"][tmpKey])
    del v["modifiers"]
    if v["stealthed"] and v["attacker_id"] == "":
        v["attacker_id"] = 0
        v["attacker_faction"] = 0
    return v


# def apiCallRevives(contract):
#     # shortcuts
#     faction = contract.faction
#     start = contract.start
#     end = contract.end if contract.end else int(timezone.now().timestamp())
#     # recompute last
#     tmp = contract.revive_set.order_by("-timestamp").first()
#     if tmp is not None:
#         last = tmp.timestamp
#     else:
#         last = contract.start
#
#     print("[function.chain.apiCallRevives] Contract from {} to {}".format(timestampToDate(start), timestampToDate(end)))
#
#     # add + 2 s to the endTS
#     end += 2
#
#     # get existing revives (just the ids)
#     revives = [r.tId for r in contract.revive_set.all()]
#     print("[function.chain.apiCallRevives] {} existing revives".format(len(revives)))
#
#     # # last timestamp
#     # if len(revives):
#     #     lastRevive = contract.revive_set.order_by("-timestamp").first()
#     #     last = lastRevive.timestamp
#     # else:
#     #     last = start
#
#     # get key
#     keys = faction.getAllPairs(enabledKeys=True)
#     if not len(keys):
#         print("[function.chain.apiCallRevives] no key for faction {}   --> deleting contract".format(faction))
#         contract.delete()
#         return False, "no key in faction {} (delete contract)".format(faction)
#
#     keyHolder, key = random.choice(keys)
#
#     # make call
#     selection = "revives,timestamp&from={}&to={}".format(last, end)
#     req = apiCall("faction", faction.tId, selection, key, verbose=True)
#
#     # in case there is an API error
#     if "apiError" in req:
#         print('[function.chain.apiCallRevives] api key error: {}'.format((req['apiError'])))
#         if req['apiErrorCode'] in API_CODE_DELETE:
#             print("[function.chain.apiCallRevives]    --> deleting {}'s key'".format(keyHolder))
#             faction.delKey(keyHolder)
#         return False, "wrong master key in faction {} for user {} (blank turn)".format(faction, keyHolder)
#
#     # try to catch cache response
#     tornTS = int(req["timestamp"])
#     nowTS = int(timezone.now().timestamp())
#     cacheDiff = abs(nowTS - tornTS)
#
#     apiRevives = req.get("revives")
#
#     # in case empty payload
#     if not len(apiRevives):
#         contract.computing = False
#         contract.save()
#         return False, "Empty payload (stop computing)"
#
#     print("[function.chain.apiCallRevives] {} revives from the API".format(len(apiRevives)))
#
#     print("[function.chain.apiCallRevives] start {}".format(timestampToDate(start)))
#     print("[function.chain.apiCallRevives] end {}".format(timestampToDate(end)))
#     print("[function.chain.apiCallRevives] last before the call {}".format(timestampToDate(last)))
#
#     newEntry = 0
#     for k, v in apiRevives.items():
#         ts = int(v["timestamp"])
#
#         # stop because out of bound
#         # probably because of cache
#         if ts < last or ts > end:
#             return False, "timestamp out of bound for faction {} with cacheDiff = {} (added {} entry before exiting)".format(faction, cacheDiff, newEntry)
#
#         if int(k) not in revives:
#             contract.revive_set.create(tId=int(k), **v)
#             newEntry += 1
#             last = max(last, ts)
#
#     print("[function.chain.apiCallRevives] last after the call {}".format(timestampToDate(last)))
#
#     # compute contract variables
#     revives = contract.revive_set.all()
#     contract.revivesContract = len(revives)
#     contract.first = revives.order_by("timestamp").first().timestamp
#     contract.last = revives.order_by("-timestamp").first().timestamp
#
#     if not newEntry and len(apiRevives) > 1:
#         return False, "No new entry for faction {} with cacheDiff = {} (continue)".format(faction, cacheDiff)
#
#     if len(apiRevives) < 2:
#         contract.computing = False
#
#     contract.save()
#     return True, "Everything's fine"


def updatePoster(faction):
    from django.conf import settings
    import os
    from PIL import Image
    from PIL import ImageDraw
    from PIL import ImageFont

    from io import BytesIO
    from django.core.files.base import ContentFile

    from faction.models import FONT_DIR

    url = os.path.join(settings.MEDIA_ROOT, f"poster/{faction.tId}.png")

    bridge = {"Criminality": 0,
              "Fortitude": 1,
              "Voracity": 2,
              "Toleration": 3,
              "Excursion": 4,
              "Steadfast": 5,
              "Aggression": 6,
              "Suppression": 7,
              }

    posterOpt = json.loads(faction.posterOpt)

    # get key
    key = faction.getKey()
    if key is None:
        faction.posterHold = False
        faction.poster = False
        faction.save()
        print("[function.faction.updatePoster] Faction {}: no key".format(faction))
        return 0

    # call for upgrades
    req = apiCall('faction', faction.tId, 'basic,upgrades', key.value, verbose=False)
    if 'apiError' in req and req['apiErrorCode'] in API_CODE_DELETE:
        faction.delKey(key=key)
        return 0

    key.lastPulled = tsnow()
    key.reason = "Faction -> poster"
    key.save()

    upgrades = req["upgrades"]

    # building upgrades tree
    tree = dict({})
    for k, upgrade in sorted(upgrades.items(), key=lambda x: x[1]['branchorder'], reverse=False):
        if upgrade['branch'] != 'Core':
            if tree.get(upgrade['branch']) is None:
                tree[upgrade['branch']] = dict({})
            tree[upgrade['branch']][upgrade['name']] = upgrade

    # create image background
    background = tuple(posterOpt.get('background', (0, 0, 0, 0)))
    main = Image.new('RGBA', (5000, 5000), color=background)

    # choose font
    fontFamily = posterOpt.get('fontFamily', [0])[0]
    fntId = {i: [f, int(f.split("__")[1].split(".")[0])] for i, f in enumerate(sorted(os.listdir(FONT_DIR)))}
    if fontFamily not in fntId:
        fontFamily = 0

    # fntId = {0: 'CourierPolski1941.ttf', 1: 'JustAnotherCourier.ttf'}
    # print("[function.chain.factionTree] fontFamily: {} {}".format(fontFamily, fntId[fontFamily]))
    fntBig = ImageFont.truetype(os.path.join(FONT_DIR, fntId[fontFamily][0]), fntId[fontFamily][1] + 10)
    fnt = ImageFont.truetype(os.path.join(FONT_DIR, fntId[fontFamily][0]), fntId[fontFamily][1])
    d = ImageDraw.Draw(main)

    fontColor = tuple(posterOpt.get('fontColor', (0, 0, 0, 255)))

    # FACTION PERKS POSTER

    # add title
    txt = "{}".format(req["name"])
    d.text((10, 10), txt, font=fntBig, fill=fontColor)
    x, y = d.textsize(txt, font=fntBig)

    txt = "{:,} respect\n".format(req["respect"])
    d.text((x + 20, 20), txt, font=fnt, fill=fontColor)
    x, y = d.textsize(txt, font=fntBig)

    iconType = posterOpt.get('iconType', [0])[0]
    for branch, upgrades in tree.items():
        icon = Image.open(os.path.join(settings.SRC_ROOT, f'posters/tier_unlocks_b{bridge[branch]}_t{iconType}.png'))
        icon = icon.convert("RGBA")
        main.paste(icon, (10, y), mask=icon)
        txt = ""
        txt += "  {}\n".format(branch)
        for k, v in upgrades.items():
            txt += "    {}: {}\n".format(k, v["ability"])
        txt += "\n"

        # txt = "a"
        d.text((90, 10 + y), txt, font=fnt, fill=fontColor)
        xTmp, yTmp = d.textsize(txt, font=fnt)
        x = max(xTmp, x)
        y += yTmp

        # print('[function.chain.factionTree] {} ({} upgrades)'.format(branch, len(upgrades)))

    main = main.crop((0, 0, x + 90 + 10, y))


    # resize main
    main_ratio = POSTER_WIDTH / float(main.size[0])
    main = main.resize((POSTER_WIDTH, int(main_ratio * main.size[1])))
    full_poster = [main]
    full_height = main.size[1]

    # check header
    if faction.posterHeadImg:
        head = Image.open(faction.posterHeadImg)
        head_ratio = POSTER_WIDTH / float(head.size[0])
        head = head.resize((POSTER_WIDTH, int(head_ratio * head.size[1])))
        full_poster.insert(0, head)
        full_height += head.size[1]

    if faction.posterTailImg:
        tail = Image.open(faction.posterTailImg)
        tail_ratio = POSTER_WIDTH / float(tail.size[0])
        tail = tail.resize((POSTER_WIDTH, int(tail_ratio * tail.size[1])))
        full_poster.append(tail)
        full_height += tail.size[1]


    print(full_poster)

    poster = Image.new('RGBA', (POSTER_WIDTH, full_height), color=background)

    for i, img_tmp in enumerate(full_poster):
        y = y + full_poster[i-1].size[1] if i else 0
        poster.paste(img_tmp, (0, y))

    f = BytesIO()
    try:
        faction.posterImg.delete()

        poster.save(f, format='png')
        faction.posterImg.save(f'posters/{faction.tId}.png', ContentFile(f.getvalue()))
        faction.posterImg.name = f'posters/{faction.tId}.png'
    finally:
        f.close()


    # FACTION GYM POSTER
    img_gym = Image.new('RGBA', (5000, 5000), color=background)
    gym_perks = {"STR": 0, "SPE": 0, "DEF": 0, "DEX": 0}

    for k, v in tree.get("Steadfast", {}).items():
        stat_type = k.split(" ")[0][:3].upper()
        gym_perks[stat_type] = v["level"]


    d = ImageDraw.Draw(img_gym)
    sep = [' ', '\n', ' ', '']
    txt = ''.join(f'{k} {v}%{s}' for s, (k, v) in zip(sep, gym_perks.items()))
    d.text((10, 5), txt, font=fntBig, fill=fontColor)
    x, y = d.textsize(txt, font=fntBig)
    img_gym = img_gym.crop((0, 0, x + 20 , y + 20))

    f = BytesIO()
    try:
        faction.posterGymImg.delete()

        img_gym.save(f, format='png')
        faction.posterGymImg.save(f'posters/{faction.tId}-gym.png', ContentFile(f.getvalue()))
        faction.posterGymImg.name = f'posters/{faction.tId}-gym.png'
    finally:
        f.close()

    faction.save()


def updatePosterConf(faction, post):
    t = post.get("t", False)
    p = int(post.get("p", False))

    # hexa color code
    if p == 4:
        hex = post.get("v").replace("#", "")[:8]
        if len(hex) == 4:
            tmp = hex
            hex = ""
            for i in range(4):
                hex += tmp[i] + tmp[i]

        elif len(hex) == 8:
            pass

        else:
            hex = "FFFFFFFF"

        try:
            int(hex, 16)
        except BaseException:
            hex = "FFFFFFFF"

        v = [int(hex[:2], 16), int(hex[2:4], 16), int(hex[4:6], 16), int(hex[6:8], 16)]

    # decimal for one color
    else:
        v = int(post.get("v", False))

    if t:
        posterOpt = json.loads(faction.posterOpt)
        if posterOpt.get(t, False):
            if p == 4:
                posterOpt[t] = v
            else:
                posterOpt[t][p] = v
        else:
            if t == "fontColor":
                if p == 4:
                    option = v
                else:
                    option = [0, 0, 0, 255]
                    option[p] = v
            elif t == "fontFamily":
                option = [0]
                option[p] = v
            elif t == "iconType":
                option = [0]
                option[p] = v
            elif t == "background":
                if p == 4:
                    option = v
                else:
                    option = [0, 0, 0, 0]
                    option[p] = v

            posterOpt[t] = option

        faction.posterOpt = json.dumps(posterOpt)
        faction.save()
