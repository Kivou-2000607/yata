def timestampToDate(timestamp):
    import datetime
    import pytz
    return datetime.datetime.fromtimestamp(timestamp, tz=pytz.UTC)


def apiCall(section, id, selections, key, sub=None):
    import requests
    # DEBUG live chain
    # if selections == "chain" and section == "faction":
    #     print("[FUNCTION apiCall] DEBUG chain/faction")
    #     chain = dict({"chain": {"current": 3,
    #                             "timeout": 65,
    #                             "modifier": 0.75,
    #                             "cooldown": 0
    #                             }})
    #     return chain[sub] if sub is not None else chain

    # DEBUG API error
    # return dict({"apiError": "API error code 42: debug error."})

    try:
        url = "https://api.torn.com/{}/{}?selections={}&key={}".format(section, id, selections, key)
        print("[FUNCTION apiCall] {}".format(url.replace(key, "*" * len(key))))
        r = requests.get(url)
        r.raise_for_status()

        rjson = r.json()

        if "error" in rjson:  # standard api error
            err = rjson
        else:
            if sub is not None:
                if sub in rjson:
                    return rjson[sub]
                else:  # key not found
                    err = dict({"error": {"code": "", "error": "key not found... something went wrong..."}})
            else:
                return rjson

    except requests.exceptions.HTTPError as e:
        print("[FUNCTION apiCall] API HTTPError {}".format(e))
        err = dict({"error": {"code": r.status_code, "error": "{} #blameched".format(r.reason)}})

    return dict({"apiError": "API error code {}: {}.".format(err["error"]["code"], err["error"]["error"])})


def apiCallAttacks(factionId, beginTS, endTS, key, stopAfterNAttacks=False):
    import requests
    # WARNING no fallback for this method if api crashed. Will yeld server error.

    WINS = ["Arrested", "Attacked", "Looted", "None", "Special", "Hospitalized", "Mugged"]

    chain = dict({})

    beginTS = beginTS
    currentEndTS = endTS + 1  # add one to get last hit
    feedAttacks = True
    i = 1
    nWins = 0
    while feedAttacks:
        url = "https://api.torn.com/faction/{}?selections=attacks&key={}&from={}&to={}".format(factionId, key, beginTS, currentEndTS)
        print("[FUNCTION apiCallAttacks] call number {}: {}".format(i, url.replace(key, "*" * len(key))), end='... ')
        attacks = requests.get(url).json()["attacks"]
        if len(attacks):
            for k, v in attacks.items():
                if v["result"] in WINS and float(v["respect_gain"]) > 0.0:
                    nWins += 1
                chain[k] = v
                currentEndTS = min(v["timestamp_ended"], currentEndTS)
            if(len(attacks) < 1000):
                feedAttacks = False
            print("\tNumber of attacks: {}".format(len(attacks)))
            i += 1
        else:
            print("\tNumber of attacks: {}".format(len(attacks)))
            feedAttacks = False

        if stopAfterNAttacks is not False and nWins >= stopAfterNAttacks:
            print("[FUNCTION apiCallAttacks] stopped after {} attacks".format(stopAfterNAttacks))
            feedAttacks = False

    return chain


def fillReport(faction, members, chain, report, attacks, stopAfterNAttacks):
    from django.utils import timezone
    import numpy

    bonus_hits = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000]  # bonus respect values are 4.2**n

    # initialisation of variables before loop
    nWR = [0, 0.0]  # number of wins and respect
    bonus = []  # chain bonus
    attacksForHisto = []  # record attacks timestamp histogram

    # create attackers array on the fly to avoid db connection in the loop
    attackers = dict({})
    for m in members:
        attackers[m.name] = [0, 0, 0.0, 0.0, m.daysInFaction, m.tId]

    # loop over attacks
    tmp = dict({})
    for k, v in sorted(attacks.items(), key=lambda x: x[1]['timestamp_ended'], reverse=True):
        attackerID = int(v['attacker_id'])
        attackerName = v['attacker_name']
        # if attacker part of the faction at the time of the chain
        if(int(v['attacker_faction']) == faction.tId):
            if tmp.get(v["result"]) is None:
                tmp[v["result"]] = 1
            else:
                tmp[v["result"]] += 1
            # if attacker not part of the faction at the time of the call
            if attackerName not in attackers:
                print('[FUNCTION fillReport] hitter out of faction: {}'.format(attackerName))
                attackers[attackerName] = [0, 0, 0.0, 0.0, -1, attackerID]  # add out of faction attackers on the fly

            # if it's a hit
            respect = float(v['respect_gain'])
            if respect > 0.0:
                attacksForHisto.append(v['timestamp_ended'])
                nWR[0] += 1
                attackers[attackerName][0] += 1
                if v['chain'] in bonus_hits:
                    r = 4.2 * 2**(1 + float([i for i, x in enumerate(bonus_hits) if x == int(v['chain'])][0]))
                    print('[FUNCTION fillReport] bonus {}: {} respects'.format(v['chain'], r))
                    bonus.append((v['chain'], attackerName, respect, r))
                attackers[attackerName][2] += float(v['modifiers']['fairFight'])
                attackers[attackerName][3] += respect / float(v['modifiers']['chainBonus'])
                nWR[1] += respect

            attackers[attackerName][1] += 1

            if stopAfterNAttacks is not False and nWR[0] >= stopAfterNAttacks:
                break

    for k, v in tmp.items():
        print(k, v)

    # create histogram
    chain.start = int(attacksForHisto[-1])
    chain.startDate = timestampToDate(chain.start)
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
    chain.nHits = nWR[0]
    chain.respect = nWR[1]
    chain.graph = ','.join(['{}:{}'.format(a, b) for (a, b) in zip(binsCenter, histo)])
    chain.save()

    # fill the database with counts and bonuses
    for k, v in attackers.items():
        # time now - chain end - days old: determine if member was in the fac for the chain
        delta = int(timezone.now().timestamp()) - chain.end - v[4] * 24 * 3600
        beenThere = True if (delta < 0 or v[4] < 0) else False
        report.count_set.create(attackerId=v[5], name=k, wins=v[0], hits=v[1], fairFight=v[2], respect=v[3], daysInFaction=v[4], beenThere=beenThere)
    for b in bonus:
        report.bonus_set.create(hit=b[0], name=b[1], respect=b[2], respectMax=b[3])

    return chain, report, (binsCenter, histo)
