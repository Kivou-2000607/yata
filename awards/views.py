from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone

import json
from yata.handy import apiCall
from yata.handy import None2Zero

def index(request):
    return render(request, 'awards.html')


def crimes(request):
    if request.session.get('awards'):
        key = request.session['awards'].get('keyValue')
        allAwards = apiCall('torn', '', 'honors,medals', key)
        if 'apiError' in allAwards:
            return render(request, 'errorPage.html', allAwards)
        myAwards = apiCall('user', '', 'personalstats,crimes,medals,honors', key)
        if 'apiError' in myAwards:
            return render(request, 'errorPage.html', myAwards)

        crimeBridgeMedal2App = {
                            "Computer": "Computer crimes",
                            "Murder": "Murder",
                            "Grand theft auto": "Auto theft",
                            "Theft": "Theft",
                            "Drug dealing": "Drug deals",
                            "Arson": "Fraud crimes"
                    }

        crimeBridgeApp2API = {
                            "Computer crimes": "computer_crimes",
                            "Illegal products": "selling_illegal_products",
                            "Murder": "murder",
                            "Auto theft": "auto_theft",
                            "Theft": "theft",
                            "Drug deals": "drug_deals",
                            "Fraud crimes": "fraud_crimes",
                            "Other": "other",
                            "Total": "total",
                    }

        # fill crimes awards
        crimes = dict({
            "Illegal products": dict(),
            "Theft": dict(),
            "Auto theft": dict(),
            "Drug deals": dict(),
            "Computer crimes": dict(),
            "Murder": dict(),
            "Fraud crimes": dict(),
            "Other": dict(),
            "Organised crimes": dict(),
            "Total": dict(),
        })

        for k, v in allAwards["honors"].items():
            if v["type"] == 5:
                gotIt = False
                i = 0
                n = 0
                while not gotIt:
                    try:
                        n = int(v["description"].split(" ")[i].replace(",", ""))
                        gotIt = True
                    except:
                        i += 1
                vp = v
                vp["goal"] = n
                vp["awardType"] = "Honor"

                if int(k) in [2, 25, 154, 157, 158]:
                    ctype = "Theft"
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[ctype]])
                    vp["achieve"] = min(1, float(vp["current"])/float(n))
                    crimes[ctype]["h_"+k] = vp
                elif int(k) in [6]  :
                    ctype = "Other"
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[ctype]])
                    vp["achieve"] = min(1, float(vp["current"])/float(n))
                    crimes[ctype]["h_"+k] = vp
                elif int(k) in [24]  :
                    ctype = "Fraud crimes"
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[ctype]])
                    vp["achieve"] = min(1, float(vp["current"])/float(n))
                    crimes[ctype]["h_"+k] = vp
                elif int(k) in [152]  :
                    ctype = "Illegal products"
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[ctype]])
                    vp["achieve"] = min(1, float(vp["current"])/float(n))
                    crimes[ctype]["h_"+k] = vp
                elif int(k) in [153]  :
                    ctype = "Drug deals"
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[ctype]])
                    vp["achieve"] = min(1, float(vp["current"])/float(n))
                    crimes[ctype]["h_"+k] = vp
                elif int(k) in [155, 161]  :
                    ctype = "Computer crimes"
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[ctype]])
                    vp["achieve"] = min(1, float(vp["current"])/float(n))
                    crimes[ctype]["h_"+k] = vp
                elif int(k) in [159]  :
                    ctype = "Murder"
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[ctype]])
                    vp["achieve"] = min(1, float(vp["current"])/float(n))
                    crimes[ctype]["h_"+k] = vp
                elif int(k) in [160]  :
                    ctype = "Auto theft"
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[ctype]])
                    vp["achieve"] = min(1, float(vp["current"])/float(n))
                    crimes[ctype]["h_"+k] = vp
                elif int(k) in [251]  :
                    ctype = "Total"
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[ctype]])
                    vp["achieve"] = min(1, float(vp["current"])/float(n))
                    crimes[ctype]["h_"+k] = vp
                elif int(k) in [552]  :
                    ctype = "Organised crimes"
                    vp["current"] = None2Zero(myAwards["personalstats"].get("organisedcrimes"))
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    crimes[ctype]["h_"+k] = vp

        for k, v in allAwards["medals"].items():
            if v["type"] == "CRM":
                print(k, v)
                ctype = crimeBridgeMedal2App[" ".join(v["description"].split(" ")[2:-1])]
                n = int(v["description"].split(" ")[1].replace(",", ""))
                vp = v
                vp["goal"] = n
                vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[ctype]])
                vp["achieve"] = min(1, float(vp["current"])/float(n))
                vp["awardType"] = "Medal"
                crimes[ctype]["m_"+k] = vp


        crimesSummary = dict()
        for k, v in crimes.items():
            n = 0
            for l, w in v.items():
                if w["achieve"] == 1:
                    n += 1
            crimesSummary[k] = {"nAwarded": n, "nAwards": len(v)}

        for k, v in crimesSummary.items():
            print(k,v)

        out = {"crimes": crimes, "crimesSummary": crimesSummary}
        return render(request, 'awards.html', out)

    return render(request, 'awards.html')

