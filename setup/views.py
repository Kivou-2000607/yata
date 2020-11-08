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
from django.conf import settings

import json
import re
import glob

from player.models import Player
from player.models import PlayerData
from setup.models import Analytics
from yata.handy import *

def prune(request):
    try:
        if request.session.get('player'):
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()

            nPlayers = PlayerData.objects.first()

            context = {"player": player, "nTotal": nPlayers.nTotal, "nInact": nPlayers.nInact, "nValid": nPlayers.nValid, "nInval": nPlayers.nInval, "nPrune": nPlayers.nPrune, "view": {"prune": True}}
            return render(request, "yata.html", context)
        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


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


def analytics(request):
    try:
        player = getPlayer(request.session.get("player", {}).get("tId", -1))

        # html reports
        html_reports = {}
        for report_file in sorted(glob.glob(settings.MEDIA_ROOT + '/analytics/*.html')):
            # get file name
            report_url = f'{settings.MEDIA_URL}analytics/{report_file.split("/")[-1]}'

            # get name and type
            report_section, report_period = [r.replace('-', ' ') for r in report_file.replace('.html', '').split('/')[-1].split('_')]

            if report_section in html_reports:
                html_reports[report_section].append({"url": report_url, "section": report_section, "period": report_period})
            else:
                html_reports[report_section] = [{"url": report_url, "section": report_section, "period": report_period}]

        # day by day graph
        web_analytics = Analytics.objects.filter(report_section="web").filter(report_period__regex=r'\d{4}\s\d{2}\s\d{2}').order_by("report_timestamp")
        api_analytics = Analytics.objects.filter(report_section="api v1").filter(report_period__regex=r'\d{4}\s\d{2}\s\d{2}').order_by("report_timestamp")
        print(api_analytics)
        context = {"html_reports": html_reports, "player": player, "web_analytics": web_analytics, "api_analytics": api_analytics, "view": {"analytics": True}}
        return render(request, 'analytics.html', context)

    except Exception as e:
        return returnError(exc=e, session=request.session)

