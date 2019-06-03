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

from yata.handy import apiCall
from yata.handy import timestampToDate
from chain.models import Member

import requests
import time
import numpy
import json


# global bonus hits
BONUS_HITS = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000]
API_CODE_DELETE = [2, 7]


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


def apiCallAttacks(faction, chain, key=None):
    # WARNING no fallback for this method if api crashed. Will yeld server error.
    # WINS = ["Arrested", "Attacked", "Looted", "None", "Special", "Hospitalized", "Mugged"]

    # get faction
    factionId = faction.tId
    beginTS = chain.start
    endTS = chain.end
    report = chain.report_set.first()

    # get all faction keys
    keys = faction.getAllPairs()

    # add + 2 s to the endTS
    endTS += 1

    # init
    chainDict = dict({})
    feedAttacks = True
    i = 1

    nAPICall = 0
    key = None
    tmp = ""
    while feedAttacks and nAPICall < faction.nAPICall:
        # try to get req from database
        tryReq = report.attacks_set.filter(tss=beginTS).first()

        if tryReq is None:
            if key is None:
                keyToUse = keys[i % len(keys)][1]
                print("[function.chain.apiCallAttacks] iteration #{}: API call using {} key".format(i, keys[i % len(keys)][0]))
            else:
                print("[function.chain.apiCallAttacks] iteration #{}: API call using personal key".format(i))
                keyToUse = key

            tsDiff = int(timezone.now().timestamp()) - faction.lastAPICall
            print("[function.chain.apiCallAttacks] \tLast API call: {}s ago".format(tsDiff))
            while tsDiff < 32:
                sleepTime = 32 - tsDiff
                print("[function.chain.apiCallAttacks] \tLast API call: {}s ago, sleeping for {} seconds".format(tsDiff, sleepTime))
                time.sleep(sleepTime)
                tsDiff = int(timezone.now().timestamp()) - faction.lastAPICall

            nAPICall += 1
            url = "https://api.torn.com/faction/{}?selections=attacks&key={}&from={}&to={}".format(faction.tId, keyToUse, beginTS, endTS)
            print("[function.chain.apiCallAttacks] \tFrom {} to {}".format(timestampToDate(beginTS), timestampToDate(endTS)))
            print("[function.chain.apiCallAttacks] \tnumber {}: {}".format(nAPICall, url.replace("&key=" + keyToUse, "")))
            req = requests.get(url).json()
            faction.lastAPICall = int(timezone.now().timestamp())
            faction.save()
            if 'error' in req:
                chainDict["apiError"] = "API error code {}: {}.".format(req["error"]["code"], req["error"]["error"])
                chainDict["apiErrorCode"] = int(req["error"]["code"])
                break

            attacks = req.get("attacks", dict({}))

            if len(attacks):
                report.attacks_set.create(tss=beginTS, tse=endTS, req=json.dumps([attacks]))

        else:
            print("[function.chain.apiCallAttacks] iteration #{} from database".format(i))
            print("[function.chain.apiCallAttacks] \tFrom {} to {}".format(timestampToDate(beginTS), timestampToDate(endTS)))
            attacks = json.loads(tryReq.req)[0]

        if json.dumps([attacks]) == tmp:
            print("[function.chain.apiCallAttacks] \tWarning same response as before")
            report.attacks_set.filter(tss=beginTS).all().delete()
            chainDict["error"] = "same response"
            break
        else:
            tmp = json.dumps([attacks])

        tableTS = []
        maxHit = 0
        if len(attacks):
            for j, (k, v) in enumerate(attacks.items()):
                if v["defender_faction"] != factionId:
                    chainDict[k] = v
                    maxHit = max(v["chain"], maxHit)
                    # print(v["timestamp_started"])
                    tableTS.append(v["timestamp_started"])
                    # beginTS = max(beginTS, v["timestamp_started"])
                    # feedattacks = True if int(v["timestamp_started"])-beginTS else False
                    # print(chain.nHits, v["chain"])
                # print(v["chain"], maxHit, chain.nHits)
            # if(len(attacks) < 2):
                # feedAttacks = False

            if chain.tId:
                feedAttacks = not chain.nHits == maxHit
            else:
                feedAttacks = len(attacks) > 95
            beginTS = max(tableTS)
            print("[function.chain.apiCallAttacks] \tattacks={} count={} beginTS={}, endTS={} feed={}".format(len(attacks), v["chain"], beginTS, endTS, feedAttacks))
            i += 1
        else:
            print("[function.chain.apiCallAttacks] call number {}: {} attacks".format(i, len(attacks)))
            feedAttacks = False

    if not chain.tId:
        try:
            report.attacks_set.last().delete()
            print('[function.chain.apiCallAttacks] Delete last attacks for live chains')
        except:
            pass

    return chainDict


