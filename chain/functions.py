from django.utils import timezone

from yata.handy import apiCall
from yata.handy import timestampToDate

from chain.models import Faction

import requests
import time
import numpy


# global bonus hits
BONUS_HITS = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000]


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


def apiCallAttacks(factionId, beginTS, endTS, key=None):
    # WARNING no fallback for this method if api crashed. Will yeld server error.
    # WINS = ["Arrested", "Attacked", "Looted", "None", "Special", "Hospitalized", "Mugged"]
    tip = time.time()

    # get all faction keys
    keys = Faction.objects.filter(tId=factionId)[0].get_all_pairs()

    # init
    chain = dict({})
    feedAttacks = True
    i = 1
    while feedAttacks:
        if key is None:
            keyToUse = keys[i % len(keys)][1]
            print("[FUNCTION apiCallAttacks] call number {}: using {} key".format(i, keys[i % len(keys)][0]))
        else:
            keyToUse = key
            print("[FUNCTION apiCallAttacks] call number {}: using personal key".format(i))

        url = "https://api.torn.com/faction/{}?selections=attacks&key={}&from={}&to={}".format(factionId, keyToUse, beginTS, endTS)
        print("[FUNCTION apiCallAttacks] call number {}: {}".format(i, url.replace("&key=" + keyToUse, "")))
        attacks = requests.get(url).json()["attacks"]

        if len(attacks):
            for j, (k, v)in enumerate(attacks.items()):
                chain[k] = v
                beginTS = max(v["timestamp_ended"] + 1, beginTS)

            if(len(attacks) < 2):
                feedAttacks = False

            print("[FUNCTION apiCallAttacks] call number {}: {} attacks".format(i, len(attacks)))
            i += 1
        else:
            print("[FUNCTION apiCallAttacks] call number {}: {} attacks".format(i, len(attacks)))
            feedAttacks = False

    print('[FUNCTION apiCallAttacks] It took {:.02f} seconds to make all the API calls'.format(time.time() - tip))

    return chain


