from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect

import json
from yata.handy import apiCall
from yata.handy import None2Zero
from yata.handy import honorId2Img
from yata.handy import createAwards
from yata.handy import createAwardsSummary


def index(request):
    return render(request, 'awards.html')

def all(request):
    if request.session.get('awards'):
        allAwards = request.session['awards'].get('allAwards')
        myAwards = request.session['awards'].get('myAwards')

        awards = dict()
        for type in ["crimes", "drugs", "attacks", "faction", "items", "travel", "work", "gym", "money", "competitions", "commitment", "miscellaneous"]:
            awardsTmp, tmp2 = createAwards(allAwards, myAwards, type)
            # for k, v in awardsTmp.items():
            #     if k in awardsTmp:
            #         print(k, v)
            awards.update(awardsTmp)


        out = {"awards": awards}
        return render(request, 'awards.html', out)

    return render(request, 'awards.html')

def crimes(request):
    if request.session.get('awards'):
        allAwards = request.session['awards'].get('allAwards')
        myAwards = request.session['awards'].get('myAwards')
        awards, awardsSummary = createAwards(allAwards, myAwards, "crimes")
        out = {"awards": awards, "awardsSummary": awardsSummary}
        return render(request, 'awards.html', out)

    return render(request, 'awards.html')


def drugs(request):
    if request.session.get('awards'):
        allAwards = request.session['awards'].get('allAwards')
        myAwards = request.session['awards'].get('myAwards')
        awards, awardsSummary = createAwards(allAwards, myAwards, "drugs")
        out = {"awards": awards, "awardsSummary": awardsSummary}
        return render(request, 'awards.html', out)

    return render(request, 'awards.html')


def attacks(request):
    if request.session.get('awards'):
        allAwards = request.session['awards'].get('allAwards')
        myAwards = request.session['awards'].get('myAwards')
        myAwards = request.session['awards'].get('myAwards')
        awards, awardsSummary = createAwards(allAwards, myAwards, "attacks")
        out = {"awards": awards, "awardsSummary": awardsSummary}
        return render(request, 'awards.html', out)

    return render(request, 'awards.html')


def faction(request):
    if request.session.get('awards'):
        allAwards = request.session['awards'].get('allAwards')
        myAwards = request.session['awards'].get('myAwards')
        awards, awardsSummary = createAwards(allAwards, myAwards, "faction")
        out = {"awards": awards, "awardsSummary": awardsSummary}
        return render(request, 'awards.html', out)

    return render(request, 'awards.html')


def items(request):
    if request.session.get('awards'):
        allAwards = request.session['awards'].get('allAwards')
        myAwards = request.session['awards'].get('myAwards')
        awards, awardsSummary = createAwards(allAwards, myAwards, "items")
        out = {"awards": awards, "awardsSummary": awardsSummary}
        return render(request, 'awards.html', out)

    return render(request, 'awards.html')


def travel(request):
    if request.session.get('awards'):
        allAwards = request.session['awards'].get('allAwards')
        myAwards = request.session['awards'].get('myAwards')
        awards, awardsSummary = createAwards(allAwards, myAwards, "travel")
        out = {"awards": awards, "awardsSummary": awardsSummary}
        return render(request, 'awards.html', out)

    return render(request, 'awards.html')


def work(request):
    if request.session.get('awards'):
        allAwards = request.session['awards'].get('allAwards')
        myAwards = request.session['awards'].get('myAwards')
        awards, awardsSummary = createAwards(allAwards, myAwards, "work")
        out = {"awards": awards, "awardsSummary": awardsSummary}
        return render(request, 'awards.html', out)

    return render(request, 'awards.html')


def gym(request):
    if request.session.get('awards'):
        allAwards = request.session['awards'].get('allAwards')
        myAwards = request.session['awards'].get('myAwards')
        awards, awardsSummary = createAwards(allAwards, myAwards, "gym")
        out = {"awards": awards, "awardsSummary": awardsSummary}
        return render(request, 'awards.html', out)

    return render(request, 'awards.html')


