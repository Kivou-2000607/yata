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
        key = player.key
        # key = ""

        error = False
        allAwards = apiCall('torn', '', 'honors,medals', key)
        if 'apiError' in allAwards:
            error = allAwards
            # return render(request, 'errorPage.html', allAwards)

        myAwards = apiCall('user', '', 'personalstats,crimes,education,battlestats,workstats,perks,networth,merits,profile,medals,honors,icons', key)
        if 'apiError' in myAwards:
            error = myAwards
            # return render(request, 'errorPage.html', myAwards)


        if not error:
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

            print("[view.awards.index] awards in database")
            awardsJson = {"allAwards": allAwards,
                          "myAwards": myAwards,
                          "awards": awards,
                          "summaryByType": dict({k: v for k, v in sorted(summaryByType.items(), key=lambda x: x[1]['nAwarded'], reverse=True)})
                          }

            player.awardsJson = json.dumps(awardsJson)
            popTotal = 0
            popPerso = 0
            for k, v in allAwards["honors"].items():
                circulation = v.get("circulation")
                if circulation is not None:
                    if circulation > 30:
                        popTotal += 1./float(circulation)
                        achieve = v.get("achieve")
                        if achieve is not None:
                            if int(achieve) == 1:
                                popPerso += 1./float(circulation)

            player.awardsInfo = "{}% honor rarity score".format(int(popPerso/popTotal*100))
            player.awardsUpda = int(timezone.now().timestamp())
            player.lastUpdateTS = int(timezone.now().timestamp())
            player.save()
            print("[view.awards.index] awards done")

        else:
            print("[view.awards.index] api error {}".format(error))
            context["apiError"] = error["apiError"]

        for k, v in json.loads(player.awardsJson).items():
            context[k] = v

        return render(request, "awards.html", context)

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