def fillReport(faction, members, chain, report, attacks):

    # initialisation of variables before loop
    nWRA = [0, 0.0, 0]  # number of wins, respect and attacks
    bonus = []  # chain bonus
    attacksForHisto = []  # record attacks timestamp histogram

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
        attackers[m.tId] = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, m.daysInFaction, m.name, 0, 0]

    #  for debug
    # PRINT_NAME = {"Thiirteen": 0,}
    # chainIterator = []

    # loop over attacks
    lastTS = 0
    for k, v in sorted(attacks.items(), key=lambda x: x[1]['timestamp_ended'], reverse=False):
        attackerID = int(v['attacker_id'])
        attackerName = v['attacker_name']
        # if attacker part of the faction at the time of the chain
        if(int(v['attacker_faction']) == faction.tId):
            # if attacker not part of the faction at the time of the call
            if attackerID not in attackers:
                print('[function.chain.fillReport] hitter out of faction: {} [{}]'.format(attackerName, attackerID))
                attackers[attackerID] = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1, attackerName, 0, 0]  # add out of faction attackers on the fly

            attackers[attackerID][0] += 1
            nWRA[2] += 1

            # if it's a hit
            respect = float(v['respect_gain'])
            chainCount = int(v['chain'])
            # if respect > 0.0 and chainCount == 0:
            #     print("[function.chain.fillReport] Attack with respect but no hit {}:".format(k))
            #     for kk, vv in v.items():
            #         print("[function.chain.fillReport] \t{}: {}".format(kk, vv))
            if chainCount:
                # chainIterator.append(v["chain"])
                # print("Time stamp:", v['timestamp_ended'])

                # init lastTS for the first iteration of the loop
                lastTS = v['timestamp_ended'] if lastTS == 0 else lastTS

                # compute chain watcher version 2
                attackers[attackerID][11] += (v['timestamp_ended'] - lastTS)
                lastTS = v['timestamp_ended']

                attacksForHisto.append(v['timestamp_ended'])
                if attackerID in attackersHisto:
                    attackersHisto[attackerID].append(v['timestamp_ended'])
                else:
                    attackersHisto[attackerID] = [v['timestamp_ended']]

                nWRA[0] += 1
                nWRA[1] += respect

                if v['chain'] in BONUS_HITS:
                    attackers[attackerID][12] += 1
                    r = getBonusHits(v['chain'], v["timestamp_ended"])
                    print('[function.chain.fillReport] bonus {}: {} respects'.format(v['chain'], r))
                    bonus.append((v['chain'], attackerID, attackerName, respect, r))
                else:
                    attackers[attackerID][1] += 1
                    attackers[attackerID][2] += float(v['modifiers']['fairFight'])
                    attackers[attackerID][3] += float(v['modifiers']['war'])
                    attackers[attackerID][4] += float(v['modifiers']['retaliation'])
                    attackers[attackerID][5] += float(v['modifiers']['groupAttack'])
                    attackers[attackerID][6] += float(v['modifiers']['overseas'])
                    attackers[attackerID][7] += float(v['modifiers']['chainBonus'])
                    attackers[attackerID][8] += respect / float(v['modifiers']['chainBonus'])

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
    diff = max(int(chain.end - chain.start), 1)
    binsGapMinutes = 5
    while diff / (binsGapMinutes * 60) > 256:
        binsGapMinutes += 5

    bins = [chain.start]
    for i in range(256):
        add = bins[i] + (binsGapMinutes * 60)
        if add > chain.end:
            break
        bins.append(add)

    # bins = max(min(int(diff / (5 * 60)), 256), 1)  # min is to limite the number of bins for long chains and max is to insure minimum 1 bin
    print('[function.chain.fillReport] chain delta time: {} second'.format(diff))
    print('[function.chain.fillReport] histogram bins delta time: {} second'.format(binsGapMinutes * 60))
    print('[function.chain.fillReport] histogram number of bins: {}'.format(len(bins) - 1))
    histo, bin_edges = numpy.histogram(attacksForHisto, bins=bins)
    binsCenter = [int(0.5 * (a + b)) for (a, b) in zip(bin_edges[0:-1], bin_edges[1:])]
    chain.reportNHits = nWRA[0]
    if not chain.tId:
        chain.nHits = nWRA[0]  # update for live chains
        chain.respect = nWRA[1]  # update for live chains
    chain.nAttacks = nWRA[2]
    chain.graph = ','.join(['{}:{}'.format(a, b) for (a, b) in zip(binsCenter, histo)])
    chain.lastUpdate = int(timezone.now().timestamp())
    chain.save()

    # fill the database with counts
    print('[function.chain.fillReport] fill database with counts')
    report.count_set.all().delete()
    for k, v in attackers.items():
        # time now - chain end - days old: determine if member was in the fac for the chain
        delta = int(timezone.now().timestamp()) - chain.end - v[9] * 24 * 3600
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
        report.count_set.create(attackerId=k,
                                name=v[10],
                                hits=v[0],
                                wins=v[1],
                                fairFight=v[2],
                                war=v[3],
                                retaliation=v[4],
                                groupAttack=v[5],
                                overseas=v[6],
                                respect=v[8],
                                daysInFaction=v[9],
                                beenThere=beenThere,
                                graph=graphTmp,
                                watcher=watcher)

    # fill the database with bonus
    print('[function.chain.fillReport] fill database with bonus')
    report.bonus_set.all().delete()
    for b in bonus:
        report.bonus_set.create(hit=b[0], tId=b[1], name=b[2], respect=b[3], respectMax=b[4])

    return chain, report, (binsCenter, histo), chain.nHits <= nWRA[0]


