from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone

import json

from yata.handy import apiCall
from yata.handy import apiCallAttacks
from yata.handy import timestampToDate
from yata.handy import toggleMessage

from .models import Faction


def index(request):
    if request.session.get("chainer"):
        factionId = request.session["chainer"].get("factionId")
        key = request.session["chainer"].get("keyValue")

        try:
            faction = Faction.objects.filter(tId=factionId)[0]
            liveChain = apiCall("faction", factionId, "chain", key, sub="chain")
            activeChain = bool(liveChain["current"])
        except:
            return render(request, 'chain.html')

        if activeChain:
            try:
                chain = faction.chain_set.filter(tId=0)[0]
                report = chain.report_set.filter(chain=chain)[0]
                counts = report.count_set.all()
                bonus = report.bonus_set.all()
            except:
                faction.chain_set.filter(tId=0).delete()
                chain = faction.chain_set.create(tId=0, status=False)
                report = False
                counts = False
                bonus = False

            context = dict({'liveChain': liveChain, 'chain': chain, 'bonus': bonus, 'counts': counts, "view": {"report": True, "liveReport": True}})

        else:
            faction.chain_set.filter(tId=0).delete()
            context = dict({'liveChain': liveChain, "view": {"liveReport": True}})

        return render(request, 'chain.html', context)

    return render(request, 'chain.html')


def list(request):
    if request.session.get("chainer"):
        factionId = request.session["chainer"].get("factionId")

        try:
            faction = Faction.objects.filter(tId=factionId)[0]
        except:
            return HttpResponseRedirect(reverse('chain:createList'))

        context = dict({'chains': faction.chain_set.filter(status=True), "view": {"list": True}})
        context = toggleMessage(request, context, "onTheFlyMessage")
        return render(request, 'chain.html', context)
    else:
        return HttpResponseRedirect(reverse('chain:index'))


def createList(request):  # able to create faction
    if request.session.get("chainer"):
        key = request.session["chainer"].get("keyValue")
        factionId = request.session["chainer"].get("factionId")
        request.session["onTheFlyMessage"] = []

        try:
            faction = Faction.objects.filter(tId=factionId)[0]
        except:
            faction = Faction.objects.create(tId=factionId, name=request.session["chainer"].get("factionName"))
            request.session["onTheFlyMessage"].append("Faction {} created".format(factionId))

        # create live chain
        try:
            faction.chain_set.create(tId=0, status=False)
        except:
            pass

        if request.session["chainer"].get("AA"):
            req = apiCall("faction", faction.tId, "chains", key, sub='chains')
            for r in req:
                if req[r]['chain'] >= faction.hitsThreshold:
                    if len(faction.chain_set.filter(tId=r)) == 0:
                        faction.chain_set.create(tId=r, nHits=req[r]['chain'], respect=req[r]['respect'],
                                                 start=req[r]['start'], startDate=timestampToDate(req[r]['start']),
                                                 end=req[r]['end'], endDate=timestampToDate(req[r]['end']))

            request.session["onTheFlyMessage"].append("List of chains updated")

        return HttpResponseRedirect(reverse('chain:list'))
    return HttpResponseRedirect(reverse('chain:index'))


def members(request):
    if request.session.get("chainer"):
        factionId = request.session["chainer"].get("factionId")

        try:
            faction = Faction.objects.filter(tId=factionId)[0]
        except:
            return HttpResponseRedirect(reverse('chain:createMembers'))

        members = faction.member_set.all()

        context = dict({'members': members, "view": {"members": True}})
        context = toggleMessage(request, context, "onTheFlyMessage")
        return render(request, 'chain.html', context)
    else:
        return render(request, 'chain.html')


def createMembers(request):
    if request.session.get("chainer"):
        request.session["onTheFlyMessage"] = []

        key = request.session["chainer"].get("keyValue")
        factionId = request.session["chainer"].get("factionId")

        try:
            faction = Faction.objects.filter(tId=factionId)[0]
        except:
            faction = Faction.objects.create(tId=factionId, name=request.session["chainer"].get("factionName"))
            request.session["onTheFlyMessage"].append("Faction {} created".format(factionId))

        members = apiCall("faction", factionId, "basic", key, sub="members")
        for m in members:
            tmp = faction.member_set.filter(tId=m)
            if len(tmp):
                tmp[0].tId = m
                tmp[0].name = members[m]["name"]
                tmp[0].lastAction = members[m]["last_action"]
                tmp[0].daysInFaction = members[m]["days_in_faction"]
                tmp[0].save()
            else:
                faction.member_set.create(tId=m, name=members[m]["name"], lastAction=members[m]["last_action"], daysInFaction=members[m]["days_in_faction"])

        request.session["onTheFlyMessage"].append("Member list updated")

    return HttpResponseRedirect(reverse('chain:members'))


def report(request, chainId):
    if request.session.get("chainer"):
        factionId = request.session["chainer"].get("factionId")

        try:
            faction = Faction.objects.filter(tId=factionId)[0]
            chain = faction.chain_set.filter(tId=chainId)[0]
            report = chain.report_set.filter(chain=chain)[0]
        except:
            return render(request, 'chain.html')

        context = dict({'chain': chain, 'members': members, 'chains': faction.chain_set.filter(status=True), 'counts': report.count_set.all(), 'bonus': report.bonus_set.all(), "view": {"report": True, "list": True}})
        context = toggleMessage(request, context, "onTheFlyMessage")

        return render(request, 'chain.html', context)
    else:
        return render(request, 'chain.html')


