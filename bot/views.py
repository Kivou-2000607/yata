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

        # update discord id
        error = player.update_discord_id()

        # get guilds
        guilds = DiscordApp.objects.filter(pk=2).first().guild_set.filter(guildJoinedTime__gt=0).order_by("-pk")
        n = len(guilds)
        max_pk = 0
        for i, g in enumerate(guilds):
            g.n = n - i
        paginator = Paginator(guilds, 25)
        page = request.GET.get('page')
        guilds = paginator.get_page(page)

        if request.GET.get('page') is not None:
            return render(request, "bot/guilds-list.html", {"guilds": guilds})

        graphs = []
        for i, g in enumerate(DiscordApp.objects.filter(pk=2).first().guild_set.filter(guildJoinedTime__gt=0).order_by("guildJoinedTime")):
            graphs.append([timestampToDate(g.guildJoinedTime), g.pk])

        # this is just for me...
        apps = False
        if player.tId in [2000607]:
            saveBotsConfigs()
            deleteOldBots()
            apps = DiscordApp.objects.order_by("pk").values()
            for app in apps:
                app["variables"] = sorted(json.loads(app["variables"]).items(), key=lambda x: x[1]["admin"]["pk"])

        context = {"player": player, "apps": apps, "guilds": guilds, "graphs": graphs, "error": error, "botcat": True, "view": {"index": True}}
        return render(request, "bot.html", context)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def dashboard(request):
    try:
        if request.session.get('player'):
            player = getPlayer(request.session["player"].get("tId"))
            page = 'bot/content-reload.html' if request.method == 'POST' else 'bot.html'

            servers = player.server_set.all()

            context = {"player": player, "servers": servers, "botcat": True, "view": {"dashboard": True}}
            return render(request, page, context)

        else:
            message = "You might want to log in."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)

