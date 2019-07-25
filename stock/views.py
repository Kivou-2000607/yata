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
from django.utils import timezone
from django.conf import settings

from player.models import Player
from stock.models import Stock

from yata.handy import apiCall
from yata.handy import returnError


def index(request):
    try:
        if request.session.get('player'):
            print('[view.stock.index] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            key = player.key

            stocks = Stock.objects.all().order_by("tId")

            context = {'player': player, 'stocks': stocks, 'stockcat': True, 'view': {'list': True}}
            return render(request, 'stock.html', context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


def list(request):
    try:
        if request.session.get('player'):
            print('[view.stock.list] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            key = player.key

            stocks = apiCall("torn", "", "stocks,timestamp", key=key)
            for k, v in stocks["stocks"].items():
                stock = Stock.objects.filter(tId=int(k)).first()
                if stock is None:
                    stock = Stock.create(k, v, stocks["timestamp"])
                else:
                    stock.update(k, v, stocks["timestamp"])
                stock.save()

            stocks = Stock.objects.all().order_by("tId")

            context = {'player': player, 'stocks': stocks, 'stockcat': True, 'view': {'list': True}}
            page = 'stock/content-reload.html' if request.method == 'POST' else 'stock.html'
            return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()
