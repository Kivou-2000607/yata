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
from awards.models import AwardsData


class Command(BaseCommand):
    def handle(self, **options):

        # update players info
        print("[command.player.updateplayers] UPDATE PLAYERS")
        for player in Player.objects.filter(validKey=True):
            try:
                player.update_info()
            except BaseException as e:
                print(f"[command.player.updateplayers]: {e}")
                print(traceback.format_exc())

        # temp... delete me
        # for player in Player.objects.filter(validKey=False):
        #     player.awardsScor = int(float(player.awardsInfo) * 10000)
        #     print("[command.player.updateplayers] COMMENT ME. update non valid key award score. {}: {}".format(player, player.awardsScor))
        #     player.save()

        # compute rank
        print("[command.player.updateplayers] COMPUTE RANKS")
        for i, player in enumerate(Player.objects.order_by('-awardsScor')):
            print("[command.player.updateplayers] #{}: {} {:.4f}".format(i + 1, player, player.awardsScor / 10000.))
            player.awardsRank = i + 1
            player.save()

        # compute hof graph
        print("[command.player.updateplayers] COMPUTE HOF GRAPH")
        hofGraph = []
        for p in Player.objects.all():
            hofGraph.append(float(p.awardsScor / 10000.0))
        bins = numpy.logspace(-2, 2, num=101)
        bins[0] = 0
        histo, _ = numpy.histogram(hofGraph, bins=bins)
        cBins = [0.5 * float(a + b) for a, b in zip(bins[:-1], bins[1:])]
        hofGraph = [[float(x), int(y), float(xm), float(xp), 0] for x, y, xm, xp in zip(cBins, histo, bins[:-1], bins[1:])]
        hofGraph[0][4] = hofGraph[0][1]
        for i in range(len(hofGraph) - 1):
            hofGraph[i + 1][4] = hofGraph[i + 1][1] + hofGraph[i][4]

        hof = AwardsData.objects.first()
        hof.hofHistogram = json.dumps(hofGraph)
        hof.save()
