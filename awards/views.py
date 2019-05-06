from django.shortcuts import render
from django.core.exceptions import PermissionDenied

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
        key = player.key

        error = False
        tornAwards = apiCall('torn', '', 'honors,medals', key)
        if 'apiError' in tornAwards:
            error = tornAwards

        userInfo = apiCall('user', '', 'personalstats,crimes,education,battlestats,workstats,perks,networth,merits,profile,medals,honors,icons', key)
        if 'apiError' in userInfo:
            error = userInfo

        if not error:
            print("[view.awards.index] update awards")
            updatePlayerAwards(player, tornAwards, userInfo)

        context = {"player": player, "awardscat": True, "view": {"awards": True}}
        for k, v in json.loads(player.awardsJson).items():
            context[k] = v
        if error:
            context.update(error)
        return render(request, "awards.html", context)

    else:
        raise PermissionDenied("You might want to log in.")


def list(request, type):
    if request.session.get('player'):
        print('[view.awards.list] get player id from session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        awardsJson = json.loads(player.awardsJson)
        print('[view.awards.list] award type: {}'.format(type))

        tornAwards = awardsJson.get('tornAwards')
        userInfo = awardsJson.get('userInfo')
        summaryByType = awardsJson.get('summaryByType')
        popTotal = awardsJson.get('popTotal')

        if type in AWARDS_CAT:
            awards, awardsSummary = createAwards(tornAwards, userInfo, type)
            context = {"player": player, "view": {"awards": True}, "awardscat": True, "awards": awards, "awardsSummary": awardsSummary, "summaryByType": summaryByType, "popTotal": popTotal}
            page = 'awards/list.html' if request.method == 'POST' else "awards.html"
            return render(request, page, context)

        elif type == "all":
            awards = awardsJson.get('awards')
            context = {"player": player, "view": {"awards": True}, "awardscat": True, "awards": awards, "summaryByType": summaryByType, "popTotal": popTotal}
            page = 'awards/content-reload.html' if request.method == 'POST' else "awards.html"
            return render(request, page, context)

        elif type == "hof":
            hof = dict({})
            for p in Player.objects.exclude(awardsInfo="N/A").all().order_by('-awardsInfo'):
                hof.update({p: {"score": float(p.awardsInfo),
                                "nAwarded": json.loads(p.awardsJson)["summaryByType"]["AllHonors"]["nAwarded"],
                                "nAwards": json.loads(p.awardsJson)["summaryByType"]["AllHonors"]["nAwards"],
                                }})

            context = {"player": player, "view": {"hof": True}, "awardscat": True, "hof": hof, "summaryByType": summaryByType}
            page = 'awards/content-reload.html' if request.method == 'POST' else "awards.html"
            return render(request, page, context)

    else:
        raise PermissionDenied("You might want to log in.")
