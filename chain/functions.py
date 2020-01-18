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
from chain.models import FactionData
from chain.models import Member
from player.models import Player

import requests
import time
import numpy
import json
import random


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
    # get faction
    factionId = faction.tId
    beginTS = chain.start
    beginTSPreviousStep = 0
    endTS = chain.end
    report = chain.report_set.first()

    # get all faction keys
    keys = faction.getAllPairs(enabledKeys=True)

    # add + 2 s to the endTS
    endTS += 2

    # init variables
    chainDict = dict({})  # returned dic of attacks
    feedAttacks = True  # set if the report is over or not
    i = 1  # indice for the number of iteration (db + api calls)
    nAPICall = 0  # indice for the number of api calls
    tmp = ""

    allReq = report.attacks_set.all()
    while feedAttacks and nAPICall < faction.nAPICall:

        # SANITY CHECK 0: ask for same beginTS than previous chain
        # shouldn't happen because fedback = False if so (see below)
        if beginTS - beginTSPreviousStep <= 0:
            print("[function.chain.apiCallAttacks] \t[WARNING] will ask for same beginTS next iteration")

        # try to get req from database
        tryReq = allReq.filter(tss=beginTS).first()

        # take attacks from torn API
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
            print("[function.chain.apiCallAttacks] \tFrom {} to {}".format(timestampToDate(beginTS), timestampToDate(endTS)))
            # make the API call
            selection = "attacks,timestamp&from={}&to={}".format(beginTS, endTS)
            req = apiCall("faction", faction.tId, selection, keyToUse, verbose=False)

            # get timestamps
            reqTS = int(timezone.now().timestamp())
            tornTS = int(req.get("timestamp", 0))

            # save payload
            faction.lastAPICall = int(req.get("timestamp", reqTS))
            faction.save()

            # check if no api call
            if 'error' in req:
                chainDict["apiError"] = "API error code {}: {}.".format(req["error"]["code"], req["error"]["error"])
                chainDict["apiErrorCode"] = int(req["error"]["code"])
                break

            # get attacks from api request
            attacks = req.get("attacks", dict({}))

            print("[function.chain.apiCallAttacks] \ttornTS={}, reqTS={} diff={}".format(tornTS, reqTS, tornTS - reqTS))

            # SANITY CHECK 1: empty payload
            if not len(attacks):
                print("[function.chain.apiCallAttacks] \t[WARNING] empty payload (blank turn)")
                break

            # SANITY CHECK 2: api timestamp delayed from now
            elif abs(tornTS - reqTS) > 25:
                print("[function.chain.apiCallAttacks] \t[WARNING] returned cache response from API tornTS={}, reqTS={} (blank turn)".format(tornTS, reqTS))
                break

            # SANITY CHECK 3: check if payload different than previous call
            elif json.dumps([attacks]) == tmp:
                print("[function.chain.apiCallAttacks] \t[WARNING] same response as before (blank turn)")
                break

            else:
                tmp = json.dumps([attacks])

            # all tests passed: push attacks in the database
            report.attacks_set.create(tss=beginTS, tse=endTS, req=json.dumps([attacks]))

        # take attacks from the database
        else:
            print("[function.chain.apiCallAttacks] iteration #{} from database".format(i))
            print("[function.chain.apiCallAttacks] \tFrom {} to {}".format(timestampToDate(beginTS), timestampToDate(endTS)))
            attacks = json.loads(tryReq.req)[0]

        # filter all attacks and compute new TS
        beginTSPreviousStep = beginTS
        beginTS = 0
        chainCounter = 0
        for k, v in attacks.items():
            if v["defender_faction"] != factionId:
                chainDict[k] = v  # dictionnary of filtered attacks
                chainCounter = max(v["chain"], chainCounter)  # get max chain counter
                beginTS = max(v["timestamp_started"], beginTS)  # get latest timestamp

        # stoping criterion if same timestamp
        if beginTS - beginTSPreviousStep <= 0:
            feedAttacks = False
            print("[function.chain.apiCallAttacks] stopped chain because was going to ask for the same timestamp")

        # stoping criterion too many attack requests
        if i > 1500:
            feedAttacks = False
            print("[function.chain.apiCallAttacks] stopped chain because too many iterations")

        # stoping criterion for walls
        elif chain.wall:
            feedAttacks = len(attacks) > 10

        # stoping criterion for regular reports
        elif chain.tId:
            feedAttacks = not chain.nHits == chainCounter

        # stoping criterion for live reports
        else:
            feedAttacks = len(attacks) > 95

        print("[function.chain.apiCallAttacks] \tattacks={} chainCounter={} beginTS={}, endTS={} feed={}".format(len(attacks), chainCounter, beginTS, endTS, feedAttacks))
        i += 1

        # SANITY CHECK 4: check if timestamps are out of bounds
        if chain.start > beginTS or chain.end < beginTS:
            print("[function.chain.apiCallAttacks] ERRORS Attacks out of bounds: chain.starts = {} < beginTS = {} < chain.end = {}".format(chain.start, beginTS, endTS))
            print("[function.chain.apiCallAttacks] ERRORS Attacks out of bounds: chain.starts = {} < beginTS = {} < chain.end = {}".format(timestampToDate(chain.start), timestampToDate(beginTS), timestampToDate(endTS)))
            report.attacks_set.last().delete()
            print('[function.chain.apiCallAttacks] Deleting last attacks and exiting')
            return chainDict

    print('[function.chain.apiCallAttacks] stop iterating')

    # potentially delete last set of attacks for live chains
    if not chain.tId:
        try:
            lastAttacks = report.attacks_set.last()
            n = len(json.loads(lastAttacks.req)[0])
            if n < 100:
                lastAttacks.delete()
                print('[function.chain.apiCallAttacks] Delete last attacks for live chains')
            else:
                print('[function.chain.apiCallAttacks] Not delete last attacks for live chains since length = {}'.format(n))
        except BaseException:
            pass

    # special case for walls
    if chain.wall and not feedAttacks:
        print('[function.chain.apiCallAttacks] set chain createReport to False')
        chain.createReport = False
        chain.save()

    return chainDict