def drugs(request):
    if request.session.get('awards'):
        key = request.session['awards'].get('keyValue')
        allAwards = apiCall('torn', '', 'honors,medals', key)
        if 'apiError' in allAwards:
            return render(request, 'errorPage.html', allAwards)
        myAwards = apiCall('user', '', 'personalstats,medals,honors', key)
        if 'apiError' in myAwards:
            return render(request, 'errorPage.html', myAwards)

        # fill drugs awards
        drugs = dict({
            "Cannabis": dict(),
            "Ecstasy": dict(),
            "Ketamine": dict(),
            "LSD": dict(),
            "Opium": dict(),
            "Shrooms": dict(),
            "Speed": dict(),
            "PCP": dict(),
            "Xanax": dict(),
            "Vicodin": dict(),
        })

        for k, v in allAwards["honors"].items():
            if v["type"] == 6:
                print(k, v)
                vp = v
                vp["awardType"] = "Honor"

                if int(k) in [26]:
                    dtype = "Cannabis"
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                elif int(k) in [29, 30, 31, 32, 33, 34, 35, 36, 37, 38]:
                    dtype = v["description"].split(" ")[-1]
                    vp["goal"] = 50
                    key = dtype.lower()[:3]+"taken"
                    vp["current"] = None2Zero(myAwards["personalstats"].get(key))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                drugs[dtype]["h_"+k] = vp


        drugsSummary = dict()
        for k, v in drugs.items():
            n = 0
            for l, w in v.items():
                if w["achieve"] == 1:
                    n += 1
            drugsSummary[k] = {"nAwarded": n, "nAwards": len(v)}

        out = {"drugs": drugs, "drugsSummary": drugsSummary}
        return render(request, 'awards.html', out)

    return render(request, 'awards.html')