def jointReport(request):
    if request.session.get("chainer"):
        factionId = request.session["chainer"].get("factionId")

        try:
            faction = Faction.objects.filter(tId=factionId)[0]
        except:
            return render(request, 'chain.html')

        chains = faction.chain_set.filter(jointReport=True)

        counts = dict({})
        total = {"nHits": 0, "respect": 0.0}
        for chain in chains:
            for count in chain.report_set.all()[0].count_set.all():
                total["nHits"] += count.wins
                total["respect"] += float(count.respectTotal)
                if count.attackerId in counts:
                    counts[count.attackerId]["hits"] += count.hits
                    counts[count.attackerId]["wins"] += count.wins
                    counts[count.attackerId]["respect"] += count.respect
                    counts[count.attackerId]["respectTotal"] += count.respectTotal
                else:
                    counts[count.attackerId] = {"name": count.name,
                                                "hits": count.hits,
                                                "wins": count.wins,
                                                "respect": count.respect,
                                                "respectTotal": count.respectTotal,
                                                "daysInFaction": count.daysInFaction}

        arrayCounts = [v for k, v in counts.items()]

        context = dict({'chains': faction.chain_set.filter(status=True), 'chainsReport': chains, 'total': total, 'counts': arrayCounts, "view": {"jointReport": True, "list": True}})

        return render(request, 'chain.html', context)
    else:
        return render(request, 'chain.html')


def createReport(request, chainId):
    if request.session.get("chainer") and request.session["chainer"].get("AA"):
        key = request.session["chainer"].get("keyValue")
        factionId = request.session["chainer"].get("factionId")
        request.session["onTheFlyMessage"] = []

        try:
            faction = Faction.objects.filter(tId=factionId)[0]
            chain = faction.chain_set.filter(tId=chainId)[0]
            chain.report_set.all().delete()
            report = chain.report_set.create()
        except:
            return HttpResponseRedirect(reverse('chain:index'))

        members = faction.member_set.all()
        attackers = dict({})  # create attackers array on the fly to avoid db connectio in the loop
        for m in members:
            attackers[m.name] = [0, 0, 0.0, 0.0, m.daysInFaction, m.tId]

        if int(chainId) == 0:
            print("create report live")
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
        else:
            attacks = apiCallAttacks(factionId, chain.start, chain.end, key)
            stopAfterNAttacks = False

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

        request.session["onTheFlyMessage"].append("Report of chain {} updated".format(chainId))

    if int(chainId) == 0:
        return HttpResponseRedirect(reverse('chain:index'))
    else:
        return HttpResponseRedirect(reverse('chain:report', kwargs={"chainId": chainId}))


def deleteReport(request, chainId):
    if request.session.get("chainer"):
        factionId = request.session["chainer"].get("factionId")
        request.session["onTheFlyMessage"] = []

        try:
            faction = Faction.objects.filter(tId=factionId)[0]
            chain = faction.chain_set.filter(tId=chainId)[0]
            chain.report_set.all().delete()
            chain.jointReport = False
            chain.save()
        except:
            pass

        request.session["onTheFlyMessage"].append("Report of chain {} deleted".format(chainId))

    return HttpResponseRedirect(reverse('chain:list'))


def toggleReport(request, chainId):
    if request.session.get("chainer"):
        factionId = request.session["chainer"].get("factionId")
        request.session["onTheFlyMessage"] = []

        try:
            faction = Faction.objects.filter(tId=factionId)[0]
            chain = faction.chain_set.filter(tId=chainId)[0]
            tog = chain.toggle_report()
            chain.save()
            if tog:
                request.session["onTheFlyMessage"].append("Report of chain {} added to joint report".format(chainId))
            else:
                request.session["onTheFlyMessage"].append("Report of chain {} removed from joint report".format(chainId))
        except:
            pass

    return HttpResponseRedirect(reverse('chain:list'))


# UPDATE ON THE FLY
def updateKey(request):
    print("[updateKey]: in")

    # request.session["chainer"] = {'keyValue': "myKeyForDebug",
    #                               'name': "Kivou",
    #                               'playerId': 2000607,
    #                               'factionName': "Nub Navy",
    #                               'factionId': 33241,
    #                               'AA': True,
    #                               }
    # request.session.set_expiry(0)  # logout when close browser
    # return render(request, "chain/login.html")


    if request.method == "POST":
        p = request.POST
        user = apiCall("user", "", "profile", p.get("keyValue"))
        if "apiError" in user:
            return render(request, "chain/{}.html".format(p["html"]), user)

        if user["faction"]["faction_id"] in [33241]:
            AArights = "chains" in apiCall("faction", user["faction"]["faction_id"], "chains", p.get("keyValue"))
            request.session["chainer"] = {'keyValue': p["keyValue"],
                                          'name': user["name"],
                                          'playerId': user["player_id"],
                                          'factionName': user["faction"]["faction_name"],
                                          'factionId': user["faction"]["faction_id"],
                                          'AA': AArights,
                                          }
            check = json.loads(p.get("rememberSession"))
            if check:
                request.session.set_expiry(31536000)  # 1 year
            else:
                request.session.set_expiry(0)  # logout when close browser
            return render(request, "chain/{}.html".format(p["html"]))

        else:
            user = {"apiError": "Sorry but this website is not yet opened to your faction"}
            return render(request, "chain/{}.html".format(p["html"]), user)

    else:
        return HttpResponse("Don't try to be a smart ass, you need to post.")


def logout(request):
    try:
        del request.session["chainer"]
    except:
        pass
    return HttpResponseRedirect(reverse('chain:index'))
