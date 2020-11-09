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

from django.http import JsonResponse

import json

from player.models import PlayerData


class BanPlayersMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # get bans lists
        playerdata = PlayerData.objects.first()

        if playerdata is None:
            ipBan = {}
            uidBan = {}
        else:
            ipBan = json.loads(playerdata.ipsBan)
            uidBan = json.loads(playerdata.uidBan)

        uid = str(request.session.get('player', {}).get('tId', -1))
        ip = str(request.META.get('REMOTE_ADDR'))

        if uid in uidBan:
            return JsonResponse({"error": {"code": 2, "error": f'Torn ID {uid} is currently banned: {uidBan.get(uid, "No reasons")}'}}, status=403)

        elif ip in ipBan:
            return JsonResponse({"error": {"code": 2, "error": f'IP address {ip} is currently banned: {ipBan.get(ip, "No reasons")}'}}, status=403)

        return self.get_response(request)
