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
from player.models import Player

import traceback


class Command(BaseCommand):
    def handle(self, **options):

        # update players info
        for player in Player.objects.filter(validKey=True):
            try:
                player.update_info()
            except BaseException as e:
                print(f"[command.player.updateplayers]: {e}")
                print(traceback.format_exc())

        # temp... delete me
        for player in Player.objects.filter(validKey=False):
            player.awardsScor = int(float(player.awardsInfo) * 10000)
            print("[command.player.updateplayers] COMMENT ME. update non valid key award score. {}: {}".format(player, player.awardsScor))
            player.save()

        # compute rank
        for i, player in enumerate(Player.objects.order_by('-awardsScor')):
            print("[command.player.updateplayers] #{}: {} {:.4f}".format(i + 1, player, player.awardsScor/10000.))
            player.awardsRank = i + 1
            player.save()
