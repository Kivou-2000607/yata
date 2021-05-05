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
from setup.models import *
from yata.handy import *


def prune(request):
    try:
        if request.session.get('player'):
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()

            nPlayers = PlayerData.objects.first()

            context = {"player": player, "nTotal": nPlayers.nTotal, "nInact": nPlayers.nInact, "nValid": nPlayers.nValid, "nInval": nPlayers.nInval, "nPrune": nPlayers.nPrune, "view": {"prune": True}}
            return render(request, "setup.html", context)
        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


# def number(request):
#     try:
#         lastActions = dict({})
#         nPlayers = PlayerData.objects.first()
#         lastActions["hour"] = nPlayers.nHour
#         lastActions["day"] = nPlayers.nDay
#         lastActions["month"] = nPlayers.nMonth
#         lastActions["total"] = nPlayers.nTotal
#         lastActions["string"] = "{} / {} / {} / {}".format(lastActions["total"], lastActions["month"], lastActions["day"], lastActions["hour"])
#         return HttpResponse(json.dumps(lastActions), content_type="application/json")
#     except BaseException:
#         return returnError()


def analytics(request):
    try:
        player = getPlayer(request.session.get("player", {}).get("tId", -1))

        # html reports
        html_reports = {"web": [], "api v1": [], "old loot": []}
        for report_file in sorted(glob.glob(settings.MEDIA_ROOT + '/analytics/*.html'), reverse=True):
            # get file name
            report_url = f'{settings.MEDIA_URL}analytics/{report_file.split("/")[-1]}'

            # get name and type
            report_section, report_period = [r.replace('-', ' ') for r in report_file.replace('.html', '').split('/')[-1].split('_')]
            html_reports[report_section].append({"url": report_url, "section": report_section, "period": report_period})

        # WEB day by day and hour / hour graph
        analytics_db = Analytics.objects.filter(report_section="web").filter(report_period__regex=r'\d{4}\s\d{2}\s\d{2}').order_by("report_timestamp")
        analytics = {"web": {"d": [], "h": [], 'r': [], "last_update": 0}}
        for a in analytics_db:

            # add last week hourly
            if a.report_timestamp > tsnow() - 3600 * 24 * 7:
                for i, ah in enumerate(json.loads(a.visitors_data.replace("'", "\""))[::-1]):
                    d = {"date": timestampToDate(a.report_timestamp + i * 3600), "unique_visitors": ah["visitors"]["count"], "total_requests": ah["hits"]["count"]}
                    analytics["web"]["h"].append(d)

                # add requests
                analytics["web"]["r"].append([a.report_period, [r for r in json.loads(a.requests_data.replace("'", "\""))[:5]]])

            # add all daily
            d = {"date": timestampToDate(a.report_timestamp), "unique_visitors": a.unique_visitors, "total_requests": a.total_requests, "failed_requests": a.failed_requests}
            analytics["web"]["d"].append(d)
            analytics["web"]["last_update"] = max(a.last_update, analytics["web"]["last_update"])


        # API day by day and hour / hour graph
        analytics_db = Analytics.objects.filter(report_section="api v1").filter(report_period__regex=r'\d{4}\s\d{2}\s\d{2}').order_by("report_timestamp")
        analytics["api"] = {"d": [], "h": [], "r": [], "last_update": 0}
        for a in analytics_db:

            # add last week hourly
            if a.report_timestamp > tsnow() - 3600 * 24 * 7:
                for i, ah in enumerate(json.loads(a.visitors_data.replace("'", "\""))[::-1]):
                    d = {"date": timestampToDate(a.report_timestamp + i * 3600), "unique_visitors": ah["visitors"]["count"], "total_requests": ah["hits"]["count"]}
                    analytics["api"]["h"].append(d)

                # add requests
                analytics["api"]["r"].append([a.report_period, [r for r in json.loads(a.requests_data.replace("'", "\""))[:5]]])

            # add all daily
            d = {"date": timestampToDate(a.report_timestamp), "unique_visitors": a.unique_visitors, "total_requests": a.total_requests, "failed_requests": a.failed_requests}
            analytics["api"]["d"].append(d)
            analytics["api"]["last_update"] = max(a.last_update, analytics["api"]["last_update"])

        # revert requests
        analytics["api"]["r"] = analytics["api"]["r"][::-1]
        analytics["web"]["r"] = analytics["web"]["r"][::-1]

        # modify last timestamp for the hourly graphs (not 100% useful)
        analytics["api"]["h"][-1]["date"] = timestampToDate(tsnow())
        analytics["web"]["h"][-1]["date"] = timestampToDate(tsnow())

        context = {"html_reports": html_reports, "player": player, "analytics": analytics, "view": {"analytics": True}}
        return render(request, 'setup.html', context)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def donations(request):
    try:
        player = getPlayer(request.session.get("player", {}).get("tId", -1))

        paypal = PayPal.objects.first()
        paypal_balance = paypal.get_balance() if paypal is not None else {"balance": 0}

        droplet = Droplet.objects.first()
        if droplet is not None:
            droplet_balance = droplet.get_balance()
            droplet_specs = droplet.dropletspec_set.order_by("timestamp").last()
            balances = Balance.objects.all()
        else:
            droplet_specs = None
            droplet_balance = {"account_balance": 0}
            balances = []

        paypal_balance["balance"] = float(paypal_balance["balance"])
        droplet_balance["account_balance"] = -float(droplet_balance["account_balance"])

        step = request.GET.get("step")

        context = {"player": player, "paypal_balance": paypal_balance, "droplet_balance": droplet_balance, "droplet_specs": droplet_specs, "balances": balances, "view": {"donations": True, "step": step}}
        return render(request, 'setup.html', context)

    except Exception as e:
        return returnError(exc=e, session=request.session)
