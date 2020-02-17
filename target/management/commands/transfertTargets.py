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

import json

from player.models import Player
from target.models import *


class Command(BaseCommand):
    def handle(self, **options):
        for player in Player.objects.only('targetJson').all():
            targets = json.loads(player.targetJson)
            for k, v in targets.get("targets", dict({})).items():

                defaults = {
                    "name": v["targetName"],
                    "level": v["level"],
                    "life_maximum": v["lifeMax"],
                    "life_current": v["life"],
                    "last_action_relative": v["lastAction"],
                    "status_description": "refresh me",
                    "update_timestamp": v["lastUpdate"],
                }
                t, s = Target.objects.get_or_create(target_id=k, defaults=defaults)

                defaults = {
                    "update_timestamp": int(v["lastUpdate"]),
                    "last_attack_timestamp": int(v["endTS"]),
                    "fairFight": float(v["fairFight"]),
                    "baseRespect": float(0.0),
                    "flatRespect": float(v["respect"]),
                    "result": str(v["result"])[:16],
                    "note": str(v["note"])[:128]}

                t, s = player.targetinfo_set.get_or_create(target_id=k, defaults=defaults)