def fillReport(faction, members, chain, report, attacks):

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
    for k, v in sorted(attacks.items(), key=lambda x: x[1]['timestamp_ended'], reverse=False):
        attackerID = int(v['attacker_id'])
        attackerName = v['attacker_name']
        # if attacker part of the faction at the time of the chain
        if(int(v['attacker_faction']) == faction.tId):
            # if attacker not part of the faction at the time of the call
            if attackerID not in attackers:
                # print('[function.chain.fillReport] hitter out of faction: {} [{}]'.format(attackerName, attackerID))
                attackers[attackerID] = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1, attackerName, 0, 0, 0]  # add out of faction attackers on the fly

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
                timeSince = v['timestamp_ended'] - lastTS
                attackers[attackerID][11] += timeSince
                lastTS = v['timestamp_ended']

                # add to critical attack
                timeLeft = max(300 - timeSince, 0)
                if timeLeft < 30:
                    attacksCriticalForHisto["30"].append(v['timestamp_ended'])
                elif timeLeft < 60:
                    attacksCriticalForHisto["60"].append(v['timestamp_ended'])
                elif timeLeft < 90:
                    attacksCriticalForHisto["90"].append(v['timestamp_ended'])

                attacksForHisto.append(v['timestamp_ended'])
                if attackerID in attackersHisto:
                    attackersHisto[attackerID].append(v['timestamp_ended'])
                else:
                    attackersHisto[attackerID] = [v['timestamp_ended']]

                nWRA[0] += 1
                nWRA[1] += respect
                nWRA[3] = max(chainCount, nWRA[3])

                if v['chain'] in BONUS_HITS:
                    attackers[attackerID][12] += 1
                    r = getBonusHits(v['chain'], v["timestamp_ended"])
                    print('[function.chain.fillReport] bonus {}: {} respects'.format(v['chain'], r))
                    bonus.append((v['chain'], attackerID, attackerName, respect, r, v.get('defender_id', '0'), v.get('defender_name', 'Unkown')))
                else:
                    attackers[attackerID][1] += 1
                    attackers[attackerID][2] += float(v['modifiers']['fairFight'])
                    attackers[attackerID][3] += float(v['modifiers']['war'])
                    attackers[attackerID][4] += float(v['modifiers']['retaliation'])
                    attackers[attackerID][5] += float(v['modifiers']['groupAttack'])
                    attackers[attackerID][6] += float(v['modifiers']['overseas'])
                    attackers[attackerID][7] += float(v['modifiers']['chainBonus'])
                    attackers[attackerID][8] += respect / float(v['modifiers']['chainBonus'])
                    if float(v['modifiers']['war']) > 1.0:
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

    # fill attack histogram
    histo, bin_edges = numpy.histogram(attacksForHisto, bins=bins)
    binsCenter = [int(0.5 * (a + b)) for (a, b) in zip(bin_edges[0:-1], bin_edges[1:])]
    chain.graph = ','.join(['{}:{}'.format(a, b) for (a, b) in zip(binsCenter, histo)])

    # fill 30, 60, 90s critical attacks histogram
    histo30, _ = numpy.histogram(attacksCriticalForHisto["30"], bins=bins)
    histo60, _ = numpy.histogram(attacksCriticalForHisto["60"], bins=bins)
    histo90, _ = numpy.histogram(attacksCriticalForHisto["90"], bins=bins)
    chain.graphCrit = ','.join(['{}:{}:{}'.format(a, b, c) for (a, b, c) in zip(histo30, histo60, histo90)])

    chain.reportNHits = nWRA[0]
    if not chain.tId or chain.wall:
        chain.nHits = nWRA[0]  # update for live chains
        chain.respect = nWRA[1]  # update for live chains
    chain.nAttacks = nWRA[2]
    chain.lastUpdate = int(timezone.now().timestamp())
    chain.save()

    # fill the database with counts
    print('[function.chain.fillReport] fill database with counts')
    report.count_set.all().delete()
    hitsForStats = []
    for k, v in attackers.items():
        # for stats later
        if v[1]:
            hitsForStats.append(v[1])

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
        # 13: #war
        report.count_set.create(attackerId=k,
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
    graphStats = ','.join(['{}:{}'.format(a, b) for (a, b) in zip(statsBinsCenter, stats)])
    chain.graphStat = graphStats

    # fill the database with bonus
    print('[function.chain.fillReport] fill database with bonus')
    report.bonus_set.all().delete()
    for b in bonus:
        report.bonus_set.create(hit=b[0], tId=b[1], name=b[2], respect=b[3], respectMax=b[4], targetId=b[5], targetName=b[6])

    if chain.wall:
        finished = not chain.createReport
    else:
        # finished = chain.nHits <= nWRA[0]
        if nWRA[0] != nWRA[3]:
            print('[function.chain.fillReport] ERROR in counts: #Wins = {} and maxCount = {}'.format(nWRA[0], nWRA[3]))
        finished = chain.nHits <= nWRA[3]

    return chain, report, (binsCenter, histo), finished


def updateMembers(faction, key=None, force=True, indRefresh=False):
    # it's not possible to delete all memebers and recreate the base
    # otherwise the target list will be lost

    now = int(timezone.now().timestamp())

    # don't update if less than 1 hour ago and force is False
    if not force and (now - faction.membersUpda) < 3600:
        print("[function.chain.updateMembers] skip update member")
        return faction.member_set.all()

    # get key
    if key is None:
        name, key = faction.getRandomKey()
        print("[function.chain.updateMembers] using {} key".format(name))
    else:
        print("[function.chain.updateMembers] using personal key")

    # call members
    membersAPI = faction.updateMemberStatus()
    if 'apiError' in membersAPI:
        return membersAPI

    membersDB = faction.member_set.all()
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
            # print('[VIEW members] member {} [{}] change faction'.format(membersAPI[m]['name'], m))
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
            memberNew = faction.member_set.create(
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
            # print('[VIEW members] member {} deleted'.format(m))
            m.delete()

    # remove old AA keys
    for id, key in faction.getAllPairs():
        if not len(faction.member_set.filter(tId=id)):
            # print("[function.chain.updateMembers] delete AA key {}".format(id))
            faction.delKey(id)

    faction.membersUpda = now
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
        keyHolder, key = faction.getRandomKey()
        if keyHolder == "0":
            print("[function.chain.factionTree] no master key".format(keyHolder))
            faction.posterHold = False
            faction.poster = False
            faction.save()
            return 0

    else:
        keyHolder is False
        # print("[function.chain.updateMembers] using personal key")

    # call for upgrades
    req = apiCall('faction', faction.tId, 'basic,upgrades', key, verbose=False)
    if 'apiError' in req:
        if req['apiErrorCode'] in API_CODE_DELETE and keyHolder:
            print("[function.chain.factionTree]    --> deleting {}'s key'".format(keyHolder))
            faction.delKey(keyHolder)
        # print('[function.chain.factionTree] api key error: {}'.format((faction['apiError'])))
        return 0

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
    # print("[function.chain.factionTree] background color: {}".format(background))
    img = Image.new('RGBA', (5000, 5000), color=background)

    # choose font
    fontFamily = posterOpt.get('fontFamily', [0])[0]
    fntId = {i: [f, int(f.split("__")[1].split(".")[0])] for i, f in enumerate(sorted(os.listdir(settings.STATIC_ROOT + '/perso/font/')))}
    # fntId = {0: 'CourierPolski1941.ttf', 1: 'JustAnotherCourier.ttf'}
    # print("[function.chain.factionTree] fontFamily: {} {}".format(fontFamily, fntId[fontFamily]))
    fntBig = ImageFont.truetype(settings.STATIC_ROOT + '/perso/font/' + fntId[fontFamily][0], fntId[fontFamily][1] + 10)
    fnt = ImageFont.truetype(settings.STATIC_ROOT + '/perso/font/' + fntId[fontFamily][0], fntId[fontFamily][1])
    d = ImageDraw.Draw(img)

    fontColor = tuple(posterOpt.get('fontColor', (0, 0, 0, 255)))
    # print("[function.chain.factionTree] fontColor: {}".format(fontColor))

    # add title
    txt = "{}".format(req["name"])
    d.text((10, 10), txt, font=fntBig, fill=fontColor)
    x, y = d.textsize(txt, font=fntBig)

    txt = "{:,} respect\n".format(req["respect"])
    d.text((x + 20, 20), txt, font=fnt, fill=fontColor)
    x, y = d.textsize(txt, font=fntBig)

    iconType = posterOpt.get('iconType', [0])[0]
    # print("[function.chain.factionTree] iconType: {}".format(iconType))
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

        # print('[function.chain.factionTree] {} ({} upgrades)'.format(branch, len(upgrades)))

    # img.crop((0, 0, x + 90 + 10, y + 10 + 10)).save(url)
    img.crop((0, 0, x + 90 + 10, y)).save(url)
    # print('[function.chain.factionTree] image saved {}'.format(url))


def updateFactionTree(faction, key=None, force=False, reset=False):
    # it's not possible to delete all memebers and recreate the base
    # otherwise the target list will be lost

    now = int(timezone.now().timestamp())

    # don't update if less than 24h ago and force is False
    if not force and (now - faction.treeUpda) < 24 * 3600:
        print("[function.chain.updateFactionTree] skip update tree")
        if faction.simuTree in ["{}"]:
            print("[function.chain.updateFactionTree] set simuTree as faction tree")
            faction.simuTree = faction.factionTree
            faction.save()
        # return faction.faction.all()
    else:

        # call upgrade Tree
        tornTree = json.loads(FactionData.objects.first().upgradeTree)
        # basic needed for respect
        # upgrades needed for upgrades daaa
        # stats needed for challenges
        factionCall = apiCall('faction', faction.tId, 'basic,upgrades,stats', key)
        if 'apiError' in factionCall:
            print("[function.chain.updateFactionTree] api key error {}".format(factionCall['apiError']))
        else:
            print("[function.chain.updateFactionTree] update faction tree")
            factionTree = factionCall.get('upgrades')
            orders = dict({})
            for i in range(48):
                id = str(i + 1)

                # skip id = 8 for example #blameched
                if id not in tornTree:
                    continue

                # create branches that are not in faction tree
                branch = tornTree[id]["1"]['branch']
                if id not in factionTree:
                    factionTree[id] = {'branch': branch, 'branchorder': 0, 'branchmultiplier': 0, 'name': tornTree[id]["1"]['name'], 'level': 0, 'basecost': 0, 'challengedone': 0}

                # put core branch to branchorder 1
                if branch in ['Core']:
                    factionTree[id]['branchorder'] = 1

                # consistency in the branchorder for the
                if branch in orders:
                    orders[branch] = max(factionTree[id]['branchorder'], orders[branch])
                else:
                    orders[branch] = factionTree[id]['branchorder']

                # set faction progress
                sub = "1"
                sub = "2" if id == "10" else sub  # chaining 1rt is No challenge
                sub = "3" if id == "11" else sub  # capacity 1rt and 2nd is No challenge
                sub = "2" if id == "12" else sub  # territory 1rt is No challenge
                ch = tornTree[id][sub]['challengeprogress']
                if ch[0] in ["age", "best_chain"]:
                    factionTree[id]["challengedone"] = factionCall.get(ch[0], 0)
                elif ch[0] in ["members"]:
                    factionTree[id]["challengedone"] = len(factionCall.get(ch[0], [1, 2]))
                elif ch[0] is None:
                    factionTree[id]["challengedone"] = 0
                else:
                    factionTree[id]["challengedone"] = factionCall["stats"].get(ch[0], 0)

            for k in factionTree:
                factionTree[k]['branchorder'] = orders[factionTree[k]['branch']]

            faction.factionTree = json.dumps(factionTree)
            if reset:
                print("[function.chain.updateFactionTree] set simuTree as faction tree")
                faction.simuTree = faction.factionTree
                faction.save()
            faction.treeUpda = now
            faction.respect = int(factionCall.get('respect', 0))
            faction.save()

    return json.loads(faction.factionTree), json.loads(faction.simuTree)


def apiCallAttacksV2(breakdown):
    # shortcuts
    faction = breakdown.faction
    tss = breakdown.tss
    tse = breakdown.tse if breakdown.tse else int(timezone.now().timestamp())
    # recompute last ts
    tmp = breakdown.attack_set.order_by("-timestamp_ended").first()
    if tmp is not None:
        tsl = tmp.timestamp_ended
    else:
        tsl = breakdown.tss

    print("[function.chain.apiCallAttacks] Breakdown from {} to {}. Live = {}".format(timestampToDate(tss), timestampToDate(tse), breakdown.live))

    # add + 2 s to the endTS
    tse += 2

    # get existing attacks (just the ids)
    attacks = [r.tId for r in breakdown.attack_set.all()]
    print("[function.chain.apiCallAttacks] {} existing attacks".format(len(attacks)))

    # get key
    keys = faction.getAllPairs(enabledKeys=True)
    if not len(keys):
        print("[function.chain.apiCallAttacks] no key for faction {}   --> deleting breakdown".format(faction))
        breakdown.delete()
        return False, "no key in faction {} (delete contract)".format(faction)

    keyHolder, key = random.choice(keys)

    # make call
    selection = "attacks,timestamp&from={}&to={}".format(tsl, tse)
    req = apiCall("faction", faction.tId, selection, key, verbose=True)

    # in case there is an API error
    if "apiError" in req:
        print('[function.chain.apiCallAttacks] api key error: {}'.format((req['apiError'])))
        if req['apiErrorCode'] in API_CODE_DELETE:
            print("[function.chain.apiCallAttacks]    --> deleting {}'s key'".format(keyHolder))
            faction.delKey(keyHolder)
        return False, "wrong master key in faction {} for user {} (blank turn)".format(faction, keyHolder)

    # try to catch cache response
    tornTS = int(req["timestamp"])
    nowTS = int(timezone.now().timestamp())
    cacheDiff = abs(nowTS - tornTS)

    apiAttacks = req.get("attacks")

    # in case empty payload
    if not len(apiAttacks):
        breakdown.computing = False
        breakdown.save()
        return False, "Empty payload (stop computing)"

    print("[function.chain.apiCallAttacks] {} attacks from the API".format(len(apiAttacks)))

    print("[function.chain.apiCallAttacks] start {}".format(timestampToDate(tss)))
    print("[function.chain.apiCallAttacks] end {}".format(timestampToDate(tse)))
    print("[function.chain.apiCallAttacks] last before the call {}".format(timestampToDate(tsl)))

    newEntry = 0
    for k, v in apiAttacks.items():
        ts = int(v["timestamp_ended"])

        # stop because out of bound
        # probably because of cache
        # if int(v["timestamp_started"]) < tsl or int(v["timestamp_ended"]) > tse:
        #     print(ts)
        #     print(tsl)
        #     print(tse)
        #     return False, "timestamp out of bound for faction {} with cacheDiff = {} (added {} entry before exiting)".format(faction, cacheDiff, newEntry)

        if int(k) not in attacks:
            for tmpKey in ["fairFight", "war", "retaliation", "groupAttack", "overseas", "chainBonus"]:
                v[tmpKey] = float(v["modifiers"][tmpKey])
            del v["modifiers"]
            breakdown.attack_set.create(tId=int(k), **v)
            newEntry += 1
            tsl = max(tsl, ts)

    print("[function.chain.apiCallAttacks] last after the call {}".format(timestampToDate(tsl)))

    # compute contract variables
    attacks = breakdown.attack_set.all()
    # breakdown.revivesContract = len(revives)
    # breakdown.first = revives.order_by("timestamp").first().timestamp
    # breakdown.last = revives.order_by("-timestamp").first().timestamp

    if not newEntry and len(apiAttacks) > 1:
        return False, "No new entry for faction {} with cacheDiff = {} (continue)".format(faction, cacheDiff)

    if len(apiAttacks) < 2 and not breakdown.live:
        print("[function.chain.apiCallAttacks] no api entry for non live breakdown (stop)")
        breakdown.computing = False

    breakdown.save()
    return True, "Everything's fine"


def apiCallRevives(contract):
    # shortcuts
    faction = contract.faction
    start = contract.start
    end = contract.end if contract.end else int(timezone.now().timestamp())
    # recompute last
    tmp = contract.revive_set.order_by("-timestamp").first()
    if tmp is not None:
        last = tmp.timestamp
    else:
        last = contract.start

    print("[function.chain.apiCallRevives] Contract from {} to {}".format(timestampToDate(start), timestampToDate(end)))

    # add + 2 s to the endTS
    end += 2

    # get existing revives (just the ids)
    revives = [r.tId for r in contract.revive_set.all()]
    print("[function.chain.apiCallRevives] {} existing revives".format(len(revives)))

    # # last timestamp
    # if len(revives):
    #     lastRevive = contract.revive_set.order_by("-timestamp").first()
    #     last = lastRevive.timestamp
    # else:
    #     last = start

    # get key
    keys = faction.getAllPairs(enabledKeys=True)
    if not len(keys):
        print("[function.chain.apiCallRevives] no key for faction {}   --> deleting contract".format(faction))
        contract.delete()
        return False, "no key in faction {} (delete contract)".format(faction)

    keyHolder, key = random.choice(keys)

    # make call
    selection = "revives,timestamp&from={}&to={}".format(last, end)
    req = apiCall("faction", faction.tId, selection, key, verbose=True)

    # in case there is an API error
    if "apiError" in req:
        print('[function.chain.apiCallRevives] api key error: {}'.format((req['apiError'])))
        if req['apiErrorCode'] in API_CODE_DELETE:
            print("[function.chain.apiCallRevives]    --> deleting {}'s key'".format(keyHolder))
            faction.delKey(keyHolder)
        return False, "wrong master key in faction {} for user {} (blank turn)".format(faction, keyHolder)

    # try to catch cache response
    tornTS = int(req["timestamp"])
    nowTS = int(timezone.now().timestamp())
    cacheDiff = abs(nowTS - tornTS)

    apiRevives = req.get("revives")

    # in case empty payload
    if not len(apiRevives):
        contract.computing = False
        contract.save()
        return False, "Empty payload (stop computing)"

    print("[function.chain.apiCallRevives] {} revives from the API".format(len(apiRevives)))

    print("[function.chain.apiCallRevives] start {}".format(timestampToDate(start)))
    print("[function.chain.apiCallRevives] end {}".format(timestampToDate(end)))
    print("[function.chain.apiCallRevives] last before the call {}".format(timestampToDate(last)))

    newEntry = 0
    for k, v in apiRevives.items():
        ts = int(v["timestamp"])

        # stop because out of bound
        # probably because of cache
        if ts < last or ts > end:
            return False, "timestamp out of bound for faction {} with cacheDiff = {} (added {} entry before exiting)".format(faction, cacheDiff, newEntry)

        if int(k) not in revives:
            contract.revive_set.create(tId=int(k), **v)
            newEntry += 1
            last = max(last, ts)

    print("[function.chain.apiCallRevives] last after the call {}".format(timestampToDate(last)))

    # compute contract variables
    revives = contract.revive_set.all()
    contract.revivesContract = len(revives)
    contract.first = revives.order_by("timestamp").first().timestamp
    contract.last = revives.order_by("-timestamp").first().timestamp

    if not newEntry and len(apiRevives) > 1:
        return False, "No new entry for faction {} with cacheDiff = {} (continue)".format(faction, cacheDiff)

    if len(apiRevives) < 2:
        contract.computing = False

    contract.save()
    return True, "Everything's fine"
