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

from django.conf import settings

from chain.models import Faction
from yata.handy import apiCall

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


bridge = {"Criminality": 0,
          "Fortitude": 1,
          "Voracity": 2,
          "Toleration": 3,
          "Excursion": 4,
          "Steadfast": 5,
          "Aggression": 6,
          "Suppression": 7,
        }

posterOpt = dict({})

#


class Command(BaseCommand):
    def handle(self, **options):
        print("[command.chain.tree] start")

        for faction in Faction.objects.all():
            print("[command.chain.tree] faction {}".format(faction))

            # get api key
            if faction.apiString == "0":
                print("[command.chain.tree] no api key found")
                break
            factionId = faction.tId
            keyHolder, key = faction.getRadomKey()

            # call for upgrades
            upgrades = apiCall('faction', factionId, 'upgrades', key, sub='upgrades')
            if 'apiError' in upgrades:
                print('[command.chain.tree] api key error: {}'.format((upgrades['apiError'])))
                break

            faction = apiCall('faction', factionId, 'basic', key)
            if 'apiError' in faction:
                print('[command.chain.tree] api key error: {}'.format((faction['apiError'])))
                break

            # building upgrades tree
            tree = dict({})
            for k, upgrade in sorted(upgrades.items(), key=lambda x: x[1]['branchorder'], reverse=False):
                if upgrade['branch'] != 'Core':
                    if tree.get(upgrade['branch']) is None:
                        tree[upgrade['branch']] = dict({})
                    tree[upgrade['branch']][upgrade['name']] = upgrade

            factionTree(faction, upgrades, tree)
