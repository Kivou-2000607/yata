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
from django.shortcuts import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.conf import settings
from django.core import serializers
from django.forms.models import model_to_dict
from django.core.paginator import Paginator

import json
import os
import traceback
import re

from player.models import *
from player.functions import updatePlayer
from faction.models import Faction
from yata.handy import *


def index(request):
    try:
        # allNews = News.objects.all().order_by("-date")
        allDonations = Donation.objects.all().order_by("-pk")
        if request.session.get('player'):
            print('[view.yata.index] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()

            # shouldn't happen
            if player is None:
                del request.session['player']
                # context = {'allNews': allNews, 'allDonations': allDonations}
                context = {'allDonations': allDonations}

            else:
                player.lastActionTS = int(timezone.now().timestamp())
                player.active = True
                player.save()
                # context = {"player": player, 'allNews': allNews, 'allDonations': allDonations}
                context = {"player": player, 'allDonations': allDonations}
        else:
            # context = {'allNews': allNews, 'allDonations': allDonations}
            context = {'allDonations': allDonations}

        return render(request, 'yata.html', context)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def login(request):
    try:
        print('[view.yata.login] START')

        if request.method == 'POST':
            p = request.POST
            print('[view.yata.login] API call with key: {}'.format(p.get('key')))
            try:
                user = apiCall('user', '', 'profile', p.get('key'))
                if 'apiError' in user:
                    print('[view.yata.login] API error: {}'.format(user))
                    context = user
                    return render(request, 'yata/login.html', context)
            except BaseException as e:
                context = {'apiError': e}
                return render(request, 'yata/login.html', context)

            # create/update player in the database
            player = Player.objects.filter(tId=user.get('player_id')).first()
            print('[view.yata.login] get player from database: {}'.format(player))

            if player is None:
                print('[view.yata.login] create new player')
                player = Player.objects.create(tId=int(user.get('player_id')))
            print('[view.yata.login] update player')
            player.addKey(p.get('key'))
            # player.key = p.get('key')
            player.active = True
            player.lastActionTS = tsnow()
            updatePlayer(player)
            print('[view.yata.login] save player')
            player.save()

            print('[view.yata.login] create session')
            request.session['player'] = {'tId': player.tId, 'name': str(player), 'login': True}

            check = json.loads(p.get('check'))
            if check:
                print('[view.yata.login] set session to expirate in 1 month')
                # request.session.set_expiry(31536000)  # 1 year
                request.session.set_expiry(2592000)  # 1 month
            else:
                print('[view.yata.login] set session to expirate when browser closes')
                request.session.set_expiry(0)  # logout when close browser

            context = {"player": player}
            return render(request, 'yata/login.html', context)

        # if not post
        else:
            return returnError(type=403, msg="You need to post. Don\'t try to be a smart ass.")
            # return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        return returnError(exc=e, session=request.session)


def logout(request):
    try:
        if request.session.get('player'):
            print('[view.yata.logout] delete session')
            del request.session['player']
        return HttpResponseRedirect(reverse('index'))

    except Exception as e:
        return returnError(exc=e, session=request.session)


def delete(request):
    try:
        if request.session.get('player'):
            print('[view.yata.delete] delete account')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            factionId = player.factionId
            faction = Faction.objects.filter(tId=factionId).first()
            try:
                faction.delKey(tId)
                faction.save()
            except BaseException:
                pass
            player.delete()
            del request.session['player']

        print('[view.yata.delete] redirect to logout')
        return HttpResponseRedirect(reverse('logout'))

    except Exception as e:
        return returnError(exc=e, session=request.session)


def analytics(request):
    try:
        fold = "analytics"
        ls = sorted(os.listdir("{}/{}".format(settings.STATIC_ROOT, fold)))
        context = {"reports": ls, 'view': {'analytics': True}}
        return render(request, 'yata.html', context)
    except BaseException:
        return returnError()


@csrf_exempt
def gym(request):
    if request.method == 'POST':
        print("hey")
        try:
            from yata.gyms import gyms

            body = json.loads(request.body)

            if "api" not in body:
                return JsonResponse({"message": "api not in payload", "type": -1})
            if "payload" not in body:
                return JsonResponse({"message": "api not in payload", "type": -1})

            api = body.get("api")

            for payload in body.get("payload"):

                # get direct values
                train = dict({})
                train["timestamp"] = tsnow()
                train["id_key"] = api.get("id_key", "x")
                train["time_diff"] = api.get("time_diff", 0)

                train["happy_before"] = payload.get("happy_before", 0)
                train["happy_after"] = payload.get("happy_after", 0)
                train["happy_delta"] = train["happy_after"] - train["happy_before"]

                train["energy_used"] = payload.get("energy_used", 0)

                train["stat_type"] = payload.get("stat_type", "None")

                train["stat_after"] = float(payload.get("stat_after", 0))
                train["stat_delta"] = float(payload.get("stat_gain", 0))
                train["stat_before"] = train["stat_after"] - train["stat_delta"]

                train["gym_id"] = payload.get("gym_id", 0)
                train["gym_dot"] = round(gyms.get(train["gym_id"], dict({})).get(train["stat_type"], 0))

                # faction perk
                for p in api.get("faction_perks", []):
                    reg = '\+ increases {stat} gym gains by \d{{1,3}}\%'.format(stat=train["stat_type"])
                    if re.match(reg, p.lower()) is not None:
                        bonus = p.replace("%", "").replace("+", "").strip().split(" ")[-1]
                        bonus = int(bonus) if bonus.isdigit() else -1
                        train["perks_faction"] = bonus
                        continue

                # education perks
                for p in api.get("education_perks", []):
                    print(p)
                    # specific gym
                    reg = '\+ \d{{1,3}}\% {stat} gym gains'.format(stat=train["stat_type"])
                    if re.match(reg, p.lower()) is not None:
                        bonus = p.replace("%", "").replace("+", "").strip().split(" ")[0]
                        bonus = int(bonus) if bonus.isdigit() else -1
                        train["perks_education_stat"] = bonus
                        continue

                    # all gyms
                    # reg = '\+ \d{1,3}\% gym gains'
                    # if re.match(reg, p.lower()) is not None:
                    if p == "+ 1% Gym gains":
                        bonus = p.replace("%", "").replace("+", "").strip().split(" ")[0]
                        bonus = int(bonus) if bonus.isdigit() else -1
                        train["perks_education_all"] = bonus
                        continue

                # property perks
                for p in api.get("property_perks", []):
                    # specific gym
                    reg = '\+ \d{{1,3}}\% gym gains'.format(stat=train["stat_type"])
                    if re.match(reg, p.lower()) is not None:
                        bonus = p.replace("%", "").replace("+", "").strip().split(" ")[0]
                        bonus = int(bonus) if bonus.isdigit() else -1
                        train["perks_property"] = bonus
                        continue

                # company perks
                for p in api.get("company_perks", []):
                    # all gym
                    reg = '\+ \d{{1,3}}\% gym gains'.format(stat=train["stat_type"])
                    if re.match(reg, p.lower()) is not None:
                        bonus = p.replace("%", "").replace("+", "").strip().split(" ")[0]
                        bonus = int(bonus) if bonus.isdigit() else -1
                        train["perks_company"] = bonus
                        continue

                    # specific gym
                    reg = '\+ \d{{1,3}}\% {stat} gym gains'.format(stat=train["stat_type"])
                    if re.match(reg, p.lower()) is not None:
                        bonus = p.replace("%", "").replace("+", "").strip().split(" ")[0]
                        bonus = int(bonus) if bonus.isdigit() else -1
                        train["perks_company"] = bonus
                        continue

                    # happiness
                    reg = '\+ \d{{1,3}}\% reduction of happiness loss in gym'.format(stat=train["stat_type"])
                    if re.match(reg, p.lower()) is not None:
                        bonus = p.replace("%", "").replace("+", "").strip().split(" ")[0]
                        bonus = int(bonus) if bonus.isdigit() else -1
                        train["company_perks_happy_red"] = bonus

                _ = TrainFull.objects.create(**train)

            return JsonResponse({"message": "All good dude", "type": 1})

        except BaseException as e:
            print(e)
            return JsonResponse({"message": "Server error... YATA's been poorly coded: {}".format(e), "type": -1})

    else:
        if request.GET.get("export") == "json":
            trains = []
            for train in TrainFull.objects.order_by("-timestamp", "happy_before"):
                trainDict = model_to_dict(train)
                vladar = train.vladar()
                trainDict["pk"] = trainDict.pk
                trainDict["stat_before"] = trainDict.stat_before_cap()
                trainDict["stat_after"] = trainDict.stat_after_cap()
                trainDict["vladar"] = vladar
                trainDict["vladar_error"] = abs(vladar - train.stat_delta) / max(train.stat_delta, 1)
                trains.append(trainDict)

            response = JsonResponse({"trains": trains})
            response['Content-Disposition'] = 'attachment; filename="trains.json"'
            return response

        else:
            trains = Paginator(TrainFull.objects.order_by("-timestamp", "happy_before"), 50)
            context = {"trains": trains.get_page(request.GET.get("page"))}
            return render(request, 'battle_stats.html', context)
            return returnError(type=403, msg="You need to post. Don\'t try to be a smart ass.")
