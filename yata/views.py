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
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.conf import settings

import json
import os
import traceback

from player.models import *
from player.functions import updatePlayer
from chain.models import Faction
from yata.handy import *


def index(request):
    try:
        allNews = News.objects.all().order_by("-date")
        allDonations = Donation.objects.all().order_by("-pk")
        if request.session.get('player'):
            print('[view.yata.index] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()

            # shouldn't happen
            if player is None:
                del request.session['player']
                context = {'allNews': allNews, 'allDonations': allDonations}

            player.lastActionTS = int(timezone.now().timestamp())
            player.active = True
            player.save()
            context = {"player": player, 'allNews': allNews, 'allDonations': allDonations}
        else:
            context = {'allNews': allNews, 'allDonations': allDonations}

        return render(request, 'yata.html', context)

    except Exception:
        return returnError()


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

    except Exception:
        return returnError()


def logout(request):
    try:
        if request.session.get('player'):
            print('[view.yata.logout] delete session')
            del request.session['player']
        return HttpResponseRedirect(reverse('index'))

    except Exception:
        return returnError()


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

    except Exception:
        return returnError()


def analytics(request):
    try:
        fold = "analytics"
        ls = sorted(os.listdir("{}/{}".format(settings.STATIC_ROOT, fold)))
        context = {"reports": ls, 'view': {'analytics': True}}
        return render(request, 'yata.html', context)
    except BaseException:
        return returnError()