def updateMembers(faction, key=None):
    # it's not possible to delete all memebers and recreate the base
    # otherwise the target list will be lost

    # # get key
    if key is None:
        name, key = faction.getRadomKey()
        print("[function.chain.updateMembers] using {} key".format(name))
    else:
        print("[function.chain.updateMembers] using personal key")

    # call members
    membersAPI = apiCall('faction', faction.tId, 'basic', key, sub='members')
    if 'apiError' in membersAPI:
        return membersAPI

    membersDB = faction.member_set.all()
    for m in membersAPI:
        memberDB = membersDB.filter(tId=m).first()
        if memberDB is not None:
            # print('[VIEW members] member {} [{}] updated'.format(membersAPI[m]['name'], m))
            memberDB.name = membersAPI[m]['name']
            memberDB.lastAction = membersAPI[m]['last_action']
            memberDB.daysInFaction = membersAPI[m]['days_in_faction']
            tmp = [s for s in membersAPI[m]['status'] if s]
            memberDB.status = ", ".join(tmp)
            memberDB.save()
            faction.membersUpda = int(timezone.now().timestamp())
        elif Member.objects.filter(tId=m).first() is not None:
            # print('[VIEW members] member {} [{}] change faction'.format(membersAPI[m]['name'], m))
            memberTmp = Member.objects.filter(tId=m).first()
            memberTmp.faction = faction
            memberTmp.name = membersAPI[m]['name']
            memberTmp.lastAction = membersAPI[m]['last_action']
            memberTmp.daysInFaction = membersAPI[m]['days_in_faction']
            tmp = [s for s in membersAPI[m]['status'] if s]
            memberTmp.status = ", ".join(tmp)
            memberTmp.save()
            faction.membersUpda = int(timezone.now().timestamp())
        else:
            # print('[VIEW members] member {} [{}] created'.format(membersAPI[m]['name'], m))
            tmp = [s for s in membersAPI[m]['status'] if s]
            faction.member_set.create(tId=m, name=membersAPI[m]['name'], lastAction=membersAPI[m]['last_action'], daysInFaction=membersAPI[m]['days_in_faction'], status=", ".join(tmp))

    # delete old members
    for m in membersDB:
        if membersAPI.get(str(m.tId)) is None:
            # print('[VIEW members] member {} deleted'.format(m))
            m.delete()

    faction.save()
    return faction.member_set.all()


