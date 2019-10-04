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

import json
import traceback

from player.models import Player
from player.models import News
from awards.models import Donation
from chain.models import Faction
from yata.handy import apiCall
from yata.handy import returnError


def index(request):
    try:
        allNews = News.objects.all().order_by("-date")
        allDonations = Donation.objects.all().order_by("-pk")
        if request.session.get('player'):
            print('[view.yata.index] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
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
            user = apiCall('user', '', 'profile', p.get('key'))
            if 'apiError' in user:
                print('[view.yata.login] API error: {}'.format(user))
                context = user
                return render(request, 'yata/login.html', context)

            # create/update player in the database
            player = Player.objects.filter(tId=user.get('player_id')).first()
            print('[view.yata.login] get player from database: {}'.format(player))

            if player is None:
                print('[view.yata.login] create new player')
                player = Player.objects.create(tId=int(user.get('player_id')))
            print('[view.yata.login] update player')
            player.key = p.get('key')
            player.update_info()
            player.lastActionTS = int(timezone.now().timestamp())

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

        print('[view.yata.delete] redirect to logout')
        return HttpResponseRedirect(reverse('logout'))

    except Exception:
        return returnError()


def api(request):
    try:
        lastActions = dict({})
        t = int(timezone.now().timestamp())
        lastActions["hour"] = len(Player.objects.filter(lastActionTS__gte=(t - (3600))))
        lastActions["day"] = len(Player.objects.filter(lastActionTS__gte=(t - (24 * 3600))))
        lastActions["month"] = len(Player.objects.filter(lastActionTS__gte=(t - (31 * 24 * 3600))))
        lastActions["total"] = len(Player.objects.all())
        lastActions["string"] = "{} / {} / {}".format(lastActions["total"], lastActions["month"], lastActions["day"])
        import time
        time.sleep(10)
        return HttpResponse(json.dumps(lastActions), content_type="application/json")
    except BaseException:
        return returnError()


def badges(request):
    return render(request, "yata/badges.html")
