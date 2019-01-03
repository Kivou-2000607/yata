from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone

import json
from yata.handy import apiCall


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
                    vp["current"] = myAwards["criminalrecord"][crimeBridgeApp2API[ctype]]
                    vp["achieve"] = min(1, float(vp["current"])/float(n))
                    crimes[ctype]["h_"+k] = vp
                elif int(k) in [6]  :
                    ctype = "Other"
                    vp["current"] = myAwards["criminalrecord"][crimeBridgeApp2API[ctype]]
                    vp["achieve"] = min(1, float(vp["current"])/float(n))
                    crimes[ctype]["h_"+k] = vp
                elif int(k) in [24]  :
                    ctype = "Fraud crimes"
                    vp["current"] = myAwards["criminalrecord"][crimeBridgeApp2API[ctype]]
                    vp["achieve"] = min(1, float(vp["current"])/float(n))
                    crimes[ctype]["h_"+k] = vp
                elif int(k) in [152]  :
                    ctype = "Illegal products"
                    vp["current"] = myAwards["criminalrecord"][crimeBridgeApp2API[ctype]]
                    vp["achieve"] = min(1, float(vp["current"])/float(n))
                    crimes[ctype]["h_"+k] = vp
                elif int(k) in [153]  :
                    ctype = "Drug deals"
                    vp["current"] = myAwards["criminalrecord"][crimeBridgeApp2API[ctype]]
                    vp["achieve"] = min(1, float(vp["current"])/float(n))
                    crimes[ctype]["h_"+k] = vp
                elif int(k) in [155, 161]  :
                    ctype = "Computer crimes"
                    vp["current"] = myAwards["criminalrecord"][crimeBridgeApp2API[ctype]]
                    vp["achieve"] = min(1, float(vp["current"])/float(n))
                    crimes[ctype]["h_"+k] = vp
                elif int(k) in [159]  :
                    ctype = "Murder"
                    vp["current"] = myAwards["criminalrecord"][crimeBridgeApp2API[ctype]]
                    vp["achieve"] = min(1, float(vp["current"])/float(n))
                    crimes[ctype]["h_"+k] = vp
                elif int(k) in [160]  :
                    ctype = "Auto theft"
                    vp["current"] = myAwards["criminalrecord"][crimeBridgeApp2API[ctype]]
                    vp["achieve"] = min(1, float(vp["current"])/float(n))
                    crimes[ctype]["h_"+k] = vp
                elif int(k) in [251]  :
                    ctype = "Total"
                    vp["current"] = myAwards["criminalrecord"][crimeBridgeApp2API[ctype]]
                    vp["achieve"] = min(1, float(vp["current"])/float(n))
                    crimes[ctype]["h_"+k] = vp
                elif int(k) in [552]  :
                    ctype = "Organised crimes"
                    vp["achieve"] = 1 if int(k) in myAwards["honors_awarded"] else 0
                    vp["current"] = myAwards["personalstats"].get("organisedcrimes")
                    crimes[ctype]["h_"+k] = vp

        for k, v in allAwards["medals"].items():
            if v["type"] == "CRM":
                print(k, v)
                ctype = crimeBridgeMedal2App[" ".join(v["description"].split(" ")[2:-1])]
                n = int(v["description"].split(" ")[1].replace(",", ""))
                vp = v
                vp["goal"] = n
                vp["current"] = myAwards["criminalrecord"][crimeBridgeApp2API[ctype]]
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
                    vp["current"] = 0 if myAwards["personalstats"].get(key) is None else myAwards["personalstats"].get(key)
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
