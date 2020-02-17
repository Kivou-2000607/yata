"""
Copyright 2020 kivou.2000607@gmail.com

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

import json
import math

from yata.handy import *
from faction.functions import BONUS_HITS
from faction.functions import modifiers2lvl1
from target.models import *

def updateAttacks(player):

    # if tsnow() - player.attacksUpda < 15 * 60:
    #     return False, player.attack_set.all()

    req = apiCall('user', "", 'attacks,timestamp', player.getKey())
    if 'apiError' in req:
        return req, player.attack_set.all()

    attacks = req.get("attacks", dict({}))
    timestamp = req.get("timestamp", 0)

    # in case 0 attacks API returns []
    if not len(attacks):
        attacks = dict({})

    remove = []
    for k, v in attacks.items():

        # ignore stealth
        if v.get("attacker_name") is None:
            print("ignore", v)
            continue

        v["attacker"] = True

        if int(v["defender_id"]) == player.tId:
            # case defender
            v["attacker"] = False
            v["bonus"] = 0

        elif v["chain"] in BONUS_HITS:
            # case attacker and bonus hit
            v["flatRespect"] = float(v["respect_gain"]) / float(v['modifiers']['chainBonus'])
            v["bonus"] = v["chain"]

        else:
            # case attacker and not bonus hit
            allModifiers = 1.0
            for mod, val in v['modifiers'].items():
                allModifiers *= float(val)
            if v["result"] == "Mugged":
                allModifiers *= 0.75
            baseRespect = float(v["respect_gain"]) / allModifiers
            level = int(math.exp(4. * baseRespect - 1))
            v["baseRespect"] = baseRespect
            v["flatRespect"] = float(v['modifiers']["fairFight"]) * baseRespect
            v["bonus"] = 0
            v["level"] = level

        v = modifiers2lvl1(v)
        player.attack_set.get_or_create(tId=int(k), defaults=v)

    player.attacksUpda = int(timestamp)
    player.save()

    return False, player.attack_set.all()


def getTargets(player):
    targets = dict({})

    # get Target Info of the player
    for targetInfo in player.targetinfo_set.all():
        _, target_id, target = targetInfo.getTarget()
        targets[target_id] = target

    return targets


def updateRevives(player):
    tId = player.tId
    key = player.getKey()

    error = False
    req = apiCall('user', "", 'revives,timestamp', key)
    if 'apiError' in req:
        error = req
    else:
        revives = req.get("revives", dict({}))

        # needs to convert to dict if empty because if empty returns []
        if not len(revives):
            revives = dict({})

        # get database revives and delete 1 month old
        player_revives = player.revive_set.all()
        lastMonth = req.get("timestamp", 0) - 31 * 24 * 3600
        player_revives.filter(timestamp__lt=lastMonth).delete()

        for k, v in revives.items():
            if not len(player_revives.filter(tId=int(k))) and v.get("timestamp", 0) > lastMonth:
                del revives[k]["reviver_id"]
                del revives[k]["reviver_name"]
                del revives[k]["reviver_faction"]
                del revives[k]["reviver_factionname"]
                player.revive_set.create(tId=k, **v)

        player.save()

    return error


def convertElaspedString(str):
    return str.replace("minute", "min").replace("hour", "hr").replace("second", "sec")