def dashboardOption(request):
    try:
        if request.session.get('player') and request.GET.get("prs", False):  #revive servers paginator

            player = getPlayer(request.session["player"].get("tId"))
            if str(request.GET.get("sid", 0)).isdigit():
                server = player.server_set.filter(bot__pk=request.GET.get("bid", 0), discord_id=request.GET.get("sid", 0)).first()
            else:
                return returnError(type=403, msg="No servers asked")

            if server is None:
                return returnError(type=403, msg="No servers found")

            context = {"player": player, "server": server, "config": server.get_revive(page=request.GET.get("prs")).get("revive_servers", {})}

            return render(request, 'bot/dashboard/module-revive-servers-table.html', context)

        elif request.session.get('player') and request.method == "POST":
            player = getPlayer(request.session["player"].get("tId"))
            post = request.POST
            page = None

            context = {"player": player, "force_display": post.get("typ"), "botcat": True, "view": {"dashboard": True}}
            server = player.server_set.filter(bot__pk=post.get("bid", 0), discord_id=post.get("sid", 0)).first()

            print(post)

            if server is None:
                context["error"] = "No server found..."

            elif "admin" not in json.loads(server.configuration):
                context["error"] = "No admin section found. Try an !update in the discord server..."

            elif post.get("mod") in ["rackets", "loot", "admin", "revive", "verify"]:
                module = post.get("mod")
                context["module"] = module
                context["server"] = server
                configuration_keys = {
                    "admin": ["prefix", "channels_admin", "channels_welcome"],
                    "rackets": ["channels_alerts", "roles_alerts", "channels_allowed"],
                    "loot": ["channels_alerts", "roles_alerts", "channels_allowed"],
                    "revive": ["channels_alerts", "roles_alerts", "channels_allowed", "sending", "blacklist"],
                    "verify": ["roles_verified", "channels_allowed", "channels_welcome", "factions", "other"],
                }.get(post.get("mod"), [])

                configuration = json.loads(server.configuration)
                c = configuration.get(module, {})
                if post.get("typ") == "enable":
                    configuration[module] = {k: {} for k in configuration_keys}

                elif post.get("typ") == "disable":
                    configuration.pop(module)

                elif post.get("typ") in configuration_keys:
                    type = post.get("typ")  # channels or roles
                    print("type", type)
                    id = post.get("key", 0)
                    name = post.get("val", "???")
                    if type not in c:
                        c[type] = {}
                    if id in c[type]:  # force toggle
                        c[type].pop(id)
                        if not len(c[type]):  # del if empty
                            del c[type]
                    else:
                        if type in ["sending", "blacklist"]:
                            c[type][id] = name
                        elif type in ["channels_allowed"]:
                            c[type][id] = name  # (multiple)
                        elif type in ["factions"]:
                            fid = post.get("fid", False)
                            if str(fid).isdigit():
                                if fid not in c[type]:
                                    c[type][fid] = {}
                                if id in c[type][fid]:
                                    del c[type][fid][id] # (toggle)
                                else:
                                    c[type][fid][id] = name  # (multiple)

                            if not len(c[type][fid]):  # del if empty
                                del c[type][fid]

                        elif type in ["other"]:
                            c[type][id] = 1
                            for a, b in [["weekly_check", "daily_check"], ["weekly_verify", "daily_verify"]]:
                                if id == a and b in c[type]:
                                    del c[type][b]
                                    break
                                elif id == b and a in c[type]:
                                    del c[type][a]
                                    break

                        else:
                            c[type] = {id: name}  # (single)

                    configuration[module] = c

                for k, v in configuration.items():
                    if k not in ["admin"]:
                        print(k, v)

                server.configuration = json.dumps(configuration)
                server.save()

            else:
                context["error"] = "Unexpected request"

            # redirect inlines
            if post.get("typ") in ["sending", "blacklist"] and "error" not in context:
                context["revive_server"] = {"server_name": post.get("val"), "server_id": post.get("key", 0)}
                configuration = json.loads(server.configuration)

                context["config"] = {"sending": configuration.get("revive", {}).get("sending", {}), "blacklist": configuration.get("revive", {}).get("blacklist", {})}
                return render(request, 'bot/dashboard/module-revive-server.html', context)
            else:
                page = 'bot/dashboard/modules.html' if page is None else page
                return render(request, page, context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def documentation(request):
    try:
        if request.session.get('player'):
            tId = request.session["player"].get("tId")
        else:
            tId = -1

        player = Player.objects.filter(tId=tId).first()
        notifications = json.loads(player.notifications)

        context = {"player": player, "notifications":notifications, "botcat": True, "view": {"doc": True}}
        page = 'bot/content-reload.html' if request.method == 'POST' else 'bot.html'
        return render(request, page, context)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def welcome(request):
    try:
        if request.session.get('player'):
            tId = request.session["player"].get("tId")
        else:
            tId = -1

        player = Player.objects.filter(tId=tId).first()

        # get guilds
        guilds = DiscordApp.objects.filter(pk=2).first().guild_set.filter(guildJoinedTime__gt=0).order_by("-pk")
        n = len(guilds)
        max_pk = 0
        for i, g in enumerate(guilds):
            g.n = n - i
        paginator = Paginator(guilds, 25)
        page = request.GET.get('page')
        guilds = paginator.get_page(page)

        if request.GET.get('page') is not None:
            return render(request, "bot/guilds-list.html", {"guilds": guilds})

        graphs = []
        for i, g in enumerate(DiscordApp.objects.filter(pk=2).first().guild_set.filter(guildJoinedTime__gt=0).order_by("guildJoinedTime")):
            max_pk = max(g.pk, max_pk)
            graphs.append([timestampToDate(g.guildJoinedTime), max_pk])

        context = {"player": player, "botcat": True, "guilds": guilds, "graphs": graphs, "view": {"index": True}}
        page = 'bot/content-reload.html' if request.method == 'POST' else 'bot.html'
        return render(request, page, context)

    except Exception as e:
        return returnError(exc=e, session=request.session)


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

    except Exception as e:
        return returnError(exc=e, session=request.session)


def updateId(request):
    try:
        if request.session.get('player') and request.method == "POST":
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()

            error = player.update_discord_id()

            context = {'player': player, 'error': error}
            return render(request, "bot/discord-id.html", context)

        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception as e:
        return returnError(exc=e, session=request.session)


# def togglePerm(request):
#     try:
#         if request.session.get('player') and request.method == "POST":
#             print('[view.bot.togglePerm] get player id from session')
#             tId = request.session["player"].get("tId")
#             player = Player.objects.filter(tId=tId).first()
#
#             player.botPerm = not player.botPerm
#             player.save()
#
#             context = {'player': player}
#             return render(request, "bot/give-permission.html", context)
#
#         else:
#             message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
#             return returnError(type=403, msg=message)
#
#     except Exception as e:
#         return returnError(exc=e, session=request.session)


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

    except Exception as e:
        return returnError(exc=e, session=request.session)


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

    except Exception as e:
        return returnError(exc=e, session=request.session)
