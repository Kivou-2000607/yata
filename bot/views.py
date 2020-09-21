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

import json


def index(request):
    try:
        player = getPlayer(request.session.get("player", {}).get("tId", -1))

        # update discord id
        error = player.update_discord_id()

        # get servers
        servers_db = Bot.objects.filter(pk=3).first().server_set.all()
        servers = dict({})
        for s in servers_db:
            configuration = json.loads(s.configuration)
            server_admins = configuration.get("admin", {}).get("server_admins")
            joined_at = configuration.get("admin", {}).get("joined_at", 0)
            if server_admins is None or not joined_at:
                print(f'skip {s}')
                continue

            servers[str(s.discord_id)] = {"server_name": s.name, "server_id": str(s.discord_id), "joined_at": joined_at, "admins": [[v["name"], v["torn_id"]] for k, v in server_admins.items()]}

        # sort
        servers = sorted(servers.items(), key=lambda x: x[1]["joined_at"], reverse=True)
        total_servers = len(servers)

        graphs = []
        for i, (k, v) in enumerate(servers):
            v["i"] = total_servers - i
            graphs.append([timestampToDate(v.get("joined_at", 1)), total_servers - i])

        paginator = Paginator(servers, 25)
        page = request.GET.get('page')
        servers = paginator.get_page(page)

        if request.GET.get('page') is not None:
            return render(request, "bot/guilds-list.html", {"servers": servers, "total_servers": total_servers})

        context = {"player": player, "servers": servers, "total_servers": total_servers, "graphs": graphs, "error": error, "botcat": True, "view": {"index": True}}
        page = 'bot/content-reload.html' if request.method == 'POST' else 'bot.html'
        return render(request, page, context)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def dashboard(request, secret=False):
    try:
        # read only dashboard
        # if secret and secret != 'x'

        player = getPlayer(request.session.get("player", {}).get("tId", -1))
        page = 'bot/content-reload.html' if request.method == 'POST' else 'bot.html'

        if secret and secret != 'x':
            servers = Server.objects.filter(secret=secret)

        else:
            servers = player.server_set.all()
            for server in servers:
                if server.secret == 'x':
                    server.secret = json.loads(server.configuration).get("admin", {}).get("secret", 'x')
                    server.save()

        context = {"player": player, "servers": servers, "botcat": True, "secret": secret, "view": {"dashboard": True}}
        return render(request, page, context)

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

            if server is None:
                context["error"] = "No server found..."

            elif "admin" not in json.loads(server.configuration):
                context["error"] = "No admin section found. Try a !sync in the discord server..."

            elif post.get("mod") in ["rackets", "loot", "admin", "revive", "verify", "oc", "stocks", "chain"]:
                module = post.get("mod")
                context["module"] = module
                context["server"] = server
                configuration_keys = {
                    "admin": ["prefix", "channels_admin", "channels_welcome", "message_welcome", "other"],
                    "rackets": ["channels_alerts", "roles_alerts", "channels_allowed"],
                    "loot": ["channels_alerts", "roles_alerts", "channels_allowed"],
                    "revive": ["channels_alerts", "roles_alerts", "channels_allowed", "sending", "blacklist", "other"],
                    "verify": ["roles_verified", "channels_allowed", "channels_welcome", "factions", "positions", "other"],
                    "oc": ["channels_allowed", "currents", "notifications"],
                    "chain": ["channels_allowed", "currents"],
                    "stocks": ["channels_wssb", "channels_tcb", "channels_alerts", "roles_wssb", "roles_tcb", "roles_alerts"],
                }.get(post.get("mod"), [])

                configuration = json.loads(server.configuration)
                c = configuration.get(module, {})
                if post.get("typ") == "enable":
                    configuration[module] = {k: {} for k in configuration_keys}

                elif post.get("typ") == "disable":
                    configuration.pop(module)

                elif post.get("typ") in configuration_keys:
                    type = post.get("typ")  # channels or roles
                    id = post.get("key", 0)
                    name = post.get("val", "???")

                    if type not in c:
                        c[type] = {}

                    if id in c[type] and isinstance(c[type], dict):  # force toggle
                        c[type].pop(id)
                        if not len(c[type]):  # del if empty
                            del c[type]
                    else:
                        if type in ["sending", "blacklist"]:
                            c[type][id] = name

                        elif type in ["channels_allowed", "positions", "notifications"]:
                            # if type == "currents" and name == "disable" and id in c[type]:
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

                        elif type in ["message_welcome"]:
                            if id == "add":
                                c[type] = [line.strip() for line in name.split("\\n")]
                            elif id == "remove":
                                c[type] = []
                                del c[type]

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
                revive_server = Server.objects.filter(bot=server.bot, discord_id=post.get("key", 0)).first()
                revive_config = json.loads(revive_server.configuration).get("revive", {})
                context["revive_server"] = {"server_name": post.get("val"),
                                            "server_id": post.get("key", 0),
                                            "admins": revive_server.get_admins(),
                                            "public": revive_config.get("other", {}).get("public"),
                                            "sending": revive_config.get("sending"),
                                            }

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