def factionTree(faction, key=None):
    from django.conf import settings
    import os
    from PIL import Image
    from PIL import ImageDraw
    from PIL import ImageFont

    url = "{}/trees/{}.png".format(settings.STATIC_ROOT, faction.tId)
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
    if key is None:
        name, key = faction.getRadomKey()
        print("[function.chain.updateMembers] using {} key".format(name))
    else:
        print("[function.chain.updateMembers] using personal key")

    # call for upgrades
    upgrades = apiCall('faction', faction.tId, 'upgrades', key, sub='upgrades')
    if 'apiError' in upgrades:
        print('[function.chain.factionTree] api key error: {}'.format((upgrades['apiError'])))
        return 0

    faction = apiCall('faction', faction.tId, 'basic', key)
    if 'apiError' in faction:
        print('[function.chain.factionTree] api key error: {}'.format((faction['apiError'])))
        return 0

    # building upgrades tree
    tree = dict({})
    for k, upgrade in sorted(upgrades.items(), key=lambda x: x[1]['branchorder'], reverse=False):
        if upgrade['branch'] != 'Core':
            if tree.get(upgrade['branch']) is None:
                tree[upgrade['branch']] = dict({})
            tree[upgrade['branch']][upgrade['name']] = upgrade

    # create image background
    background = tuple(posterOpt.get('background', (0, 0, 0, 0)))
    print("[function.chain.factionTree] background color: {}".format(background))
    img = Image.new('RGBA', (5000, 5000), color=background)

    # choose font
    fontFamily = posterOpt.get('fontFamily', [0])[0]
    fntId = {i: [f, int(f.split("__")[1].split(".")[0])] for i, f in enumerate(sorted(os.listdir(settings.STATIC_ROOT + '/perso/font/')))}
    # fntId = {0: 'CourierPolski1941.ttf', 1: 'JustAnotherCourier.ttf'}
    print("[function.chain.factionTree] fontFamily: {} {}".format(fontFamily, fntId[fontFamily]))
    fntBig = ImageFont.truetype(settings.STATIC_ROOT + '/perso/font/' + fntId[fontFamily][0], fntId[fontFamily][1] + 10)
    fnt = ImageFont.truetype(settings.STATIC_ROOT + '/perso/font/' + fntId[fontFamily][0], fntId[fontFamily][1])
    d = ImageDraw.Draw(img)

    fontColor = tuple(posterOpt.get('fontColor', (0, 0, 0, 255)))
    print("[function.chain.factionTree] fontColor: {}".format(fontColor))

    # add title
    txt = "{}".format(faction["name"])
    d.text((10, 10), txt, font=fntBig, fill=fontColor)
    x, y = d.textsize(txt, font=fntBig)

    txt = "{:,} respect\n".format(faction["respect"])
    d.text((x + 20, 20), txt, font=fnt, fill=fontColor)
    x, y = d.textsize(txt, font=fntBig)

    iconType = posterOpt.get('iconType', [0])[0]
    print("[function.chain.factionTree] iconType: {}".format(iconType))
    for branch, upgrades in tree.items():
        icon = Image.open(settings.STATIC_ROOT + '/trees/tier_unlocks_b{}_t{}.png'.format(bridge[branch], iconType))
        icon = icon.convert("RGBA")
        img.paste(icon, (10, y), mask=icon)

        txt = ""
        txt += "  {}\n".format(branch)
        for k, v in upgrades.items():
            txt += "    {}: {}\n".format(k, v["ability"])
        txt += "\n"

        d.text((90, 10 + y), txt, font=fnt, fill=fontColor)
        xTmp, yTmp = d.textsize(txt, font=fnt)
        x = max(xTmp, x)
        y += yTmp

        print('[function.chain.factionTree] {} ({} upgrades)'.format(branch, len(upgrades)))

    # img.crop((0, 0, x + 90 + 10, y + 10 + 10)).save(url)
    img.crop((0, 0, x + 90 + 10, y)).save(url)
    print('[function.chain.factionTree] image saved {}'.format(url))
