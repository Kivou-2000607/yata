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
from player.models import PlayerData
from player.models import News
from yata.handy import returnError


def readNews(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            news = News.objects.last()
            news.player.add(player)

            return HttpResponse("{} marked as read".format(news.type))
        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


def prune(request):
    try:
        if request.session.get('player'):
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()

            nPlayers = PlayerData.objects.first()

            context = {"player": player, "nTotal": nPlayers.nTotal, "nInact": nPlayers.nInact, "nValid": nPlayers.nValid, "nInval": nPlayers.nInval, "nPrune": nPlayers.nPrune}
            return render(request, "player.html", context)
        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


def number(request):
    try:
        lastActions = dict({})
        nPlayers = PlayerData.objects.first()
        lastActions["hour"] = nPlayers.nHour
        lastActions["day"] = nPlayers.nDay
        lastActions["month"] = nPlayers.nMonth
        lastActions["total"] = nPlayers.nTotal
        lastActions["string"] = "{} / {} / {} / {}".format(lastActions["total"], lastActions["month"], lastActions["day"], lastActions["hour"])
        return HttpResponse(json.dumps(lastActions), content_type="application/json")
    except BaseException:
        return returnError()
