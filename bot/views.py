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
from django.core.paginator import Paginator

from yata.handy import *
from player.models import Player
from bot.models import *
from bot.functions import *

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
        graphs = []
        guilds = DiscordApp.objects.filter(pk=2).first().guild_set.all().order_by("-pk")
        n = len(guilds)
        for i, g in enumerate(guilds):
            g.n = n - i
            if g.guildJoinedTime:
                graphs.append([timestampToDate(g.guildJoinedTime), n - i])
        graphs = sorted(graphs, key=lambda x: x[0])

        paginator = Paginator(guilds, 25)
        page = request.GET.get('page')
        guilds = paginator.get_page(page)

        if request.GET.get('page') is not None:
            return render(request, "bot/guilds-list.html", {"guilds": guilds})

        # this is just for me...
        apps = False
        if player.tId in [2000607]:
            saveBotsConfigs()
            deleteOldBots()
            apps = DiscordApp.objects.order_by("pk").values()
            for app in apps:
                app["variables"] = sorted(json.loads(app["variables"]).items(), key=lambda x: x[1]["admin"]["pk"])

        context = {"player": player, "apps": apps, "guilds": guilds, "graphs": graphs, "notifications": notifications, "error": error, "botcat": True, "view": {"index": True}}
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
        graphs = []
        guilds = DiscordApp.objects.filter(pk=2).first().guild_set.all().order_by("-pk")
        n = len(guilds)
        for i, g in enumerate(guilds):
            g.n = n - i
            if g.guildJoinedTime:
                graphs.append([timestampToDate(g.guildJoinedTime), n - i])
        graphs = sorted(graphs, key=lambda x: x[0])

        paginator = Paginator(guilds, 25)
        page = request.GET.get('page')
        guilds = paginator.get_page(page)

        if request.GET.get('page') is not None:
            return render(request, "bot/guilds-list.html", {"guilds": guilds})

        context = {"player": player, "botcat": True, "guilds": guilds, "graphs": graphs, "view": {"index": True}}
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

            # the check key is hashed with SHA256
            secret = request.META.get("HTTP_SECRET")
            check = request.META.get("HTTP_CHECK")
            uid = int(request.META.get("HTTP_UID"))

            print(secret, check, uid)

            rooms = []
            for chat in Chat.objects.all():

                if chat.check != check:
                    t = -1
                    m = "Wrong check key."
                    return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")

                else:
                    cred, _ = chat.credential_set.get_or_create(uid=uid)
                    if cred.secret != secret:
                        rooms.append(chat.name)
                        cred.secret = secret
                        cred.timestamp = tsnow()
                        cred.save()

                    chat.setNewestSecret()

            if len(rooms):
                t = 1
                m = "Secret imported for {}. Thanks, chats will live!".format(", ".join(rooms))
            else:
                t = 1
                m = "Secret was already up to date... All good dude!"
            return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")

        except BaseException as e:
            t = -2
            m = "Server error... YATA's been poorly coded: {}".format(e)
            return HttpResponse(json.dumps({"message": m, "type": t}), content_type="application/json")

    else:
        return returnError(type=403, msg="You need to post. Don\'t try to be a smart ass.")


def admin(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))

            context = {"player": player, "botcat": True, "view": {"admin": True}}
            return render(request, 'bot.html', context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()
