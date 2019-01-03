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
            "Busts": dict(),
            "Total": dict(),
        })

        for k, v in allAwards["honors"].items():
            if v["type"] in [5, 15]:
                vp = v
                vp["awardType"] = "Honor"

                if int(k) in [2, 25, 154, 157, 158]:
                    type = "Theft"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[type]])
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))
                    crimes[type]["h_"+k] = vp
                elif int(k) in [6]  :
                    type = "Other"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[type]])
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))
                    crimes[type]["h_"+k] = vp
                elif int(k) in [24]  :
                    type = "Fraud crimes"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[type]])
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))
                    crimes[type]["h_"+k] = vp
                elif int(k) in [152]  :
                    type = "Illegal products"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[type]])
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))
                    crimes[type]["h_"+k] = vp
                elif int(k) in [153]  :
                    type = "Drug deals"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[type]])
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))
                    crimes[type]["h_"+k] = vp
                elif int(k) in [155, 161]  :
                    type = "Computer crimes"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[type]])
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))
                    crimes[type]["h_"+k] = vp
                elif int(k) in [159]  :
                    type = "Murder"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[type]])
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))
                    crimes[type]["h_"+k] = vp
                elif int(k) in [160]  :
                    type = "Auto theft"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[type]])
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))
                    crimes[type]["h_"+k] = vp
                elif int(k) in [251]  :
                    type = "Total"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[type]])
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))
                    crimes[type]["h_"+k] = vp
                elif int(k) in [552]  :
                    type = "Organised crimes"
                    vp["goal"] = int(v["description"].split(" ")[2].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("organisedcrimes"))
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    crimes[type]["h_"+k] = vp
                elif int(k) in [248, 249, 250]  :
                    # 248 {'name': 'Bar Breaker', 'description': 'Make 1,000 busts', 'type': 15, 'circulation': 4454, 'rarity': 'Rare', 'goal': 1000, 'awardType': 'Honor'}
                    type = "Busts"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("peoplebusted"))
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    crimes[type]["h_"+k] = vp
                elif int(k) in [252]  :
                    # 252 {'name': "Freedom Isn't Free", 'description': 'Make 500 bails from jail', 'type': 15, 'circulation': 2032, 'rarity': 'Extraordinary', 'goal': 500, 'awardType': 'Honor'}
                    type = "Busts"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("peoplebailed"))
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    crimes[type]["h_"+k] = vp

                else:
                    print(k, v)


        for k, v in allAwards["medals"].items():
            vp = v
            vp["awardType"] = "Medal"
            if v["type"] == "CRM":
                print(k, v)
                type = crimeBridgeMedal2App[" ".join(v["description"].split(" ")[2:-1])]
                vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[type]])
                vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))
                crimes[type]["m_"+k] = vp

            elif v["type"] == "OTR":
                if int(k) in [30, 31, 32, 33, 105, 106, 107]:
                    type = "Busts"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("peoplebusted"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))
                    crimes[type]["h_"+k] = vp

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
                    type = "Cannabis"
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                elif int(k) in [29, 30, 31, 32, 33, 34, 35, 36, 37, 38]:
                    type = v["description"].split(" ")[-1]
                    vp["goal"] = 50
                    key = type.lower()[:3]+"taken"
                    vp["current"] = None2Zero(myAwards["personalstats"].get(key))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                drugs[type]["h_"+k] = vp


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
                    type = "Wins"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attackswon"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [28, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 515]:
                    # 28 {'name': 'Machinist', 'description': 'Achieve 100 finishing hits with mechanical weapons', 'type': 2, 'circulation': 9269, 'rarity': 'Limited', 'awardType': 'Honor', 'achieve': 0}
                    type = "Finishing hits"
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
                    type = "Kill streak"
                    vp["goal"] = int(v["description"].split(" ")[-1].replace(",", ""))
                    # vp["current"] = None2Zero(myAwards["personalstats"].get("killstreak"))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("bestkillstreak"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [20, 227]:
                    # 20 {'name': 'Precision', 'description': 'Achieve 25 critical hits', 'type': 8, 'circulation': 133458, 'rarity': 'Very Common'}
                    type = "Critical hits"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attackcriticalhits"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [22, 228]:
                    # 22 {'name': 'Self Defense', 'description': 'Win 50 defends', 'type': 8, 'circulation': 31674, 'rarity': 'Common', 'awardType': 'Honor'}
                    # 228 {'name': '007', 'description': 'Achieve 1,000 attacks and 1,000 defends', 'type': 8, 'circulation': 1710, 'rarity': 'Extraordinary', 'awardType': 'Honor'}
                    type = "Defends"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("defendswon"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [27]:
                    # 27 {'name': 'Night Walker', 'description': 'Make 100 stealthed attacks', 'type': 8, 'circulation': 50474, 'rarity': 'Common', 'awardType': 'Honor'}
                    type = "Miscellaneous"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attacksstealthed"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [140, 151]:
                    # 140 {'name': 'Spray And Pray', 'description': 'Fire 2,500 rounds', 'type': 8, 'circulation': 72720, 'rarity': 'Very Common', 'awardType': 'Honor'}
                    type = "Fire rounds"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("roundsfired"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [230, 254, 481, 500, 615]:
                    # 230 {'name': 'Domino Effect', 'description': 'Defeat someone displaying this honor', 'type': 8, 'circulation': 112529, 'rarity': 'Very Common', 'awardType': 'Honor'}
                    # 254 {'name': 'Flatline', 'description': 'Achieve a one hit kill on a target from full life', 'type': 8, 'circulation': 72276, 'rarity': 'Very Common', 'awardType': 'Honor'}
                    # 500 {'name': 'Survivalist', 'description': 'Win an attack with only 1% life remaining', 'type': 8, 'circulation': 5980, 'rarity': 'Limited', 'awardType': 'Honor'}
                    # 481 {'name': 'Semper     Fortis', 'description': 'Defeat someone more powerful than you', 'type': 8, 'circulation': 29809, 'rarity': 'Common', 'awardType': 'Honor'}
                    # 615 {'name': 'Guardian Angel', 'description': 'Defeat someone while they are attacking someone else', 'type': 8, 'circulation': 6228, 'rarity': 'Limited', 'awardType': 'Honor'}
                    type = "Miscellaneous"
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0

                elif int(k) in [232]:
                    # 232 {'name': 'Bounty Hunter', 'description': 'Collect 250 bounties', 'type': 8, 'circulation': 3942, 'rarity': 'Rare', 'awardType': 'Honor'}
                    type = "Bounties"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("bountiescollected"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [236]:
                    # 236 {'name': 'Dead Or Alive', 'description': 'Earn $10,000,000 from bounty hunting', 'type': 8, 'circulation': 12012, 'rarity': 'Uncommon', 'awardType': 'Honor'}
                    type = "Bounties"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", "").replace("$", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("totalbountyreward"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [247]:
                    # 247 {'name': 'Blood Money', 'description': 'Make $1,000,000 from a single mugging', 'type': 8, 'circulation': 32879, 'rarity': 'Common', 'awardType': 'Honor'}
                    type = "Miscellaneous"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", "").replace("$", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("largestmug"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [270]:
                    # 270 {'name': 'Deadlock', 'description': 'Stalemate 100 times', 'type': 8, 'circulation': 5194, 'rarity': 'Rare', 'awardType': 'Honor'}
                    type = "Miscellaneous"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attacksdraw")) + None2Zero(myAwards["personalstats"].get("defendsstalemated"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [639]:
                    # 639 {'name': 'Double Dragon', 'description': 'Assist in a single attack', 'type': 8, 'circulation': 5413, 'rarity': 'Rare', 'awardType': 'Honor'}
                    type = "Assists"
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0

                elif int(k) in [490]:
                    # 490 {'name': 'Sidekick', 'description': 'Assist in 250 attacks', 'type': 8, 'circulation': 59, 'rarity': 'Extremely Rare', 'awardType': 'Honor'}
                    type = "Assists"
                    vp["goal"] = int(v["description"].split(" ")[2].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attacksassisted"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [253, 255, 257, 475, 476]:
                    # 253 {'name': 'Chainer 1', 'description': 'Participate in a 10 length chain', 'type': 8, 'circulation': 39418, 'rarity': 'Common', 'awardType': 'Honor'}
                    type = "Chains"
                    vp["goal"] = int(v["description"].split(" ")[3].replace(",", ""))
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0

                elif int(k) in [256, 477, 478]:
                    # 256 {'name': 'Carnage', 'description': 'Make a single hit that earns your faction 10 or more respect', 'type': 8, 'circulation': 19716, 'rarity': 'Uncommon', 'awardType': 'Honor'}
                    type = "Respects"
                    vp["goal"] = int(v["description"].split(" ")[8].replace(",", ""))
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0

                elif int(k) in [517]:
                    # 517 {'name': 'Pressure Point', 'description': 'Achieve 100 one hit kills', 'type': 8, 'circulation': 13351, 'rarity': 'Uncommon', 'awardType': 'Honor'}
                    type = "Miscellaneous"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("onehitkills"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [601]:
                    # 601 {'name': 'Fury', 'description': 'Achieve 10,000 hits', 'type': 8, 'circulation': 8172, 'rarity': 'Limited', 'awardType': 'Honor'}
                    type = "Miscellaneous"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attackhits"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [50, 51, 52]:
                    # 50 {'name': 'Zebra Skin', 'description': 'Achieve 50 skill in hunting', 'type': 3, 'circulation': 12055, 'rarity': 'Uncommon', 'awardType': 'Honor', 'achieve': 0}
                    ignore = True

                else:
                    type = "?"
                    vp["achieve"] = 0
                    print(k, v)

                if not ignore:
                    attacks[type]["h_"+k] = vp

        for k, v in allAwards["medals"].items():
            if v["type"] == "ATK":
                vp = v
                vp["awardType"] = "Medal"

                if int(k) in [174, 175, 176, 177, 178]:
                    # 174 {'name': 'Anti Social', 'description': 'Win 50 attacks', 'type': 'ATK'}
                    type = "Wins"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attackswon"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [179, 180, 181, 182, 183]:
                    # 179 {'name': 'Bouncer', 'description': 'Successfully defend against 50 attacks', 'type': 'ATK', 'awardType': 'Medals'}
                    type = "Defends"
                    vp["goal"] = int(v["description"].split(" ")[-2].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("defendswon"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [184, 185, 186]:
                    # 184 {'name': 'Close Escape', 'description': 'Successfully escape from 50 foes', 'type': 'ATK', 'awardType': 'Medal'}
                    type = "Escapes"
                    vp["goal"] = int(v["description"].split(" ")[-2].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("yourunaway"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [187, 188, 189]:
                    # 187 {'name': 'Ego Smashing', 'description': 'Have 50 enemies escape from you during an attack', 'type': 'ATK', 'awardType': 'Medal'}
                    type = "Escapes"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("theyrunaway"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [190, 191, 192, 193, 194]:
                    # 190 {'name': 'Strike', 'description': 'Acquire a kill streak of 25', 'type': 'ATK', 'awardType': 'Medal'}
                    type = "Kill streak"
                    vp["goal"] = int(v["description"].split(" ")[-1].replace(",", ""))
                    # vp["current"] = None2Zero(myAwards["personalstats"].get("killstreak"))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("bestkillstreak"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [195, 196, 197]:
                    # 195 {'name': 'Boom Headshot', 'description': 'Deal 500 critical hits to enemies during combat', 'type': 'ATK', 'awardType': 'Medal'}
                    type = "Critical hits"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attackcriticalhits"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [201, 202, 203]:
                    # 201 {'name': 'Hired Gun', 'description': 'Collect 25 bounties', 'type': 'ATK', 'awardType': 'Medal', 'goal': 25, 'current': 160, 'achieve': 1}
                    type = "Bounties"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("bountiescollected"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [215, 216, 217, 218, 219, 220, 221, 222, 223, 224]:
                    # 215 {'name': 'Recruit', 'description': 'Earn 100 respect for your faction', 'type': 'ATK', 'awardType': 'Medal'}
                    type = "Respects"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("respectforfaction"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                else:
                    type = "?"
                    print(k, v)

                attacks[type]["m_"+k] = vp

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

def items(request):
    if request.session.get('awards'):
        key = request.session['awards'].get('keyValue')
        allAwards = apiCall('torn', '', 'honors,medals', key)
        if 'apiError' in allAwards:
            return render(request, 'errorPage.html', allAwards)
        myAwards = apiCall('user', '', 'personalstats,medals,honors', key)
        if 'apiError' in myAwards:
            return render(request, 'errorPage.html', myAwards)

        # fill items awards
        items = dict({
            "City Finds": dict(),
            "Medical items": dict(),
            "?": dict(),
        })

        for k, v in allAwards["honors"].items():
            if int(v["type"]) in [15]:
                vp = v
                vp["awardType"] = "Honor"
                ignore = False

                if int(k) in [398, 418]:
                    # 398 {'name': 'Anaemic', 'description': 'Fill 1,000 empty blood bags', 'type': 15, 'circulation': 3823, 'rarity': 'Rare', 'awardType': 'Honor', 'goal': 1000, 'current': 0, 'achieve': 0.0}
                    type = "Medical items"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("bloodwithdrawn"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [367, 406]:
                    # 406 {'name': 'Vampire', 'description': 'Random chance upon using a blood bag', 'type': 15, 'circulation': 10562, 'rarity': 'Limited', 'awardType': 'Honor', 'achieve': 0}
                    # 367 {'name': 'Clotted', 'description': 'Suffer from an acute haemolytic reaction, or be immune to it', 'type': 15, 'circulation': 11247, 'rarity': 'Uncommon', 'awardType': 'Honor', 'achieve': 0}
                    type = "Medical items"
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0

                elif int(k) in [4]:
                    # 4 {'name': "I'm a Real Doctor", 'description': 'Steal 500 medical items', 'type': 15, 'circulation': 24992, 'rarity': 'Common', 'awardType': 'Honor', 'achieve': 0}
                    type = "Medical items"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("medstolen"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [7]:
                    # 7 {'name': 'Magical Veins', 'description': 'Use 5,000 medical items', 'type': 15, 'circulation': 4686, 'rarity': 'Rare', 'awardType': 'Honor', 'achieve': 0}
                    type = "Medical items"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("medicalitemsused"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [23, 248, 249, 250, 252, 267]:
                    ignore = True

                else:
                    type = "?"
                    vp["achieve"] = 0
                    print(k, v)

                if not ignore:
                    items[type]["h_"+k] = vp

        for k, v in allAwards["medals"].items():
            if v["type"] == "OTR":
                vp = v
                vp["awardType"] = "Medal"
                ignore = False

                if int(k) in [204, 205, 206]:
                    # 204 {'name': 'Watchful', 'description': 'Find 10 items in the city', 'type': 'OTR', 'awardType': 'Medal', 'goal': 10, 'current': 0, 'achieve': 0.0}
                    type = "City Finds"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("cityfinds"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [198, 199, 200]:
                    # 198 {'name': 'Pin Cushion', 'description': 'Use 500 medical items', 'type': 'OTR', 'awardType': 'Medal', 'goal': 500, 'current': 0, 'achieve': 0.0}
                    type = "Medical items"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("medicalitemsused"))
                    vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                # elif int(k) in [207, 208, 209]:
                #     # 207 {'name': 'Frequent Flyer', 'description': 'Travel abroad 25 times', 'type': 'OTR', 'awardType': 'Medal', 'achieve': 0}
                #     type = "Travels"
                #     vp["goal"] = int(v["description"].split(" ")[2].replace(",", ""))
                #     vp["current"] = None2Zero(myAwards["personalstats"].get("traveltimes"))
                #     vp["achieve"] = min(1, float(vp["current"])/float(vp["goal"]))

                elif int(k) in [30, 31, 32, 33, 105, 106, 107, 207, 208, 209]:
                    ignore = True

                else:
                    type = "?"
                    vp["achieve"] = 0
                    print(k, v)

                if not ignore:
                    items[type]["h_"+k] = vp

        itemsSummary = dict()
        for k, v in items.items():
            n = 0
            for l, w in v.items():
                if w["achieve"] == 1:
                    n += 1
            itemsSummary[k] = {"nAwarded": n, "nAwards": len(v)}

        out = {"items": items, "itemsSummary": itemsSummary}
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