def attacks(request):
    if request.session.get('awards'):
        key = request.session['awards'].get('keyValue')
        allAwards = apiCall('torn', '', 'honors,medals', key)
        if 'apiError' in allAwards:
            return render(request, 'errorPage.html', allAwards)
        myAwards = apiCall('user', '', 'personalstats,medals,honors', key)
        if 'apiError' in myAwards:
            return render(request, 'errorPage.html', myAwards)

        # fill attacks awards
        attacks = dict({
            "Wins": dict(),
            "Defends": dict(),
            "Escapes": dict(),
            "Kill streak": dict(),
            "Critical hits": dict(),
            "Bounties": dict(),
            "Respects": dict(),
            "Stealth": dict(),
            "Fire rounds": dict(),
            "Miscellaneous": dict(),
            "Mugs": dict(),
            "Stalemates": dict(),
            "Assists": dict(),
            "Chains": dict(),
            "Finishing hits": dict(),
            "?": dict(),
        })

        for k, v in allAwards["honors"].items():
            if int(v["type"]) in [8, 2, 3]:
                vp = v
                vp["awardType"] = "Honor"
                ignore = False

                if int(k) in [39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49]:
                    # 39 {'name': 'Woodland Camo', 'description': 'Win 5 attacks', 'type': 3, 'circulation': 205626, 'rarity': 'Very Common', 'awardType': 'Honor', 'achieve': 0}
                    dtype = "Wins"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attackswon"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [28, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 515]:
                    # 28 {'name': 'Machinist', 'description': 'Achieve 100 finishing hits with mechanical weapons', 'type': 2, 'circulation': 9269, 'rarity': 'Limited', 'awardType': 'Honor', 'achieve': 0}
                    dtype = "Finishing hits"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))

                    end = " ".join(v["description"].split(" ")[5:])
                    key = end.lower()[:3]+"hits"
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
                    vp["current"] = None2Zero(myAwards["personalstats"].get(bridge[key]))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [15, 16, 17]:
                    # 15 {'name': 'Kill Streaker 1', 'description': 'Achieve a best killstreak of 10', 'type': 8, 'circulation': 124231, 'rarity': 'Very Common'}
                    dtype = "Kill streak"
                    vp["goal"] = int(v["description"].split(" ")[-1].replace(",", ""))
                    # vp["current"] = None2Zero(myAwards["personalstats"].get("killstreak"))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("bestkillstreak"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [20, 227]:
                    # 20 {'name': 'Precision', 'description': 'Achieve 25 critical hits', 'type': 8, 'circulation': 133458, 'rarity': 'Very Common'}
                    dtype = "Critical hits"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attackcriticalhits"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [22, 228]:
                    # 22 {'name': 'Self Defense', 'description': 'Win 50 defends', 'type': 8, 'circulation': 31674, 'rarity': 'Common', 'awardType': 'Honor'}
                    # 228 {'name': '007', 'description': 'Achieve 1,000 attacks and 1,000 defends', 'type': 8, 'circulation': 1710, 'rarity': 'Extraordinary', 'awardType': 'Honor'}
                    dtype = "Defends"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("defendswon"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [27]:
                    # 27 {'name': 'Night Walker', 'description': 'Make 100 stealthed attacks', 'type': 8, 'circulation': 50474, 'rarity': 'Common', 'awardType': 'Honor'}
                    dtype = "Miscellaneous"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attacksstealthed"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [140, 151]:
                    # 140 {'name': 'Spray And Pray', 'description': 'Fire 2,500 rounds', 'type': 8, 'circulation': 72720, 'rarity': 'Very Common', 'awardType': 'Honor'}
                    dtype = "Fire rounds"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("roundsfired"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [230, 254, 481, 500, 615]:
                    # 230 {'name': 'Domino Effect', 'description': 'Defeat someone displaying this honor', 'type': 8, 'circulation': 112529, 'rarity': 'Very Common', 'awardType': 'Honor'}
                    # 254 {'name': 'Flatline', 'description': 'Achieve a one hit kill on a target from full life', 'type': 8, 'circulation': 72276, 'rarity': 'Very Common', 'awardType': 'Honor'}
                    # 500 {'name': 'Survivalist', 'description': 'Win an attack with only 1% life remaining', 'type': 8, 'circulation': 5980, 'rarity': 'Limited', 'awardType': 'Honor'}
                    # 481 {'name': 'Semper     Fortis', 'description': 'Defeat someone more powerful than you', 'type': 8, 'circulation': 29809, 'rarity': 'Common', 'awardType': 'Honor'}
                    # 615 {'name': 'Guardian Angel', 'description': 'Defeat someone while they are attacking someone else', 'type': 8, 'circulation': 6228, 'rarity': 'Limited', 'awardType': 'Honor'}
                    dtype = "Miscellaneous"
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0

                elif int(k) in [232]:
                    # 232 {'name': 'Bounty Hunter', 'description': 'Collect 250 bounties', 'type': 8, 'circulation': 3942, 'rarity': 'Rare', 'awardType': 'Honor'}
                    dtype = "Bounties"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("bountiescollected"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [236]:
                    # 236 {'name': 'Dead Or Alive', 'description': 'Earn $10,000,000 from bounty hunting', 'type': 8, 'circulation': 12012, 'rarity': 'Uncommon', 'awardType': 'Honor'}
                    dtype = "Bounties"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", "").replace("$", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("totalbountyreward"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [247]:
                    # 247 {'name': 'Blood Money', 'description': 'Make $1,000,000 from a single mugging', 'type': 8, 'circulation': 32879, 'rarity': 'Common', 'awardType': 'Honor'}
                    dtype = "Miscellaneous"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", "").replace("$", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("largestmug"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [270]:
                    # 270 {'name': 'Deadlock', 'description': 'Stalemate 100 times', 'type': 8, 'circulation': 5194, 'rarity': 'Rare', 'awardType': 'Honor'}
                    dtype = "Miscellaneous"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attacksdraw")) + None2Zero(myAwards["personalstats"].get("defendsstalemated"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [639]:
                    # 639 {'name': 'Double Dragon', 'description': 'Assist in a single attack', 'type': 8, 'circulation': 5413, 'rarity': 'Rare', 'awardType': 'Honor'}
                    dtype = "Assists"
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0

                elif int(k) in [490]:
                    # 490 {'name': 'Sidekick', 'description': 'Assist in 250 attacks', 'type': 8, 'circulation': 59, 'rarity': 'Extremely Rare', 'awardType': 'Honor'}
                    dtype = "Assists"
                    vp["goal"] = int(v["description"].split(" ")[2].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attacksassisted"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [253, 255, 257, 475, 476]:
                    # 253 {'name': 'Chainer 1', 'description': 'Participate in a 10 length chain', 'type': 8, 'circulation': 39418, 'rarity': 'Common', 'awardType': 'Honor'}
                    dtype = "Chains"
                    vp["goal"] = int(v["description"].split(" ")[3].replace(",", ""))
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0

                elif int(k) in [256, 477, 478]:
                    # 256 {'name': 'Carnage', 'description': 'Make a single hit that earns your faction 10 or more respect', 'type': 8, 'circulation': 19716, 'rarity': 'Uncommon', 'awardType': 'Honor'}
                    dtype = "Respects"
                    vp["goal"] = int(v["description"].split(" ")[8].replace(",", ""))
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0

                elif int(k) in [517]:
                    # 517 {'name': 'Pressure Point', 'description': 'Achieve 100 one hit kills', 'type': 8, 'circulation': 13351, 'rarity': 'Uncommon', 'awardType': 'Honor'}
                    dtype = "Miscellaneous"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("onehitkills"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [601]:
                    # 601 {'name': 'Fury', 'description': 'Achieve 10,000 hits', 'type': 8, 'circulation': 8172, 'rarity': 'Limited', 'awardType': 'Honor'}
                    dtype = "Miscellaneous"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attackhits"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [50, 51, 52]:
                    # 50 {'name': 'Zebra Skin', 'description': 'Achieve 50 skill in hunting', 'type': 3, 'circulation': 12055, 'rarity': 'Uncommon', 'awardType': 'Honor', 'achieve': 0}
                    ignore = True

                else:
                    dtype = "?"
                    vp["achieve"] = 0
                    print(k, v)

                if not ignore:
                    attacks[dtype]["h_"+k] = vp

        for k, v in allAwards["medals"].items():
            if v["type"] == "ATK":
                vp = v
                vp["awardType"] = "Medal"

                if int(k) in [174, 175, 176, 177, 178]:
                    # 174 {'name': 'Anti Social', 'description': 'Win 50 attacks', 'type': 'ATK'}
                    atype = "Wins"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attackswon"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [179, 180, 181, 182, 183]:
                    # 179 {'name': 'Bouncer', 'description': 'Successfully defend against 50 attacks', 'type': 'ATK', 'awardType': 'Medals'}
                    atype = "Defends"
                    vp["goal"] = int(v["description"].split(" ")[-2].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("defendswon"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [184, 185, 186]:
                    # 184 {'name': 'Close Escape', 'description': 'Successfully escape from 50 foes', 'type': 'ATK', 'awardType': 'Medal'}
                    atype = "Escapes"
                    vp["goal"] = int(v["description"].split(" ")[-2].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("yourunaway"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [187, 188, 189]:
                    # 187 {'name': 'Ego Smashing', 'description': 'Have 50 enemies escape from you during an attack', 'type': 'ATK', 'awardType': 'Medal'}
                    atype = "Escapes"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("theyrunaway"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [190, 191, 192, 193, 194]:
                    # 190 {'name': 'Strike', 'description': 'Acquire a kill streak of 25', 'type': 'ATK', 'awardType': 'Medal'}
                    atype = "Kill streak"
                    vp["goal"] = int(v["description"].split(" ")[-1].replace(",", ""))
                    # vp["current"] = None2Zero(myAwards["personalstats"].get("killstreak"))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("bestkillstreak"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [195, 196, 197]:
                    # 195 {'name': 'Boom Headshot', 'description': 'Deal 500 critical hits to enemies during combat', 'type': 'ATK', 'awardType': 'Medal'}
                    atype = "Critical hits"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attackcriticalhits"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [201, 202, 203]:
                    # 201 {'name': 'Hired Gun', 'description': 'Collect 25 bounties', 'type': 'ATK', 'awardType': 'Medal', 'goal': 25, 'current': 160, 'achieve': 1}
                    atype = "Bounties"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("bountiescollected"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [215, 216, 217, 218, 219, 220, 221, 222, 223, 224]:
                    # 215 {'name': 'Recruit', 'description': 'Earn 100 respect for your faction', 'type': 'ATK', 'awardType': 'Medal'}
                    atype = "Respects"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("respectforfaction"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                else:
                    dtype = "?"
                    print(k, v)

                attacks[atype]["m_"+k] = vp

        attacksSummary = dict()
        for k, v in attacks.items():
            n = 0
            for l, w in v.items():
                if w["achieve"] == 1:
                    n += 1
            attacksSummary[k] = {"nAwarded": n, "nAwards": len(v)}

        out = {"attacks": attacks, "attacksSummary": attacksSummary}
        return render(request, 'awards.html', out)

    return render(request, 'awards.html')


# UPDATE ON THE FLY
def updateKey(request):
    print('[updateKey] in')

    # request.session['chainer'] = {'keyValue': 'myKeyForDebug',
    #                               'name': 'Kivou',
    #                               'playerId': 2000607,
    #                               'factionName': 'Nub Navy',
    #                               'factionId': 33241,
    #                               'AA': True,
    #                               }
    # request.session.set_expiry(0)  # logout when close browser
    # return render(request, 'chain/login.html')

    if request.method == 'POST':
        p = request.POST
        user = apiCall('user', '', 'profile', p.get('keyValue'))
        if 'apiError' in user:
            return render(request, 'chain/{}.html'.format(p['html']), user)

        request.session['awards'] = {'keyValue': p['keyValue'],
                                     'name': user['name'],
                                     'playerId': user['player_id']
                                     }
        check = json.loads(p.get('rememberSession'))
        if check:
            request.session.set_expiry(31536000)  # 1 year
        else:
            request.session.set_expiry(0)  # logout when close browser
        return render(request, 'awards/{}.html'.format(p['html']))

    else:
        return HttpResponse('Don\'t try to be a smart ass, you need to post.')


def logout(request):
    try:
        del request.session['awards']
    except:
        pass
    return HttpResponseRedirect(reverse('awards:index'))
