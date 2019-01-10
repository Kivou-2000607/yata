from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect

import json
from yata.handy import apiCall
from yata.handy import None2Zero
from yata.handy import honorId2Img
from yata.handy import createAwards
from yata.handy import createAwardsSummary

AWARDS_CAT = ["crimes", "drugs", "attacks", "faction", "items", "travel", "work", "gym", "money", "competitions", "commitment", "miscellaneous"]

def index(request):
    if request.session.get('awards'):
        try:
            allAwards = request.session['awards'].get('allAwards')
            myAwards = request.session['awards'].get('myAwards')
            summaryByType = request.session['awards'].get('summaryByType')
            awards = request.session['awards'].get('awards')
            out = {"awards": awards, "summaryByType": summaryByType}
            return render(request, 'awards.html', out)
        except:
            return HttpResponseRedirect(reverse('awards:logout'))

    return render(request, 'awards.html')


def crimes(request):
    if request.session.get('awards'):
        try:
            allAwards = request.session['awards'].get('allAwards')
            myAwards = request.session['awards'].get('myAwards')
            summaryByType = request.session['awards'].get('summaryByType')
            awards, awardsSummary = createAwards(allAwards, myAwards, "crimes")
            out = {"awards": awards, "awardsSummary": awardsSummary, "summaryByType": summaryByType}
            return render(request, 'awards.html', out)
        except:
            return HttpResponseRedirect(reverse('awards:logout'))

    return render(request, 'awards.html')


def drugs(request):
    if request.session.get('awards'):
        try:
            allAwards = request.session['awards'].get('allAwards')
            myAwards = request.session['awards'].get('myAwards')
            summaryByType = request.session['awards'].get('summaryByType')
            awards, awardsSummary = createAwards(allAwards, myAwards, "drugs")
            out = {"awards": awards, "awardsSummary": awardsSummary, "summaryByType": summaryByType}
            return render(request, 'awards.html', out)
        except:
            return HttpResponseRedirect(reverse('awards:logout'))

    return render(request, 'awards.html')


def attacks(request):
    if request.session.get('awards'):
        try:
            allAwards = request.session['awards'].get('allAwards')
            myAwards = request.session['awards'].get('myAwards')
            myAwards = request.session['awards'].get('myAwards')
            summaryByType = request.session['awards'].get('summaryByType')
            awards, awardsSummary = createAwards(allAwards, myAwards, "attacks")
            out = {"awards": awards, "awardsSummary": awardsSummary, "summaryByType": summaryByType}
            return render(request, 'awards.html', out)
        except:
            return HttpResponseRedirect(reverse('awards:logout'))

    return render(request, 'awards.html')


def faction(request):
    if request.session.get('awards'):
        try:
            allAwards = request.session['awards'].get('allAwards')
            myAwards = request.session['awards'].get('myAwards')
            summaryByType = request.session['awards'].get('summaryByType')
            awards, awardsSummary = createAwards(allAwards, myAwards, "faction")
            out = {"awards": awards, "awardsSummary": awardsSummary, "summaryByType": summaryByType}
            return render(request, 'awards.html', out)
        except:
            return HttpResponseRedirect(reverse('awards:logout'))

    return render(request, 'awards.html')


def items(request):
    if request.session.get('awards'):
        try:
            allAwards = request.session['awards'].get('allAwards')
            myAwards = request.session['awards'].get('myAwards')
            summaryByType = request.session['awards'].get('summaryByType')
            awards, awardsSummary = createAwards(allAwards, myAwards, "items")
            out = {"awards": awards, "awardsSummary": awardsSummary, "summaryByType": summaryByType}
            return render(request, 'awards.html', out)
        except:
            return HttpResponseRedirect(reverse('awards:logout'))

    return render(request, 'awards.html')


def travel(request):
    if request.session.get('awards'):
        try:
            allAwards = request.session['awards'].get('allAwards')
            myAwards = request.session['awards'].get('myAwards')
            summaryByType = request.session['awards'].get('summaryByType')
            awards, awardsSummary = createAwards(allAwards, myAwards, "travel")
            out = {"awards": awards, "awardsSummary": awardsSummary, "summaryByType": summaryByType}
            return render(request, 'awards.html', out)
        except:
            return HttpResponseRedirect(reverse('awards:logout'))

    return render(request, 'awards.html')


