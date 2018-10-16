from django.core.management.base import BaseCommand
from django.utils import timezone

import numpy

from chain.models import Faction
from yata.handy import apiCall
from yata.handy import apiCallAttacks
from yata.handy import timestampToDate


class Command(BaseCommand):
    def handle(self, **options):
        print("[COMMAND live] start")

        for faction in Faction.objects.all():
            print("[COMMAND live] faction {}".format(faction))

            # get api key
            if faction.apiKey == "0":
                print("[COMMAND live] no api key found")
                break
            factionId = faction.tId
            key = faction.apiKey

            # get chain status
            print("[COMMAND live] with api key")
            liveChain = apiCall("faction", factionId, "chain", key, sub="chain")
            if 'apiError' in liveChain:
                print('[COMMAND live] api key error: {}'.format((liveChain['apiError'])))
                break

            if not bool(liveChain["current"]):
                print("[COMMAND live] no active chain")
                faction.chain_set.filter(tId=0).delete()
                print("[COMMAND live] report 0 deleted")
                break

            # get chain
            print('[COMMAND live] this is a live report')
            chain = faction.chain_set.filter(tId=0).first()
            if chain is None:
                print('[COMMAND live] create chain 0')
                chain = faction.chain_set.create(tId=0)

            # change dates and status
            chain.status = True
            chain.end = int(timezone.now().timestamp())
            chain.start = 1
            chain.endDate = timestampToDate(chain.end)
            chain.save()
            # get number of attacks
            chainInfo = apiCall('faction', factionId, 'chain', key, sub='chain')
            if 'apiError' in chainInfo:
                print('[COMMAND live] api key error: {}'.format((chainInfo['apiError'])))
                break

            stopAfterNAttacks = chainInfo.get('current')
            print('[COMMAND live] stop after {} attacks'.format(stopAfterNAttacks))
            if stopAfterNAttacks:
                attacks = apiCallAttacks(factionId, chain.start, chain.end, key, stopAfterNAttacks=stopAfterNAttacks)
            else:
                attacks = dict({})

            # delete old report and create new
            chain.report_set.all().delete()
            report = chain.report_set.create()
            print('[COMMAND live] new report created')

            # refresh members
            members = apiCall('faction', factionId, 'basic', key, sub='members')
            if 'apiError' in members:
                print('[COMMAND live] api key error: {}'.format((members['apiError'])))
                break
            faction.member_set.all().delete()
            for m in members:
                faction.member_set.create(tId=m, name=members[m]['name'], lastAction=members[m]['last_action'], daysInFaction=members[m]['days_in_faction'])
            members = faction.member_set.all()

            # initialisation of variables before loop
            bonus_hits = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000]  # bonus respect values are 4.2**n
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
                        print('[COMMAND live] hitter out of faction: {}'.format(attackerName))
                        attackers[attackerName] = [0, 0, 0.0, 0.0, -1, attackerID]  # add out of faction attackers on the fly

                    # if it's a hit
                    respect = float(v['respect_gain'])
                    if respect > 0.0:
                        attacksForHisto.append(v['timestamp_ended'])
                        nWR[0] += 1
                        attackers[attackerName][0] += 1
                        if v['chain'] in bonus_hits:
                            r = 4.2 * 2**(1 + float([i for i, x in enumerate(bonus_hits) if x == int(v['chain'])][0]))
                            print('[COMMAND live] bonus {}: {} respects'.format(v['chain'], r))
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
            print('[COMMAND live] chain delta time: {} second'.format(diff))
            print('[COMMAND live] histogram bins delta time: {} second'.format(binsGapMinutes * 60))
            print('[COMMAND live] histogram number of bins: {}'.format(len(bins) - 1))
            histo, bin_edges = numpy.histogram(attacksForHisto, bins=bins)
            binsCenter = [int(0.5 * (a + b)) for (a, b) in zip(bin_edges[0:-1], bin_edges[1:])]
            chain.nHits = nWR[0]
            chain.respect = nWR[1]
            chain.graph = ','.join(['{}:{}'.format(a, b) for (a, b) in zip(binsCenter, histo)])
            chain.save()

            # fill the database with counts and bonuses
            for k, v in attackers.items():
                # if v[1]:
                report.count_set.create(attackerId=v[5], name=k, wins=v[0], hits=v[1], fairFight=v[2], respect=v[3], daysInFaction=v[4])
            for b in bonus:
                report.bonus_set.create(hit=b[0], name=b[1], respect=b[2], respectMax=b[3])

            print("[COMMAND live] report filled")
