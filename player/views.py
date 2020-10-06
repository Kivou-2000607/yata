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
from django.http import HttpResponse
from django.utils import timezone

import json

from player.models import Player
from yata.handy import *

from player.forms import GymForm

# def index(request):
#     try:
#         if request.session.get('player'):
#             player = getPlayer(request.session["player"].get("tId"))
#             context = {"player": player, 'playercat': True}
#             page = "player/content-reload.html" if request.POST else "player.html"
#             return render(request, page, context)
#
#         else:
#             return returnError(type=403, msg="You might want to log in.")
#
#     except Exception as e:
#         return returnError(exc=e, session=request.session)


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

                req = apiCall("user", "", "personalstats,merits,honors,medals", key=player.getKey())

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

            req = apiCall("user", "", "personalstats", key=player.getKey())

            for key in ["personalstats"]:
                if key not in req:
                    context["apiErrorSub"] = req["apiError"] if "apiError" in req else "#blameched"
                    break

            if "apiErrorSub" not in context:
                context["personalstats"] = player.getPersonalstats(req=req["personalstats"])

            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def gym(request):
    # # if this is a POST request we need to process the form data
    # if request.method == 'POST':
    #     # create a form instance and populate it with data from the request:
    #     form = GymForm(request.POST)
    #     # check whether it's valid:
    #     if form.is_valid():
    #         # process the data in form.cleaned_data as required
    #         # ...
    #         # redirect to a new URL:
    #         return HttpResponseRedirect('/thanks/')
    #
    # # if a GET (or any other method) we'll create a blank form
    # else:
    #     form = NameForm()
    #
    # return render(request, 'name.html', {'form': form})

    try:
        player = getPlayer(request.session.get('player', {}).get("tId", -1))
        context = {"player": player, 'playercat': True, 'view': {'gym': True}}
        page = "player/content-reload.html" if request.POST else "player.html"

        # init value if logged in
        # if player.tId > 0:
        #     req = apiCall("user", "", "personalstats", key=player.getKey())
        #
        #     for key in ["personalstats"]:
        #         if key not in req:
        #             context["apiErrorSub"] = req["apiError"] if "apiError" in req else "#blameched"
        #             break
        #
        #     if "apiErrorSub" not in context:
        #         context["personalstats"] = player.getPersonalstats(req=req["personalstats"])

        # if click on train
        if request.method == 'POST':
            form = GymForm(request.POST)
            if form.is_valid():
                print("VALID")
            else:
                print("NOT VALID")
            print(form.cleaned_data)


        form = GymForm()

        context['form'] = form
        return render(request, page, context)


    except Exception as e:
        return returnError(exc=e, session=request.session)
