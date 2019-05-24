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

from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.utils import timezone
from django.core.exceptions import PermissionDenied

import json

from player.models import Player
from chain.models import Faction
from yata.handy import apiCall


def index(request):
    if request.session.get('player'):
        print('[view.yata.index] get player id from session')
        tId = request.session["player"].get("tId")
        context = {"player": Player.objects.filter(tId=tId).first()}
    else:
        context = None

    return render(request, 'yata.html', context)


def login(request):
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
        raise PermissionDenied


def logout(request):
    try:
        print('[view.yata.logout] delete session')
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        del request.session['player']
        print('[view.yata.logout] done')
    except:
        print('[view.yata.logout] error while deleting the session')
        pass
    print('[view.yata.logout] redirect to index')
    return HttpResponseRedirect(reverse('index'))


def delete(request):
    if request.session.get('player'):
        print('[view.yata.delete] delete account')
        tId = request.session["player"].get("tId")
        factionId = player.factionId
        faction = Faction.objects.filter(tId=factionId).first()
        try:
            faction.delKey(tId)
            faction.save()
        except:
            pass
        player.delete()

    print('[view.yata.delete] redirect to logout')
    return HttpResponseRedirect(reverse('logout'))
