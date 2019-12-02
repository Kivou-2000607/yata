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

from yata.handy import apiCall
from yata.handy import returnError
from player.models import Player


# def index(request):
#     try:
#         if request.session.get('player'):
#             print('[view.bot.index] get player id from session')
#             tId = request.session["player"].get("tId")
#             player = Player.objects.filter(tId=tId).first()
#             player.lastActionTS = int(timezone.now().timestamp())
#             player.active = True
#
#             if player.dId:
#                 print("registered to discord")
#             else:
#                 print("not registered to discord")
#
#             preference = player.preference_set.first()
#             if preference is None:
#                 preference = player.preference_set.create()
#
#             player.save()
#             context = {"player": player, "preference": preference}
#             return render(request, "bot.html", context)
#
#         else:
#             return returnError(type=403, msg="You might want to log in.")
#
#     except Exception:
#         return returnError()
#
#
# def togglePref(request, type):
#     try:
#         if request.session.get('player') and request.method == "POST":
#             print('[view.bot.updateId] get player id from session')
#             tId = request.session["player"].get("tId")
#             player = Player.objects.filter(tId=tId).first()
#
#             preference = player.preference_set.first()
#             if type in ['event']:
#                 preference.notificationsEvents = not preference.notificationsEvents
#
#             preference.save()
#
#             context = {"player": player, "preference": preference}
#             return render(request, "bot/notifications-events.html", context)
#
#         else:
#             message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
#             return returnError(type=403, msg=message)
#
#     except Exception:
#         return returnError()
#
#
# def updateId(request):
#     try:
#         if request.session.get('player') and request.method == "POST":
#             print('[view.bot.updateId] get player id from session')
#             tId = request.session["player"].get("tId")
#             player = Player.objects.filter(tId=tId).first()
#
#             # update inventory of bazaarJson
#             error = False
#             discord = apiCall("user", "", "discord", player.key)
#             if 'apiError' in discord:
#                 error = {"apiErrorSub": discord["apiError"]}
#             else:
#                 dId = discord.get('discord', {'discordID': ''})['discordID']
#                 player.dId = 0 if dId in [''] else dId
#                 player.save()
#
#             context = {'player': player, 'error': error}
#             return render(request, "bot/discord-id.html", context)
#
#         else:
#             message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
#             return returnError(type=403, msg=message)
#
#     except Exception:
#         return returnError()