def work(request):
    if request.session.get('awards'):
        try:
            allAwards = request.session['awards'].get('allAwards')
            myAwards = request.session['awards'].get('myAwards')
            summaryByType = request.session['awards'].get('summaryByType')
            awards, awardsSummary = createAwards(allAwards, myAwards, "work")
            out = {"awards": awards, "awardsSummary": awardsSummary, "summaryByType": summaryByType}
            return render(request, 'awards.html', out)
        except:
            return HttpResponseRedirect(reverse('awards:logout'))

    return render(request, 'awards.html')


def gym(request):
    if request.session.get('awards'):
        try:
            allAwards = request.session['awards'].get('allAwards')
            myAwards = request.session['awards'].get('myAwards')
            summaryByType = request.session['awards'].get('summaryByType')
            awards, awardsSummary = createAwards(allAwards, myAwards, "gym")
            out = {"awards": awards, "awardsSummary": awardsSummary, "summaryByType": summaryByType}
            return render(request, 'awards.html', out)
        except:
            return HttpResponseRedirect(reverse('awards:logout'))

    return render(request, 'awards.html')


def money(request):
    if request.session.get('awards'):
        try:
            allAwards = request.session['awards'].get('allAwards')
            myAwards = request.session['awards'].get('myAwards')
            summaryByType = request.session['awards'].get('summaryByType')
            awards, awardsSummary = createAwards(allAwards, myAwards, "money")
            out = {"awards": awards, "awardsSummary": awardsSummary, "summaryByType": summaryByType}
            return render(request, 'awards.html', out)
        except:
            return HttpResponseRedirect(reverse('awards:logout'))

    return render(request, 'awards.html')


def competitions(request):
    if request.session.get('awards'):
        try:
            allAwards = request.session['awards'].get('allAwards')
            myAwards = request.session['awards'].get('myAwards')
            summaryByType = request.session['awards'].get('summaryByType')
            awards, awardsSummary = createAwards(allAwards, myAwards, "competitions")
            out = {"awards": awards, "awardsSummary": awardsSummary, "summaryByType": summaryByType}
            return render(request, 'awards.html', out)
        except:
            return HttpResponseRedirect(reverse('awards:logout'))

    return render(request, 'awards.html')


def miscellaneous(request):
    if request.session.get('awards'):
        try:
            allAwards = request.session['awards'].get('allAwards')
            myAwards = request.session['awards'].get('myAwards')
            summaryByType = request.session['awards'].get('summaryByType')
            awards, awardsSummary = createAwards(allAwards, myAwards, "miscellaneous")
            out = {"awards": awards, "awardsSummary": awardsSummary, "summaryByType": summaryByType}
            return render(request, 'awards.html', out)
        except:
            return HttpResponseRedirect(reverse('awards:logout'))

    return render(request, 'awards.html')


def commitment(request):
    if request.session.get('awards'):
        try:
            allAwards = request.session['awards'].get('allAwards')
            myAwards = request.session['awards'].get('myAwards')
            summaryByType = request.session['awards'].get('summaryByType')
            awards, awardsSummary = createAwards(allAwards, myAwards, "commitment")
            out = {"awards": awards, "awardsSummary": awardsSummary, "summaryByType": summaryByType}
            return render(request, 'awards.html', out)
        except:
            return HttpResponseRedirect(reverse('awards:logout'))

    return render(request, 'awards.html')


