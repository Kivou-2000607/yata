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
from django.db import connection
from django.views.decorators.csrf import csrf_exempt

from yata.handy import *
from player.models import Player
from bot.models import *
from bot.functions import saveBotsConfigs

import json


def index(request):
    try:
        if request.session.get('player'):
            tId = request.session["player"].get("tId")
        else:
            tId = -1

        player = Player.objects.filter(tId=tId).first()
        notifications = json.loads(player.notifications)

        # update discord id
        error = player.update_discord_id()

        # get guilds
        guilds = [guild for guild in DiscordApp.objects.filter(pk=2).first().guild_set.all().order_by("pk")]

        # this is just for me...
        apps = False
        if player.tId in [2000607]:
            saveBotsConfigs()
            apps = DiscordApp.objects.values()
            for app in apps:
                app["variables"] = json.loads(app["variables"])

        context = {"player": player, "apps": apps, "guilds": guilds, "notifications": notifications, "error": error, "botcat": True, "view": {"index": True}}
        return render(request, "bot.html", context)

    except Exception:
        return returnError()


def documentation(request):
    try:
        if request.session.get('player'):
            tId = request.session["player"].get("tId")
        else:
            tId = -1

        player = Player.objects.filter(tId=tId).first()

        context = {"player": player, "botcat": True, "view": {"doc": True}}
        page = 'bot/content-reload.html' if request.method == 'POST' else 'bot.html'
        return render(request, page, context)

    except Exception:
        return returnError()


def welcome(request):
    try:
        if request.session.get('player'):
            tId = request.session["player"].get("tId")
        else:
            tId = -1

        player = Player.objects.filter(tId=tId).first()
        # get guilds
        guilds = [guild for guild in DiscordApp.objects.filter(pk=2).first().guild_set.all().order_by("pk")]

        context = {"player": player, "botcat": True, "guilds": guilds, "view": {"index": True}}
        page = 'bot/content-reload.html' if request.method == 'POST' else 'bot.html'
        return render(request, page, context)

    except Exception:
        return returnError()

def host(request):
    try:
        if request.session.get('player'):
            tId = request.session["player"].get("tId")
        else:
            tId = -1

        player = Player.objects.filter(tId=tId).first()

        context = {"player": player, "botcat": True, "view": {"host": True}}
        page = 'bot/content-reload.html' if request.method == 'POST' else 'bot.html'
        return render(request, page, context)

    except Exception:
        return returnError()


def updateId(request):
    try:
        if request.session.get('player') and request.method == "POST":
            print('[view.bot.updateId] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()

            error = player.update_discord_id()

            context = {'player': player, 'error': error}
            return render(request, "bot/discord-id.html", context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


def togglePerm(request):
    try:
        if request.session.get('player') and request.method == "POST":
            print('[view.bot.togglePerm] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()

            player.botPerm = not player.botPerm
            player.save()

            context = {'player': player}
            return render(request, "bot/give-permission.html", context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


def toggleNoti(request):
    try:
        if request.session.get('player') and request.method == "POST":
            print('[view.bot.toggleNoti] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()

            type = request.POST["type"]
            notifications = json.loads(player.notifications)
            if type in notifications:
                del notifications[type]
            else:
                notifications[type] = dict({})

            player.activateNotifications = bool(len(notifications))
            player.notifications = json.dumps(notifications)
            player.save()

            context = {'player': player, "type": type, 'notifications': notifications}
            return render(request, "bot/commands-api-notifications.html".format(type), context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()


@csrf_exempt
def secret(request):
    if request.method == 'POST':
        try:
            from Crypto.Hash import SHA256

            HTTP_SECRET = request.META.get("HTTP_SECRET")
            HTTP_UID = int(request.META.get("HTTP_UID"))
            HTTP_CHECK = request.META.get("HTTP_CHECK")

            i = 0
            for secret in Chat.objects.all():

                hash = SHA256.new()
                hash.update(secret.check.encode('utf-8'))

                if hash.hexdigest() != HTTP_CHECK:
                    print("{} {} not checked".format(secret.uid, secret.name))
                else:
                    i += 1
                    secret.update = tsnow()
                    secret.uid = HTTP_UID
                    secret.secret = HTTP_SECRET
                    secret.save()

            t = 1
            m = "{} secret(s) imported thanks. Chats will live!".format(i)
            return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")

        except BaseException as e:
            t = 0
            m = "Server error... YATA's been poorly coded: {}".format(e)
            return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")

    else:
        return returnError(type=403, msg="You need to post. Don\'t try to be a smart ass.")
