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

from yata.handy import returnError
from django.utils.safestring import mark_safe

import json

from player.models import PlayerData


class FilterIPMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # get banned ips
        playerdata = PlayerData.objects.first()
        if playerdata is None:
            ipsBan = []
        else:
            ipsBan = json.loads(playerdata.ipsBan)

        # get client ip
        ip = request.META.get('REMOTE_ADDR')

        # return 403
        if ip in ipsBan:
            message = '<p><i class="fas fa-gavel"></i>&nbsp&nbspYou are banned from YATA by IP address.</p>\
                       <p>Reason: <span class="error">{}</span></p>\
                       <p>If you want to know why contact ingame <a href="https://www.torn.com/profiles.php?XID=2000607" target="_blank">Kivou [2000607]</a>.</p>'.format(ipsBan[str(ip)])
            return returnError(type=403, msg=mark_safe(message), home=False)

        return self.get_response(request)
