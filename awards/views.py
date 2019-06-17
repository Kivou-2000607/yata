"""
Copyright 2019 kivou.2000607@gmail.com

This file is part of yata.

    yata is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    yata is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with yata. If not, see <https://www.gnu.org/licenses/>.
"""

from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.http import HttpResponseServerError
from django.template.loader import render_to_string

import json
import traceback

from yata.handy import apiCall
from awards.functions import createAwards
from awards.functions import updatePlayerAwards
from awards.functions import AWARDS_CAT
from player.models import Player


def index(request):
    try:
        if request.session.get('player'):
            print('[view.awards.index] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            player.save()

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
            return HttpResponseServerError(render_to_string('403.html', {'exception': "You might want to log in."}))

    except Exception:
        print("[{:%d/%b/%Y %H:%M:%S}] ERROR 500 \n{}".format(timezone.now(), traceback.format_exc()))
        return HttpResponseServerError(render_to_string('500.html', {'exception': traceback.format_exc().strip()}))


def list(request, type):
    try:
        if request.session.get('player'):
            print('[view.awards.list] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            player.save()

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
                    try:
                        hof.update({p: {"score": float(p.awardsInfo),
                                        "nAwarded": json.loads(p.awardsJson)["summaryByType"]["AllHonors"]["nAwarded"],
                                        "nAwards": json.loads(p.awardsJson)["summaryByType"]["AllHonors"]["nAwards"],
                                        }})
                    except:
                        print('[view.awards.list] error getting info on {}'.format(p))

                context = {"player": player, "view": {"hof": True}, "awardscat": True, "hof": hof, "summaryByType": summaryByType}
                page = 'awards/content-reload.html' if request.method == 'POST' else "awards.html"
                return render(request, page, context)

        else:
            return HttpResponseServerError(render_to_string('403.html', {'exception': "You might want to log in."}))

    except Exception:
        print("[{:%d/%b/%Y %H:%M:%S}] ERROR 500 \n{}".format(timezone.now(), traceback.format_exc()))
        return HttpResponseServerError(render_to_string('500.html', {'exception': traceback.format_exc().strip()}))
