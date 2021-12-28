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
            # isProxy = isProxyKey(player.getKey())

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
                # user = apiCall('user', '', 'profile,bars', p.get('key'))
                user = apiCall('user', '', 'profile', p.get('key'))
                if 'apiError' in user:
                    print('[view.yata.login] API error: {}'.format(user))
                    context = user
                    context['login'] = True
                    return render(request, 'header.html', context)
                elif user['player_id'] in [1610750]:
                    context = {"apiError": "User ban for being a dickhead"}
                    context['login'] = True
                    return render(request, 'header.html', context)

            except BaseException as e:
                context = {'apiError': e, 'login': True}
                return render(request, 'header.html', context)

            # create/update player in the database
            player = Player.objects.filter(tId=user.get('player_id')).first()
            print('[view.yata.login] get player from database: {}'.format(player))

            new_player = False
            if player is None:
                print('[view.yata.login] create new player')
                player = Player.objects.create(tId=int(user.get('player_id')))
                new_player = True

            print('[view.yata.login] update player')
            player.addKey(p.get('key'))
            # player.key = p.get('key')
            player.active = True
            player.lastActionTS = tsnow()
            updatePlayer(player)
            print('[view.yata.login] save player')
            player.save()

            print('[view.yata.login] create session')
            request.session['player'] = {'tId': player.tId, 'name': str(player)}
            request.session.set_expiry(7776000)  # 3 months

            context = {"player": player, "new_player": new_player, 'login': True}
            return render(request, 'header.html', context)

        # if not post
        else:
            return returnError(type=403, msg="You need to post. Don\'t try to be a smart ass.")
            # return returnError(type=403, msg="You might want to log in.")

    except Exception as e:
        context = {'apiError': e}
        return render(request, 'header.html', context)


def logout(request):
    try:
        if request.session.get('player'):
            print('[view.yata.logout] delete session')
            del request.session['player']
        return HttpResponseRedirect(reverse('index'))

    except Exception as e:
        return returnError(exc=e, session=request.session)

def update_session(request):
    if request.method != 'POST':
        return render(request, 'yata/toggle-colors.html')

    if request.POST.get("key") == "dark":
        if "dark" not in request.session:
            request.session['dark'] = True
        else:
            request.session['dark'] = not request.session['dark']

        request.session.modified = True

    return render(request, 'yata/toggle-colors.html')


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