def fillReport(faction, members, chain, report, attacks):
    tip = time.time()

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
        attackers[m.name] = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, m.daysInFaction, m.tId, 0]

    # loop over attacks
    lastTS = 0
    for k, v in sorted(attacks.items(), key=lambda x: x[1]['timestamp_ended'], reverse=False):

        attackerID = int(v['attacker_id'])
        attackerName = v['attacker_name']
        # if attacker part of the faction at the time of the chain
        if(int(v['attacker_faction']) == faction.tId):
            # if attacker not part of the faction at the time of the call
            if attackerName not in attackers:
                print('[FUNCTION fillReport] hitter out of faction: {}'.format(attackerName))
                attackers[attackerName] = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1, attackerID, 0]  # add out of faction attackers on the fly

            attackers[attackerName][0] += 1
            nWRA[2] += 1

            # if it's a hit
            respect = float(v['respect_gain'])
            if respect > 0.0:
                # print("Time stamp:", v['timestamp_ended'])

                # init lastTS for the first iteration of the loop
                lastTS = v['timestamp_ended'] if lastTS == 0 else lastTS

                # compute chain watcher version 2
                attackers[attackerName][11] += (v['timestamp_ended'] - lastTS)
                lastTS = v['timestamp_ended']

                attacksForHisto.append(v['timestamp_ended'])
                if attackerName in attackersHisto:
                    attackersHisto[attackerName].append(v['timestamp_ended'])
                else:
                    attackersHisto[attackerName] = [v['timestamp_ended']]

                nWRA[0] += 1
                nWRA[1] += respect

                attackers[attackerName][1] += 1
                attackers[attackerName][2] += float(v['modifiers']['fairFight'])
                attackers[attackerName][3] += float(v['modifiers']['war'])
                attackers[attackerName][4] += float(v['modifiers']['retaliation'])
                attackers[attackerName][5] += float(v['modifiers']['groupAttack'])
                attackers[attackerName][6] += float(v['modifiers']['overseas'])
                attackers[attackerName][7] += float(v['modifiers']['chainBonus'])
                attackers[attackerName][8] += respect / float(v['modifiers']['chainBonus'])
                if v['chain'] in BONUS_HITS:
                    r = getBonusHits(v['chain'], v["timestamp_ended"])
                    print('[FUNCTION fillReport] bonus {}: {} respects'.format(v['chain'], r))
                    bonus.append((v['chain'], attackerName, respect, r))
                
    print('[FUNCTION fillReport] It took {:.02f} seconds to build the attacker array'.format(time.time() - tip))
    tip = time.time()

    # create histogram
    chain.start = int(attacksForHisto[0])
    chain.end = int(attacksForHisto[-1])
    chain.startDate = timestampToDate(chain.start)
    chain.endDate = timestampToDate(chain.end)
    diff = int(chain.end - chain.start)
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
    print('[FUNCTION fillReport] chain delta time: {} second'.format(diff))
    print('[FUNCTION fillReport] histogram bins delta time: {} second'.format(binsGapMinutes * 60))
    print('[FUNCTION fillReport] histogram number of bins: {}'.format(len(bins) - 1))
    histo, bin_edges = numpy.histogram(attacksForHisto, bins=bins)
    binsCenter = [int(0.5 * (a + b)) for (a, b) in zip(bin_edges[0:-1], bin_edges[1:])]
    chain.nHits = nWRA[0]
    chain.respect = nWRA[1]
    chain.nAttacks = nWRA[2]
    chain.graph = ','.join(['{}:{}'.format(a, b) for (a, b) in zip(binsCenter, histo)])
    chain.save()

    print('[FUNCTION fillReport] It took {:.02f} seconds to build histogram'.format(time.time() - tip))
    tip = time.time()

    # fill the database with counts
    print('[FUNCTION fillReport] fill database with counts')
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
        print("watcher for ", k, watcher)
        report.count_set.create(attackerId=v[10],
                                name=k,
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

    print('[FUNCTION fillReport] It took {:.02f} seconds to fill the count'.format(time.time() - tip))
    tip = time.time()

    # fill the database with bonus
    print('[FUNCTION fillReport] fill database with bonus')
    for b in bonus:
        report.bonus_set.create(hit=b[0], name=b[1], respect=b[2], respectMax=b[3])

    print('[FUNCTION fillReport] It took {:.02f} seconds to fill the bonus'.format(time.time() - tip))
    tip = time.time()

    return chain, report, (binsCenter, histo)


def updateMembers(faction, key=None):
    # it's not possible to delete all memebers and recreate the base
    # otherwise the target list will be lost

    # get key
    if key is None:
        name, key = faction.get_random_key()
        print("[FUNCTION updateMembers] using {} key".format(name))
    else:
        print("[FUNCTION updateMembers] using personal key")

    # call members
    membersAPI = apiCall('faction', faction.tId, 'basic', key, sub='members')
    if 'apiError' in membersAPI:
        return membersAPI

    membersDB = faction.member_set.all()
    for m in membersAPI:
        memberDB = membersDB.filter(tId=m).first()
        if memberDB is not None:
            print('[VIEW members] member {} [{}] updated'.format(membersAPI[m]['name'], m))
            memberDB.name = membersAPI[m]['name']
            memberDB.lastAction = membersAPI[m]['last_action']
            memberDB.daysInFaction = membersAPI[m]['days_in_faction']
            memberDB.save()
        else:
            print('[VIEW members] member {} [{}] created'.format(membersAPI[m]['name'], m))
            faction.member_set.create(tId=m, name=membersAPI[m]['name'], lastAction=membersAPI[m]['last_action'], daysInFaction=membersAPI[m]['days_in_faction'])

    # delete old members
    for m in membersDB:
        if membersAPI.get(str(m.tId)) is None:
            print('[VIEW members] member {} deleted'.format(m))
            m.delete()

    return faction.member_set.all()
