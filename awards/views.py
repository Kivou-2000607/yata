from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect

import json
from yata.handy import apiCall
from yata.handy import None2Zero
from yata.handy import honorId2Img
from yata.handy import createAwardSummary


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
            "Arson": "Fraud crimes"}

        crimeBridgeApp2API = {
            "Computer crimes": "computer_crimes",
            "Illegal products": "selling_illegal_products",
            "Murder": "murder",
            "Auto theft": "auto_theft",
            "Theft": "theft",
            "Drug deals": "drug_deals",
            "Fraud crimes": "fraud_crimes",
            "Other": "other",
            "Total": "total"}

        awards = dict({
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
            "Total": dict()})

        for k, v in allAwards["honors"].items():
            if v["type"] in [5, 15]:
                vp = v
                vp["awardType"] = "Honor"
                vp["img"] = honorId2Img(int(k))
                vp["title"] = "{} [{}]: {} ({})".format(vp["name"], k, vp["rarity"], vp["circulation"])

                if int(k) in [2, 25, 154, 157, 158]:
                    type = "Theft"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[type]])
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [6]:
                    type = "Other"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[type]])
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [24]:
                    type = "Fraud crimes"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[type]])
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [152]:
                    type = "Illegal products"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[type]])
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [153]:
                    type = "Drug deals"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[type]])
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [155, 161]:
                    type = "Computer crimes"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[type]])
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [159]:
                    type = "Murder"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[type]])
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [160]:
                    type = "Auto theft"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[type]])
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [251]:
                    type = "Total"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[type]])
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [552]:
                    type = "Organised crimes"
                    vp["goal"] = int(v["description"].split(" ")[2].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("organisedcrimes"))
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    awards[type]["h_" + k] = vp
                elif int(k) in [248, 249, 250]:
                    # 248 {'name': 'Bar Breaker', 'description': 'Make 1,000 busts', 'type': 15, 'circulation': 4454, 'rarity': 'Rare', 'goal': 1000, 'awardType': 'Honor'}
                    type = "Busts"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("peoplebusted"))
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    awards[type]["h_" + k] = vp
                elif int(k) in [252]:
                    # 252 {'name': "Freedom Isn't Free", 'description': 'Make 500 bails from jail', 'type': 15, 'circulation': 2032, 'rarity': 'Extraordinary', 'goal': 500, 'awardType': 'Honor'}
                    type = "Busts"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("peoplebailed"))
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    awards[type]["h_" + k] = vp

                else:
                    print(k, v)

        for k, v in allAwards["medals"].items():
            vp = v
            vp["awardType"] = "Medal"
            if v["type"] == "CRM":
                type = crimeBridgeMedal2App[" ".join(v["description"].split(" ")[2:-1])]
                vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                vp["current"] = None2Zero(myAwards["criminalrecord"][crimeBridgeApp2API[type]])
                vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                awards[type]["m_" + k] = vp
            elif v["type"] == "OTR":
                if int(k) in [30, 31, 32, 33, 105, 106, 107]:
                    type = "Busts"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("peoplebusted"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["m_" + k] = vp
                else:
                    print(k, v)

        awardsSummary = createAwardSummary(awards)

        out = {"awards": awards, "awardsSummary": awardsSummary}
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

        awards = dict({
            "Cannabis": dict(),
            "Ecstasy": dict(),
            "Ketamine": dict(),
            "LSD": dict(),
            "Opium": dict(),
            "Shrooms": dict(),
            "Speed": dict(),
            "PCP": dict(),
            "Xanax": dict(),
            "Vicodin": dict()})

        for k, v in allAwards["honors"].items():
            if v["type"] == 6:
                vp = v
                vp["awardType"] = "Honor"
                vp["img"] = honorId2Img(int(k))
                vp["title"] = "{} [{}]: {} ({})".format(vp["name"], k, vp["rarity"], vp["circulation"])

                if int(k) in [26]:
                    type = "Cannabis"
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    awards[type]["h_" + k] = vp
                elif int(k) in [29, 30, 31, 32, 33, 34, 35, 36, 37, 38]:
                    type = v["description"].split(" ")[-1]
                    vp["goal"] = 50
                    key = type.lower()[:3] + "taken"
                    if key == "ecstaken":
                        key = "exttaken"
                    vp["current"] = None2Zero(myAwards["personalstats"].get(key))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                else:
                    print(k, v)

        awardsSummary = createAwardSummary(awards)

        out = {"awards": awards, "awardsSummary": awardsSummary}
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

        awards = dict({
            "Wins": dict(),
            "Defends": dict(),
            "Escapes": dict(),
            "Kill streak": dict(),
            "Critical hits": dict(),
            "Bounties": dict(),
            "Respects": dict(),
            "Fire rounds": dict(),
            "Miscellaneous": dict(),
            "Assists": dict(),
            "Chains": dict(),
            "Finishing hits": dict()})

        for k, v in allAwards["honors"].items():
            if int(v["type"]) in [8, 2, 3]:
                vp = v
                vp["awardType"] = "Honor"
                vp["img"] = honorId2Img(int(k))
                vp["title"] = "{} [{}]: {} ({})".format(vp["name"], k, vp["rarity"], vp["circulation"])

                if int(k) in [39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49]:
                    # 39 {'name': 'Woodland Camo', 'description': 'Win 5 awards', 'type': 3, 'circulation': 205626, 'rarity': 'Very Common', 'awardType': 'Honor', 'achieve': 0}
                    type = "Wins"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attackswon"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [28, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 515]:
                    # 28 {'name': 'Machinist', 'description': 'Achieve 100 finishing hits with mechanical weapons', 'type': 2, 'circulation': 9269, 'rarity': 'Limited', 'awardType': 'Honor', 'achieve': 0}
                    type = "Finishing hits"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    end = " ".join(v["description"].split(" ")[5:])
                    key = end.lower()[:3] + "hits"
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
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [15, 16, 17]:
                    # 15 {'name': 'Kill Streaker 1', 'description': 'Achieve a best killstreak of 10', 'type': 8, 'circulation': 124231, 'rarity': 'Very Common'}
                    type = "Kill streak"
                    vp["goal"] = int(v["description"].split(" ")[-1].replace(",", ""))
                    # vp["current"] = None2Zero(myAwards["personalstats"].get("killstreak"))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("bestkillstreak"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [20, 227]:
                    # 20 {'name': 'Precision', 'description': 'Achieve 25 critical hits', 'type': 8, 'circulation': 133458, 'rarity': 'Very Common'}
                    type = "Critical hits"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attackcriticalhits"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [22, 228]:
                    # 22 {'name': 'Self Defense', 'description': 'Win 50 defends', 'type': 8, 'circulation': 31674, 'rarity': 'Common', 'awardType': 'Honor'}
                    # 228 {'name': '007', 'description': 'Achieve 1,000 attacks and 1,000 defends', 'type': 8, 'circulation': 1710, 'rarity': 'Extraordinary', 'awardType': 'Honor'}
                    type = "Defends"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("defendswon"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [27]:
                    # 27 {'name': 'Night Walker', 'description': 'Make 100 stealthed attacks', 'type': 8, 'circulation': 50474, 'rarity': 'Common', 'awardType': 'Honor'}
                    type = "Miscellaneous"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attacksstealthed"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [140, 151]:
                    # 140 {'name': 'Spray And Pray', 'description': 'Fire 2,500 rounds', 'type': 8, 'circulation': 72720, 'rarity': 'Very Common', 'awardType': 'Honor'}
                    type = "Fire rounds"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("roundsfired"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
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
                    awards[type]["h_" + k] = vp
                elif int(k) in [232]:
                    # 232 {'name': 'Bounty Hunter', 'description': 'Collect 250 bounties', 'type': 8, 'circulation': 3942, 'rarity': 'Rare', 'awardType': 'Honor'}
                    type = "Bounties"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("bountiescollected"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [236]:
                    # 236 {'name': 'Dead Or Alive', 'description': 'Earn $10,000,000 from bounty hunting', 'type': 8, 'circulation': 12012, 'rarity': 'Uncommon', 'awardType': 'Honor'}
                    type = "Bounties"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", "").replace("$", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("totalbountyreward"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["head"] = "$"
                    awards[type]["h_" + k] = vp
                elif int(k) in [247]:
                    # 247 {'name': 'Blood Money', 'description': 'Make $1,000,000 from a single mugging', 'type': 8, 'circulation': 32879, 'rarity': 'Common', 'awardType': 'Honor'}
                    type = "Miscellaneous"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", "").replace("$", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("largestmug"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["head"] = "$"
                    awards[type]["h_" + k] = vp
                elif int(k) in [270]:
                    # 270 {'name': 'Deadlock', 'description': 'Stalemate 100 times', 'type': 8, 'circulation': 5194, 'rarity': 'Rare', 'awardType': 'Honor'}
                    type = "Miscellaneous"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attacksdraw")) + None2Zero(myAwards["personalstats"].get("defendsstalemated"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [639]:
                    # 639 {'name': 'Double Dragon', 'description': 'Assist in a single attack', 'type': 8, 'circulation': 5413, 'rarity': 'Rare', 'awardType': 'Honor'}
                    type = "Assists"
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    awards[type]["h_" + k] = vp
                elif int(k) in [490]:
                    # 490 {'name': 'Sidekick', 'description': 'Assist in 250 attacks', 'type': 8, 'circulation': 59, 'rarity': 'Extremely Rare', 'awardType': 'Honor'}
                    type = "Assists"
                    vp["goal"] = int(v["description"].split(" ")[2].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attacksassisted"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [253, 255, 257, 475, 476]:
                    # 253 {'name': 'Chainer 1', 'description': 'Participate in a 10 length chain', 'type': 8, 'circulation': 39418, 'rarity': 'Common', 'awardType': 'Honor'}
                    type = "Chains"
                    vp["goal"] = int(v["description"].split(" ")[3].replace(",", ""))
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    awards[type]["h_" + k] = vp
                elif int(k) in [256, 477, 478]:
                    # 256 {'name': 'Carnage', 'description': 'Make a single hit that earns your faction 10 or more respect', 'type': 8, 'circulation': 19716, 'rarity': 'Uncommon', 'awardType': 'Honor'}
                    type = "Respects"
                    vp["goal"] = int(v["description"].split(" ")[8].replace(",", ""))
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    awards[type]["h_" + k] = vp
                elif int(k) in [517]:
                    # 517 {'name': 'Pressure Point', 'description': 'Achieve 100 one hit kills', 'type': 8, 'circulation': 13351, 'rarity': 'Uncommon', 'awardType': 'Honor'}
                    type = "Miscellaneous"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("onehitkills"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [601]:
                    # 601 {'name': 'Fury', 'description': 'Achieve 10,000 hits', 'type': 8, 'circulation': 8172, 'rarity': 'Limited', 'awardType': 'Honor'}
                    type = "Miscellaneous"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attackhits"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                else:
                    print(k, v)

        for k, v in allAwards["medals"].items():
            if v["type"] == "ATK":
                vp = v
                vp["awardType"] = "Medal"

                if int(k) in [174, 175, 176, 177, 178]:
                    # 174 {'name': 'Anti Social', 'description': 'Win 50 attacks', 'type': 'ATK'}
                    type = "Wins"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attackswon"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["m_" + k] = vp
                elif int(k) in [179, 180, 181, 182, 183]:
                    # 179 {'name': 'Bouncer', 'description': 'Successfully defend against 50 attacks', 'type': 'ATK', 'awardType': 'Medals'}
                    type = "Defends"
                    vp["goal"] = int(v["description"].split(" ")[-2].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("defendswon"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["m_" + k] = vp
                elif int(k) in [184, 185, 186]:
                    # 184 {'name': 'Close Escape', 'description': 'Successfully escape from 50 foes', 'type': 'ATK', 'awardType': 'Medal'}
                    type = "Escapes"
                    vp["goal"] = int(v["description"].split(" ")[-2].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("yourunaway"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["m_" + k] = vp
                elif int(k) in [187, 188, 189]:
                    # 187 {'name': 'Ego Smashing', 'description': 'Have 50 enemies escape from you during an attack', 'type': 'ATK', 'awardType': 'Medal'}
                    type = "Escapes"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("theyrunaway"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["m_" + k] = vp
                elif int(k) in [190, 191, 192, 193, 194]:
                    # 190 {'name': 'Strike', 'description': 'Acquire a kill streak of 25', 'type': 'ATK', 'awardType': 'Medal'}
                    type = "Kill streak"
                    vp["goal"] = int(v["description"].split(" ")[-1].replace(",", ""))
                    # vp["current"] = None2Zero(myAwards["personalstats"].get("killstreak"))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("bestkillstreak"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["m_" + k] = vp
                elif int(k) in [195, 196, 197]:
                    # 195 {'name': 'Boom Headshot', 'description': 'Deal 500 critical hits to enemies during combat', 'type': 'ATK', 'awardType': 'Medal'}
                    type = "Critical hits"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("attackcriticalhits"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["m_" + k] = vp
                elif int(k) in [201, 202, 203]:
                    # 201 {'name': 'Hired Gun', 'description': 'Collect 25 bounties', 'type': 'ATK', 'awardType': 'Medal', 'goal': 25, 'current': 160, 'achieve': 1}
                    type = "Bounties"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("bountiescollected"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["m_" + k] = vp
                elif int(k) in [215, 216, 217, 218, 219, 220, 221, 222, 223, 224]:
                    # 215 {'name': 'Recruit', 'description': 'Earn 100 respect for your faction', 'type': 'ATK', 'awardType': 'Medal'}
                    type = "Respects"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("respectforfaction"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["m_" + k] = vp
                else:
                    print(k, v)

        awardsSummary = createAwardSummary(awards)

        out = {"awards": awards, "awardsSummary": awardsSummary}
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

        awards = dict({
            "City": dict(),
            "Medical items": dict(),
            "Miscellaneous": dict(),
            "Consume": dict()})

        for k, v in allAwards["honors"].items():
            if int(v["type"]) in [15, 16]:
                vp = v
                vp["awardType"] = "Honor"
                vp["img"] = honorId2Img(int(k))
                vp["title"] = "{} [{}]: {} ({})".format(vp["name"], k, vp["rarity"], vp["circulation"])

                if int(k) in [398, 418]:
                    # 398 {'name': 'Anaemic', 'description': 'Fill 1,000 empty blood bags', 'type': 15, 'circulation': 3823, 'rarity': 'Rare', 'awardType': 'Honor', 'goal': 1000, 'current': 0, 'achieve': 0.0}
                    type = "Medical items"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("bloodwithdrawn"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [367, 406]:
                    # 406 {'name': 'Vampire', 'description': 'Random chance upon using a blood bag', 'type': 15, 'circulation': 10562, 'rarity': 'Limited', 'awardType': 'Honor', 'achieve': 0}
                    # 367 {'name': 'Clotted', 'description': 'Suffer from an acute haemolytic reaction, or be immune to it', 'type': 15, 'circulation': 11247, 'rarity': 'Uncommon', 'awardType': 'Honor', 'achieve': 0}
                    type = "Medical items"
                    vp["goal"] = 1
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    awards[type]["h_" + k] = vp
                elif int(k) in [4]:
                    # 4 {'name': "I'm a Real Doctor", 'description': 'Steal 500 medical items', 'type': 15, 'circulation': 24992, 'rarity': 'Common', 'awardType': 'Honor', 'achieve': 0}
                    type = "Medical items"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("medstolen"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [7]:
                    # 7 {'name': 'Magical Veins', 'description': 'Use 5,000 medical items', 'type': 15, 'circulation': 4686, 'rarity': 'Rare', 'awardType': 'Honor', 'achieve': 0}
                    type = "Medical items"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("medicalitemsused"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [1]:
                    # 1 {'name': "I'm Watching You", 'description': 'Find 50 items in the city', 'type': 16, 'circulation': 26943, 'rarity': 'Common', 'awardType': 'Honor', 'achieve': 0}
                    type = "City"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("cityfinds"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [238]:
                    # 238 {'name': 'Optimist', 'description': 'Find 1,000 items in the dump', 'type': 16, 'circulation': 5850, 'rarity': 'Limited', 'awardType': 'Honor', 'achieve': 0}
                    type = "City"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("dumpfinds"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [271]:
                    # 271 {'name': 'Eco Friendly', 'description': 'Trash 5,000 items', 'type': 16, 'circulation': 14796, 'rarity': 'Uncommon', 'awardType': 'Honor', 'achieve': 0}
                    type = "City"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("itemsdumped"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [273]:
                    # 273 {'name': 'Bargain Hunter', 'description': 'Win 10 auctions', 'type': 16, 'circulation': 8415, 'rarity': 'Limited', 'awardType': 'Honor', 'achieve': 0}
                    type = "Miscellaneous"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("auctionswon"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [527]:
                    # 527 {'name': 'Worth it', 'description': 'Use a stat enhancer', 'type': 16, 'circulation': 698, 'rarity': 'Extraordinary', 'awardType': 'Honor', 'achieve': 0}
                    type = "Consume"
                    vp["goal"] = 1
                    vp["current"] = None2Zero(myAwards["personalstats"].get("statenhancersused"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [534]:
                    # 534 {'name': 'Alcoholic', 'description': 'Drink 500 bottles of alcohol', 'type': 16, 'circulation': 7842, 'rarity': 'Limited', 'awardType': 'Honor', 'achieve': 0}
                    type = "Consume"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("alcoholused"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [537]:
                    # 537 {'name': 'Diabetic', 'description': 'Eat 500 bags of candy', 'type': 16, 'circulation': 7948, 'rarity': 'Limited', 'awardType': 'Honor', 'achieve': 0}
                    type = "Consume"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("candyused"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [538]:
                    # 538 {'name': 'Sodaholic', 'description': 'Drink 500 cans of energy drink', 'type': 16, 'circulation': 898, 'rarity': 'Extraordinary', 'awardType': 'Honor', 'achieve': 0}
                    type = "Consume"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("boostersused"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [539]:
                    # 539 {'name': 'Bibliophile', 'description': 'Read 10 books', 'type': 16, 'circulation': 384, 'rarity': 'Extraordinary', 'awardType': 'Honor', 'achieve': 0}
                    type = "Consume"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("booksread"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                else:
                    print(k, v)

        for k, v in allAwards["medals"].items():
            if v["type"] == "OTR":
                vp = v
                vp["awardType"] = "Medal"

                if int(k) in [204, 205, 206]:
                    # 204 {'name': 'Watchful', 'description': 'Find 10 items in the city', 'type': 'OTR', 'awardType': 'Medal', 'goal': 10, 'current': 0, 'achieve': 0.0}
                    type = "City"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("cityfinds"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["m_" + k] = vp
                elif int(k) in [198, 199, 200]:
                    # 198 {'name': 'Pin Cushion', 'description': 'Use 500 medical items', 'type': 'OTR', 'awardType': 'Medal', 'goal': 500, 'current': 0, 'achieve': 0.0}
                    type = "Medical items"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("medicalitemsused"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["m_" + k] = vp
                # elif int(k) in [207, 208, 209]:
                #     # 207 {'name': 'Frequent Flyer', 'description': 'Travel abroad 25 times', 'type': 'OTR', 'awardType': 'Medal', 'achieve': 0}
                #     type = "Travels"
                #     vp["goal"] = int(v["description"].split(" ")[2].replace(",", ""))
                #     vp["current"] = None2Zero(myAwards["personalstats"].get("traveltimes"))
                #     vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                else:
                    print(k, v)

        awardsSummary = createAwardSummary(awards)

        out = {"awards": awards, "awardsSummary": awardsSummary}
        return render(request, 'awards.html', out)

    return render(request, 'awards.html')


def travel(request):
    if request.session.get('awards'):
        key = request.session['awards'].get('keyValue')
        allAwards = apiCall('torn', '', 'honors,medals', key)
        if 'apiError' in allAwards:
            return render(request, 'errorPage.html', allAwards)
        myAwards = apiCall('user', '', 'personalstats,medals,honors', key)
        if 'apiError' in myAwards:
            return render(request, 'errorPage.html', myAwards)

        awards = dict({
            "Destinations": dict(),
            "Time": dict()})

        for k, v in allAwards["honors"].items():
            if int(v["type"]) in [7]:
                vp = v
                vp["awardType"] = "Honor"
                vp["img"] = honorId2Img(int(k))
                vp["title"] = "{} [{}]: {} ({})".format(vp["name"], k, vp["rarity"], vp["circulation"])

                if int(k) in [11, 165]:
                    # 11 {'name': 'Mile High Club', 'description': 'Travel 100 times', 'type': 7, 'circulation': 31338, 'rarity': 'Common', 'awardType': 'Honor', 'img': 241952085, 'title': 'Mile High Club [11]: Common (31338)'}
                    # 165 {'name': 'There And Back', 'description': 'Travel 1,000 times', 'type': 7, 'circulation': 6183, 'rarity': 'Limited', 'awardType': 'Honor', 'img': 317282935, 'title': 'There And Back [165]: Limited (6183)'}
                    type = "Time"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("traveltimes"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp

                elif int(k) in [549, 567]:
                    # 549 {'name': 'Tourist', 'description': 'Spend 7 days in the air', 'type': 7, 'circulation': 16881, 'rarity': 'Uncommon', 'awardType': 'Honor', 'img': 724568067, 'title': 'Tourist [549]: Uncommon (16881)'}
                    # 567 {'name': 'Frequent Flyer', 'description': 'Spend 31 days in the air', 'type': 7, 'circulation': 9638, 'rarity': 'Limited', 'awardType': 'Honor', 'img': 891235999, 'title': 'Frequent Flyer [567]: Limited (9638)'}
                    type = "Time"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = int(None2Zero(myAwards["personalstats"].get("traveltime")) / (3600 * 24))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 272]:
                    # 130 {'name': 'Maradona', 'description': 'Travel to Argentina 50 times', 'type': 7, 'circulation': 10543, 'rarity': 'Limited', 'awardType': 'Honor', 'img': 697523940, 'title': 'Maradona [130]: Limited (10543)'}
                    type = "Destinations"
                    key = v["description"].split(" ")[2].lower()[:3] + "travel"
                    if key == "thetravel":
                        key = "lontravel"
                    vp["goal"] = int(v["description"].split(" ")[-2].replace(",", ""))
                    vp["current"] = int(None2Zero(myAwards["personalstats"].get(key)))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                else:
                    print(k, v)

        for k, v in allAwards["medals"].items():
            if v["type"] == "OTR":
                vp = v
                vp["awardType"] = "Medal"

                if int(k) in [207, 208, 209]:
                    # 207 {'name': 'Frequent Flyer', 'description': 'Travel abroad 25 times', 'type': 'OTR', 'awardType': 'Medal', 'achieve': 0}
                    type = "Time"
                    vp["goal"] = int(v["description"].split(" ")[2].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("traveltimes"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["m_" + k] = vp
                else:
                    print(k, v)

        awardsSummary = createAwardSummary(awards)

        out = {"awards": awards, "awardsSummary": awardsSummary}
        return render(request, 'awards.html', out)

    return render(request, 'awards.html')


def work(request):
    if request.session.get('awards'):
        key = request.session['awards'].get('keyValue')
        allAwards = apiCall('torn', '', 'honors,medals', key)
        if 'apiError' in allAwards:
            return render(request, 'errorPage.html', allAwards)
        myAwards = apiCall('user', '', 'workstats,personalstats,education,medals,honors', key)
        if 'apiError' in myAwards:
            return render(request, 'errorPage.html', myAwards)

        awards = dict({
            "Bachelors": dict(),
            "Courses": dict(),
            "Working stats": dict(),
            "City jobs": dict()})

        for k, v in allAwards["honors"].items():
            if int(v["type"]) in [0, 4, 15]:
                vp = v
                vp["awardType"] = "Honor"
                vp["img"] = honorId2Img(int(k))
                vp["title"] = "{} [{}]: {} ({})".format(vp["name"], k, vp["rarity"], vp["circulation"])

                if int(k) in [53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64]:
                    # 53 {'name': 'Biology Bachelor', 'description': 'Complete all classes in Biology', 'type': 4, 'circulation': 28936, 'rarity': 'Common', 'awardType': 'Honor', 'img': None, 'title': 'Biology Bachelor [53]: Common (28936)'}
                    type = "Bachelors"
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    awards[type]["h_" + k] = vp
                elif int(k) in [653]:
                    # 653 {'name': 'Smart Alec', 'description': 'Complete 10 education courses', 'type': 4, 'circulation': 150699, 'rarity': 'Very Common', 'awardType': 'Honor', 'img': 872280837, 'title': 'Smart Alec [653]: Very Common (150699)'}
                    type = "Courses"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(len(myAwards.get("education_completed")))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [4]:
                    # 4 {'name': "I'm a Real Doctor", 'description': 'Steal 500 medical items', 'type': 15, 'circulation': 24996, 'rarity': 'Common', 'awardType': 'Honor', 'img': 408554952, 'title': "I'm a Real Doctor [4]: Common (24996)"}
                    type = "City jobs"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("medstolen"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [23, 267]:
                    # 23 {'name': 'Florence Nightingale', 'description': 'Revive 500 people', 'type': 15, 'circulation': 1053, 'rarity': 'Extraordinary', 'awardType': 'Honor', 'img': None, 'title': 'Florence Nightingale [23]: Extraordinary (1053)'}
                    type = "City jobs"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("revives"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [164]:
                    # 164 {'name': 'Keen', 'description': 'Spy on people while in the army 100 times', 'type': 0, 'circulation': 2066, 'rarity': 'Extraordinary', 'awardType': 'Honor', 'img': None, 'title': 'Keen [164]: Extraordinary (2066)'}
                    type = "City jobs"
                    vp["goal"] = int(v["description"].split(" ")[-2].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("?"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [220]:
                    # 220 {'name': 'The Affronted', 'description': 'Infuriate all interviewers in starter jobs', 'type': 0, 'circulation': 4630, 'rarity': 'Rare', 'awardType': 'Honor', 'img': 384148528, 'title': 'The Affronted [220]: Rare (4630)'}
                    type = "City jobs"
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    awards[type]["h_" + k] = vp
                elif int(k) in [525, 530, 533]:
                    # 525 {'name': 'Tireless', 'description': 'Attain 100,000 endurance', 'type': 4, 'circulation': 8731, 'rarity': 'Limited', 'awardType': 'Honor', 'img': None, 'title': 'Tireless [525]: Limited (8731)'}
                    # 530 {'name': 'Talented', 'description': 'Attain 100,000 intelligence', 'type': 4, 'circulation': 11171, 'rarity': 'Uncommon', 'awardType': 'Honor', 'img': None, 'title': 'Talented [530]: Uncommon (11171)'}
                    # 533 {'name': 'Tough', 'description': 'Attain 100,000 manual labour', 'type': 4, 'circulation': 7204, 'rarity': 'Limited', 'awardType': 'Honor', 'img': None, 'title': 'Tough [533]: Limited (7204)'}
                    type = "Working stats"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    key = "_".join(v["description"].split(" ")[2:]).replace("ou", "o")
                    vp["current"] = None2Zero(myAwards.get(key))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                else:
                    print(k, v)

        awardsSummary = createAwardSummary(awards)

        out = {"awards": awards, "awardsSummary": awardsSummary}
        return render(request, 'awards.html', out)

    return render(request, 'awards.html')


def gym(request):
    if request.session.get('awards'):
        key = request.session['awards'].get('keyValue')
        allAwards = apiCall('torn', '', 'honors,medals', key)
        if 'apiError' in allAwards:
            return render(request, 'errorPage.html', allAwards)
        myAwards = apiCall('user', '', 'battlestats,medals,honors', key)
        if 'apiError' in myAwards:
            return render(request, 'errorPage.html', myAwards)

        awards = dict({
            "Memberships": dict(),
            "Defense": dict(),
            "Dexterity": dict(),
            "Speed": dict(),
            "Strength": dict(),
            "Total stats": dict()})

        for k, v in allAwards["honors"].items():
            if int(v["type"]) in [10]:
                vp = v
                vp["awardType"] = "Honor"
                vp["img"] = honorId2Img(int(k))
                vp["title"] = "{} [{}]: {} ({})".format(vp["name"], k, vp["rarity"], vp["circulation"])

                if int(k) in [240, 241, 242, 243, 297, 497, 505, 506, 635, 640, 643, 646, 686, 687, 694, 720, 723]:
                    # 240 {'name': 'Behemoth', 'description': 'Gain 1,000,000 defense', 'type': 10, 'circulation': 20913, 'rarity': 'Uncommon', 'awardType': 'Honor', 'img': 362146978, 'title': 'Behemoth [240]: Uncommon (20913)'}
                    type = "zzz".join(v["description"].split(" ")[2:]).title().replace("zzz", " ")
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    key = v["description"].split(" ")[2].lower()
                    vp["current"] = None2Zero(myAwards.get(key)).split(".")[0]
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp
                elif int(k) in [233, 234, 235]:
                    # 233 {'name': 'Bronze Belt', 'description': 'Own all lightweight gym memberships', 'type': 10, 'circulation': 61239, 'rarity': 'Common', 'awardType': 'Honor', 'img': 439667520, 'title': 'Bronze Belt [233]: Common (61239)'}
                    type = "Memberships"
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    awards[type]["h_" + k] = vp

                else:
                    print(k, v)

        awardsSummary = createAwardSummary(awards)

        out = {"awards": awards, "awardsSummary": awardsSummary}
        return render(request, 'awards.html', out)

    return render(request, 'awards.html')


def money(request):
    if request.session.get('awards'):
        key = request.session['awards'].get('keyValue')
        allAwards = apiCall('torn', '', 'honors,medals', key)
        if 'apiError' in allAwards:
            return render(request, 'errorPage.html', allAwards)
        myAwards = apiCall('user', '', 'personalstats,networth,medals,honors', key)
        if 'apiError' in myAwards:
            return render(request, 'errorPage.html', myAwards)

        awards = dict({
            "Stocks": dict(),
            "Bank": dict(),
            "Miscellaneous": dict(),
            "Networth": dict()})

        for k, v in allAwards["honors"].items():
            if int(v["type"]) in [14, 16]:
                vp = v
                vp["awardType"] = "Honor"
                vp["img"] = honorId2Img(int(k))
                vp["title"] = "{} [{}]: {} ({})".format(vp["name"], k, vp["rarity"], vp["circulation"])

                if int(k) in [546]:
                    # 546 {'name': 'Dividend', 'description': 'Receive 100 stock payouts ', 'type': 14, 'circulation': 8295, 'rarity': 'Limited', 'awardType': 'Honor', 'img': 543547927, 'title': 'Dividend [546]: Limited (8295)'}
                    type = "Stocks"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("stockpayouts"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp

                elif int(k) in [3, 19, 546]:
                    # 3 {'name': 'Moneybags', 'description': 'Achieve excellent success in the stock market', 'type': 14, 'circulation': 20747, 'rarity': 'Uncommon', 'awardType': 'Honor', 'img': 234842928, 'title': 'Moneybags [3]: Uncommon (20747)'}
                    # 19 {'name': 'Stock Analyst', 'description': 'Buy and sell shares actively in the stock market', 'type': 14, 'circulation': 2446, 'rarity': 'Rare', 'awardType': 'Honor', 'img': 890959235, 'title': 'Stock Analyst [19]: Rare (2446)'}
                    type = "Stocks"
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [10]:
                    # 10 {'name': 'Green, Green Grass', 'description': 'Make an investment in the city bank of over $1,000,000,000', 'type': 14, 'circulation': 21990, 'rarity': 'Uncommon', 'awardType': 'Honor', 'img': 927018892, 'title': 'Green, Green Grass [10]: Uncommon (21990)'}
                    type = "Bank"
                    vp["goal"] = int(v["description"].split(" ")[-1].replace(",", "").replace("$", ""))
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["current"] = None2Zero(myAwards["networth"].get("bank"))
                    vp["head"] = "$"
                    awards[type]["h_" + k] = vp

                elif int(k) in [12]:
                    # 12 {'name': 'Pocket Money', 'description': 'Make an investment in the city bank', 'type': 14, 'circulation': 182442, 'rarity': 'Very Common', 'awardType': 'Honor', 'img': 533285823, 'title': 'Pocket Money [12]: Very Common (182442)'}
                    type = "Bank"
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [8]:
                    # 8 {'name': 'Loan Shark', 'description': 'Achieve a high credit score with Duke', 'type': 14, 'circulation': 10499, 'rarity': 'Limited', 'awardType': 'Honor', 'img': 602403620, 'title': 'Loan Shark [8]: Limited (10499)'}
                    type = "Miscellaneous"
                    vp["goal"] = 1
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["current"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    awards[type]["h_" + k] = vp

                elif int(k) in [239]:
                    # 239 {'name': 'Middleman', 'description': 'Have 100 customers buy from your bazaar', 'type': 16, 'circulation': 27683, 'rarity': 'Common', 'awardType': 'Honor', 'achieve': 0}
                    type = "Miscellaneous"
                    vp["goal"] = int(v["description"].split(" ")[1].replace(",", ""))
                    vp["current"] = None2Zero(myAwards["personalstats"].get("bazaarcustomers"))
                    vp["achieve"] = min(1, float(vp["current"]) / float(vp["goal"]))
                    awards[type]["h_" + k] = vp

                else:
                    print(k, v)

        for k, v in allAwards["medals"].items():
            if v["type"] == "NTW":
                vp = v
                vp["awardType"] = "Medal"

                if int(k) in [89, 90, 91, 92, 93, 94, 95, 96, 236, 237, 238, 239, 240, 241]:
                    # 89 {'name': 'Apprentice', 'description': 'Have a recorded networth value of $100,000 for at least 3 days', 'type': 'NTW', 'awardType': 'Medal'}
                    type = "Networth"
                    vp["goal"] = int(v["description"].split(" ")[6].replace(",", "").replace("$", ""))
                    vp["current"] = None2Zero(myAwards["networth"].get("total"))
                    vp["achieve"] = 1 if int(k) in myAwards["medals_awarded"] else min(1, float(vp["current"]) / float(vp["goal"]))
                    vp["head"] = "$"
                    awards[type]["m_" + k] = vp

                else:
                    print(k, v)

        awardsSummary = createAwardSummary(awards)

        out = {"awards": awards, "awardsSummary": awardsSummary}
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