def money(request):
    if request.session.get('awards'):
        allAwards = request.session['awards'].get('allAwards')
        myAwards = request.session['awards'].get('myAwards')
        awards, awardsSummary = createAwards(allAwards, myAwards, "money")
        out = {"awards": awards, "awardsSummary": awardsSummary}
        return render(request, 'awards.html', out)

    return render(request, 'awards.html')


def competitions(request):
    if request.session.get('awards'):
        allAwards = request.session['awards'].get('allAwards')
        myAwards = request.session['awards'].get('myAwards')
        awards, awardsSummary = createAwards(allAwards, myAwards, "competitions")
        out = {"awards": awards, "awardsSummary": awardsSummary}
        return render(request, 'awards.html', out)

    return render(request, 'awards.html')


def miscellaneous(request):
    if request.session.get('awards'):
        allAwards = request.session['awards'].get('allAwards')
        myAwards = request.session['awards'].get('myAwards')
        awards, awardsSummary = createAwards(allAwards, myAwards, "miscellaneous")
        out = {"awards": awards, "awardsSummary": awardsSummary}
        return render(request, 'awards.html', out)

    return render(request, 'awards.html')


def commitment(request):
    if request.session.get('awards'):
        allAwards = request.session['awards'].get('allAwards')
        myAwards = request.session['awards'].get('myAwards')
        awards, awardsSummary = createAwards(allAwards, myAwards, "commitment")
        out = {"awards": awards, "awardsSummary": awardsSummary}
        return render(request, 'awards.html', out)
    else:
        return render(request, 'awards.html')


# UPDATE ON THE FLY
def updateKey(request):
    print('[updateKey] in')
    if request.method == 'POST':
        p = request.POST
        user = apiCall('user', '', 'profile', p.get('keyValue'))
        if 'apiError' in user:
            return render(request, 'errorPage.html', user)
        allAwards = apiCall('torn', '', 'honors,medals', p.get('keyValue'))
        if 'apiError' in allAwards:
            return render(request, 'errorPage.html', allAwards)
        myAwards = apiCall('user', '', 'personalstats,crimes,education,battlestats,workstats,perks,networth,merits,profile,medals,honors', p.get('keyValue'))
        if 'apiError' in myAwards:
            return render(request, 'errorPage.html', myAwards)

        request.session['awards'] = {'keyValue': p['keyValue'],
                                     'name': user['name'],
                                     'playerId': user['player_id'],
                                     'allAwards': allAwards,
                                     'myAwards': myAwards,
                                     }

        check = json.loads(p.get('rememberSession'))
        if check:
            request.session.set_expiry(31536000)  # 1 year
        else:
            request.session.set_expiry(0)  # logout when close browser
        return render(request, 'awards/{}.html'.format(p['html']))

    else:
        return HttpResponse('Don\'t try to be a smart ass, you need to post.')


def updateData(request):
    print('[updateData] in')
    if request.method == 'POST':
        key = request.session['awards'].get('keyValue')

        allAwards = apiCall('torn', '', 'honors,medals', key)
        if 'apiError' in allAwards:
            return render(request, 'errorPage.html', allAwards)

        myAwards = apiCall('user', '', 'personalstats,crimes,education,battlestats,workstats,perks,networth,merits,profile,medals,honors', key)
        if 'apiError' in myAwards:
            return render(request, 'errorPage.html', myAwards)

        request.session['awards']['allAwards'] = allAwards
        request.session['awards']['myAwards'] = myAwards
        request.session.cycle_key()

        return render(request, 'awards/{}.html'.format(request.POST['html']))

    else:
        return HttpResponse('Don\'t try to be a smart ass, you need to post.')


def logout(request):
    try:
        del request.session['awards']
    except:
        pass
    return HttpResponseRedirect(reverse('awards:index'))
