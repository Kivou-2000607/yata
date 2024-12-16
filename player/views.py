# Copyright 2019 kivou.2000607@gmail.com
# 
# This file is part of yata.
# 
#     yata is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     any later version.
# 
#     yata is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with yata. If not, see <https://www.gnu.org/licenses/>.

from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone

import json

from player.models import Player
from yata.handy import *


def merits(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            context = {"player": player, 'playercat': True, 'view': {'merits': True}}
            page = "player/content-reload.html" if request.POST else "player.html"

            # update merits
            if request.POST and "merits" in request.POST:
                merits = dict({})
                for it in json.loads(request.POST.get("merits")):
                    merits[it[0]] = [int(it[1]), int(it[2])]

                k, v = json.loads(request.POST.get("simu"))
                merits[k][0] = int(v)

                merits = player.getMerits(req=merits)

                context["merits"] = merits
                context["nMerits"] = request.POST.get("n_merits", 0)
                return render(request, "player/merits/index.html", context)

            else:

                req = apiCall("user", "", "personalstats,merits,honors,medals", kv={"cat": "other"}, key=player.getKey())

                for key in ["merits", "honors_awarded", "medals_awarded", "personalstats"]:
                    if key not in req:
                        context["apiErrorSub"] = req["apiError"] if "apiError" in req else "#blameched"
                        break

                if "apiErrorSub" not in context:
                    merits = player.getMerits(req=req["merits"])
                    context["nMerits"] = len(req.get("honors_awarded")) + len(req.get("medals_awarded")) + int(req["personalstats"].get("meritsbought", 0))
                    context["merits"] = merits

                return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def stats(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            context = {"player": player, 'playercat': True, 'view': {'stats': True}}
            page = "player/content-reload.html" if request.POST else "player.html"

            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)

