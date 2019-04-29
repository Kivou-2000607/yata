from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone

import json

from yata.handy import apiCall
from awards.functions import createAwards
from player.models import Player

AWARDS_CAT = ["crimes", "drugs", "attacks", "faction", "items", "travel", "work", "gym", "money", "competitions", "commitment", "miscellaneous"]


def index(request):
    if request.session.get('player'):
        print('[view.awards.index] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        context = {"player": player}

        print('[view.awards.index] Player.awardsInfo = {}'.format(player.awardsInfo))
        print('[view.awards.index] Player.awardsJson = {}'.format(len(json.loads(player.awardsJson))))

        if player.awardsInfo == "N/A" and not len(json.loads(player.awardsJson)):
            print("[view.awards.index] No awards found -> update")

        else:
            print("[view.awards.index] Awards found")
            for k, v in json.loads(player.awardsJson).items():
                context[k] = v

        return render(request, "awards.html", context)

    return HttpResponseRedirect(reverse('logout'))


def update(request):
    if request.session.get('player') and request.method == 'POST':
        print('[view.awards.update] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        context = {"player": player}
        key = player.key

        allAwards = apiCall('torn', '', 'honors,medals', key)
        if 'apiError' in allAwards:
            return render(request, 'errorPage.html', allAwards)

        myAwards = apiCall('user', '', 'personalstats,crimes,education,battlestats,workstats,perks,networth,merits,profile,medals,honors,icons', key)
        if 'apiError' in myAwards:
            return render(request, 'errorPage.html', myAwards)

        medals = allAwards["medals"]
        honors = allAwards["honors"]
        remove = [k for k, v in honors.items() if v["type"] == 1]
        for k in remove:
            del honors[k]
        myMedals = myAwards["medals_awarded"]
        myHonors = myAwards["honors_awarded"]

        awards = dict()
        summaryByType = dict({})
        for type in AWARDS_CAT:
            awardsTmp, awardsSummary = createAwards(allAwards, myAwards, type)
            summaryByType[type.title()] = awardsSummary["All awards"]
            awards.update(awardsTmp)

        summaryByType["AllAwards"] = {"nAwarded": len(myHonors) + len(myMedals), "nAwards": len(honors) + len(medals)}
        summaryByType["AllHonors"] = {"nAwarded": len(myHonors), "nAwards": len(honors)}
        summaryByType["AllMedals"] = {"nAwarded": len(myMedals), "nAwards": len(medals)}

        # request.session['awards']['allAwards'] = allAwards
        # request.session['awards']['myAwards'] = myAwards
        # request.session['awards']['awards'] = awards
        # request.session['awards']['summaryByType'] = dict({k: v for k, v in sorted(summaryByType.items(), key=lambda x: x[1]['nAwarded'], reverse=True)})

        print("[view.awards.update] awards in database")
        awardsJson = {"allAwards": allAwards,
                      "myAwards": myAwards,
                      "awards": awards,
                      "summaryByType": dict({k: v for k, v in sorted(summaryByType.items(), key=lambda x: x[1]['nAwarded'], reverse=True)})
                      }

        player.awardsJson = json.dumps(awardsJson)
        player.awardsInfo = "{}/{}".format(summaryByType["AllAwards"]["nAwarded"], summaryByType["AllAwards"]["nAwards"])
        player.save()
        print("[view.awards.update] awards done")


        for k, v in json.loads(player.awardsJson).items():
            context[k] = v


        # return render(request, "awards.html", context)
        # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        return HttpResponseRedirect(reverse('index'))

    return HttpResponseRedirect(reverse('logout'))


def list(request, type):
    if request.session.get('player') and request.method == 'POST':
        print('[view.awards.awards] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        awardsJson = json.loads(player.awardsJson)
        print('[view.awards.awards] award type: {}'.format(type))

        allAwards = awardsJson.get('allAwards')
        myAwards = awardsJson.get('myAwards')
        summaryByType = awardsJson.get('summaryByType')

        if type in AWARDS_CAT:
            awards, awardsSummary = createAwards(allAwards, myAwards, type)
            context = {"awards": awards, "awardsSummary": awardsSummary, "summaryByType": summaryByType}
        else:
            awards = awardsJson.get('awards')
            context = {"awards": awards, "summaryByType": summaryByType}

        return render(request, 'awards/list.html', context)

    print("[view.awards.crimes] no active session or wrong type or not post")
    return HttpResponseRedirect(reverse('logout'))
