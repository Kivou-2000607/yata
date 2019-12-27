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

from yata.handy import returnError
from yata.handy import apiCall
from player.models import Player
from bot.models import DiscordApp
from bot.functions import saveBotsConfigs

import json


def index(request):
    try:
        if request.session.get('player'):
            print('[view.bot.index] get player id from session')
            tId = request.session["player"].get("tId")
        else:
            print('[view.bot.index] anon session')
            tId = -1

        player = Player.objects.filter(tId=tId).first()
        notifications = json.loads(player.notifications)

        # update discord id
        error = player.update_discord_id()

        # get guilds
        guilds = [[guild.guildName, guild.guildId] for guild in DiscordApp.objects.filter(pk=2).first().guild_set.all()]

        # this is just for me...
        apps = False
        if player.tId in [2000607]:
            saveBotsConfigs()
            apps = DiscordApp.objects.values()
            for app in apps:
                app["variables"] = json.loads(app["variables"])

        context = {"player": player, "apps": apps, "guilds": guilds, "notifications": notifications, "error": error}
        return render(request, "bot.html", context)

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
