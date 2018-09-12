from django.core.management.base import BaseCommand
from django.utils import timezone


from chain.models import Faction
from yata.handy import apiCall
from yata.handy import apiCallAttacks
from yata.handy import timestampToDate

class Command(BaseCommand):
    def handle(self, **options):
        print("[COMMAND live] start")

        for faction in Faction.objects.all():
            print("[COMMAND live] faction {}".format(faction))
            if faction.apiKey != "0":
                factionId = faction.tId
                key = faction.apiKey
                print("[COMMAND live] with api key")
                liveChain = apiCall("faction", factionId, "chain", key, sub="chain")
                activeChain = bool(liveChain["current"])
                if activeChain:
                    print("[COMMAND live] active chain")
                    try:
                        chain = faction.chain_set.filter(tId=0)[0]
                        print("[COMMAND live] chain found")
                    except:
                        chain = faction.chain_set.create(tId=0, status=False)
                        print("[COMMAND live] chain created")

                    try:
                        report = chain.report_set.all()[0]
                        print("[COMMAND live] report found")
                    except:
                        report = chain.report_set.create()
                        print("[COMMAND live] report created")

                    report.count_set.all().delete()

                    members = faction.member_set.all()
                    attackers = dict({})  # create attackers array on the fly to avoid db connectio in the loop
                    for m in members:
                        attackers[m.name] = [0, 0, 0.0, 0.0, m.daysInFaction, m.tId]

                    chain.end = int(timezone.now().timestamp())
                    chain.start = 1
                    chain.startDate = timestampToDate(chain.start)
                    chain.endDate = timestampToDate(chain.end)
                    chain.save()
                    stopAfterNAttacks = apiCall("faction", factionId, "chain", key, sub="chain")["current"]
                    if stopAfterNAttacks:
                        attacks = apiCallAttacks(factionId, chain.start, chain.end, key, stopAfterNAttacks=stopAfterNAttacks)
                    else:
                        attacks = dict({})


                    # loop over the attacks
                    BONUS_RESPECT = {10: 8.4, 25: 16.8, 50: 33.6, 100: 67.2, 250: 134.4, 500: 268.8, 1000: 537.6,
                                     2500: 1075.2, 5000: 2150.4, 10000: 4300.8, 25000: 8601.6, 50000: 17203.2, 100000: 34406.4}
                    WINS = ["Arrested", "Attacked", "Looted", "None", "Special", "Hospitalized", "Mugged"]
                    bonus = []

                    nWins = 0
                    i = 0
                    for k, v in sorted(attacks.items(), key=lambda x: x[1]["timestamp_ended"], reverse=True):
                        i += 1
                        attackerID = int(v["attacker_id"])
                        # print(i, nWins, v["chain"], v["timestamp_started"])
                        if(int(v["attacker_faction"]) == faction.tId):
                            # get relevent info
                            tmp = faction.member_set.filter(tId=attackerID)
                            if len(tmp):
                                name = tmp[0].name
                            else:
                                tmpAttacker = apiCall("user", attackerID, "basic", key)
                                name = tmpAttacker["name"]
                                attackers[name] = [0, 0, 0.0, 0.0, -1, attackerID]                                # add out of faction attackers on the fly
                                faction.member_set.create(tId=attackerID, name=name, daysInFaction=-1)
                            respect = float(v["respect_gain"])

                            if v["result"] in WINS and respect > 0.0:  # respect > 0.0 in case of friendly fire ^^
                                nWins += 1
                                attackers[name][0] += 1
                                if v["chain"] in BONUS_RESPECT:
                                    # print(k, v)
                                    attackers[name][2] += respect - BONUS_RESPECT[v["chain"]]
                                    bonus.append((v["chain"], name, respect, BONUS_RESPECT[v["chain"]]))
                                else:
                                    attackers[name][2] += respect
                                attackers[name][3] += respect

                            attackers[name][1] += 1

                            if stopAfterNAttacks is not False and nWins >= stopAfterNAttacks:
                                break

                    for k, v in attackers.items():
                        if v[1]:
                            report.count_set.create(attackerId=v[5], name=k, wins=v[0], hits=v[1], respect=v[2], respectTotal=v[3], daysInFaction=v[4])
                    for b in bonus:
                        report.bonus_set.create(hit=b[0], name=b[1], respect=b[2], respectMax=b[3])

                    print("[COMMAND live] report filled")

                else:
                    print("[COMMAND live] no active chain")
                    faction.chain_set.filter(tId=0).delete()
                    print("[COMMAND live] report 0 deleted")


        print("[COMMAND live] end")
