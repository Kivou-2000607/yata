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


from django.core.management.base import BaseCommand

import traceback
import numpy
import json

from player.models import Player
from player.functions import updatePlayer
from yata.handy import *

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('json_path', type=str)

    def handle(self, **options):
        json_path = options['json_path']
        keys = json.load(open(json_path, 'r'))
        for k in keys:
            print(f'[add user by key] {k}')
            user = apiCall('user', '', 'profile', k)
            if 'apiError' in user:
                print(user)
                continue

            # create/update player in the database
            player = Player.objects.filter(tId=user.get('player_id')).first()

            new_player = False
            if player is None:
                print('[add user by key] create new player')
                player = Player.objects.create(tId=int(user.get('player_id')))
                new_player = True

            print('[add user by key] update player')
            player.addKey(k)
            # player.key = p.get('key')
            player.active = True
            player.lastActionTS = tsnow()
            updatePlayer(player)
            print('[add user by key] save player')
            player.save()
