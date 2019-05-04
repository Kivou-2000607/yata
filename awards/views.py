from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
from django.utils import timezone

import json

from yata.handy import apiCall
from awards.functions import createAwards
from awards.functions import updatePlayerAwards
from awards.functions import AWARDS_CAT
from player.models import Player


def index(request):
    if request.session.get('player'):
        print('[view.awards.index] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        context = {"player": player}
        key = player.key
        # key = ""

        error = False
        tornAwards = apiCall('torn', '', 'honors,medals', key)
        if 'apiError' in tornAwards:
            error = tornAwards
            # return render(request, 'errorPage.html', tornAwards)

        userInfo = apiCall('user', '', 'personalstats,crimes,education,battlestats,workstats,perks,networth,merits,profile,medals,honors,icons', key)
        if 'apiError' in userInfo:
            error = userInfo
            # return render(request, 'errorPage.html', userInfo)

        if not error:
            updatePlayerAwards(player, tornAwards, userInfo)
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
        print('[view.awards.list] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        awardsJson = json.loads(player.awardsJson)
        print('[view.awards.list] award type: {}'.format(type))

        tornAwards = awardsJson.get('tornAwards')
        userInfo = awardsJson.get('userInfo')
        summaryByType = awardsJson.get('summaryByType')
        popTotal = awardsJson.get('popTotal')

        print(type)
        if type in AWARDS_CAT:
            awards, awardsSummary = createAwards(tornAwards, userInfo, type)
            context = {"awards": awards, "awardsSummary": awardsSummary, "summaryByType": summaryByType, "popTotal": popTotal }
            return render(request, 'awards/list.html', context)

        elif type == "all":
            awards = awardsJson.get('awards')
            context = {"awards": awards, "summaryByType": summaryByType, "popTotal": popTotal }
            return render(request, 'awards/list.html', context)

        elif type == "hof":
            hof = dict({})
            for p in Player.objects.exclude(awardsInfo="N/A").all().order_by('-awardsInfo'):
                hof.update({p: {"score": float(p.awardsInfo),
                                "nAwarded": json.loads(p.awardsJson)["summaryByType"]["AllHonors"]["nAwarded"],
                                "nAwards": json.loads(p.awardsJson)["summaryByType"]["AllHonors"]["nAwards"],
                                }})

            context = {"player": player, "hof": hof}
            return render(request, 'awards/hof.html', context)


    print("[view.awards.list] no active session or wrong type or not post")
    return HttpResponseRedirect(reverse('logout'))