# UPDATE ON THE FLY
def updateKey(request):
    print('[updateKey] in')
    if request.method == 'POST':
        p = request.POST
        allAwards = apiCall('torn', '', 'honors,medals', p.get('keyValue'))
        if 'apiError' in allAwards:
            return render(request, 'errorPage.html', allAwards)
        myAwards = apiCall('user', '', 'personalstats,crimes,education,battlestats,workstats,perks,networth,merits,profile,medals,honors', p.get('keyValue'))
        if 'apiError' in myAwards:
            return render(request, 'errorPage.html', myAwards)

        medals = allAwards["medals"]
        honors = allAwards["honors"]
        remove = [k for k, v in honors.items() if v["type"] == 1]
        for k in remove: del honors[k]
        myMedals = myAwards["medals_awarded"]
        myHonors = myAwards["honors_awarded"]

        awards = dict()
        summaryByType = dict()
        for type in AWARDS_CAT:
            awardsTmp, awardsSummary = createAwards(allAwards, myAwards, type)
            summaryByType[type.title()] = awardsSummary["All awards"]
            awards.update(awardsTmp)

        summaryByType["AllAwards"] = { "nAwarded": len(myHonors)+len(myMedals), "nAwards": len(honors)+len(medals) }
        summaryByType["AllHonors"] = { "nAwarded": len(myHonors), "nAwards": len(honors) }
        summaryByType["AllMedals"] = { "nAwarded": len(myMedals), "nAwards": len(medals) }

        request.session['awards'] = {'keyValue': p['keyValue'],
                                     'name': myAwards['name'],
                                     'playerId': myAwards['player_id'],
                                     'allAwards': allAwards,
                                     'myAwards': myAwards,
                                     'awards': awards,
                                     'summaryByType': dict({k: v for k, v in sorted(summaryByType.items(), key=lambda x: x[1]['nAwarded'], reverse=True)}),
                                     }

        check = json.loads(p.get('rememberSession'))
        if check:
            request.session.set_expiry(31536000)  # 1 year
        else:
            request.session.set_expiry(0)  # logout when close browser
        out = {"summaryByType": summaryByType, "awardsCategories": AWARDS_CAT}
        return render(request, 'awards/{}.html'.format(p['html']), out)

    else:
        return HttpResponse('Don\'t try to be a smart ass, you need to post.')


def updateData(request):
    if request.method == 'POST':
        key = request.session['awards'].get('keyValue')

        allAwards = apiCall('torn', '', 'honors,medals', key)
        if 'apiError' in allAwards:
            return render(request, 'errorPage.html', allAwards)

        myAwards = apiCall('user', '', 'personalstats,crimes,education,battlestats,workstats,perks,networth,merits,profile,medals,honors', key)
        if 'apiError' in myAwards:
            return render(request, 'errorPage.html', myAwards)

        medals = allAwards["medals"]
        honors = allAwards["honors"]
        remove = [k for k, v in honors.items() if v["type"] == 1]
        for k in remove: del honors[k]
        myMedals = myAwards["medals_awarded"]
        myHonors = myAwards["honors_awarded"]

        awards = dict()
        summaryByType = dict({})
        for type in AWARDS_CAT:
            awardsTmp, awardsSummary = createAwards(allAwards, myAwards, type)
            summaryByType[type.title()] = awardsSummary["All awards"]
            awards.update(awardsTmp)

        summaryByType["AllAwards"] = { "nAwarded": len(myHonors)+len(myMedals), "nAwards": len(honors)+len(medals) }
        summaryByType["AllHonors"] = { "nAwarded": len(myHonors), "nAwards": len(honors) }
        summaryByType["AllMedals"] = { "nAwarded": len(myMedals), "nAwards": len(medals) }

        request.session['awards']['allAwards'] = allAwards
        request.session['awards']['myAwards'] = myAwards
        request.session['awards']['awards'] = awards
        request.session['awards']['summaryByType'] = dict({k: v for k, v in sorted(summaryByType.items(), key=lambda x: x[1]['nAwarded'], reverse=True)})
        request.session.cycle_key()

        print(current_url)

        out = {"summaryByType": summaryByType, "awardsCategories": AWARDS_CAT}
        return render(request, 'awards/{}.html'.format(request.POST['html']), out)

    else:
        return HttpResponse('Don\'t try to be a smart ass, you need to post.')


def logout(request):
    try:
        del request.session['awards']
    except:
        pass

    return HttpResponseRedirect(reverse('awards:index'))
