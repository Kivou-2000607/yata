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

from faction.functions import BONUS_HITS, modifiers2lvl1
from yata.handy import apiCall, tsnow


def updateAttacks(player, full=False):
    from target.models import Attack

    # if tsnow() - player.attacksUpda < 15 * 60:
    #     return False, player.attack_set.all()

    query = "attacksfull,timestamp" if full else "attacks,timestamp"
    req = apiCall("user", "", query, player.getKey())
    if "apiError" in req:
        return req, player.attack_set.order_by("-timestamp_ended").all()

    attacks = req.get("attacks", dict({}))
    timestamp = req.get("timestamp", 0)

    # in case 0 attacks API returns []
    if not len(attacks):
        attacks = dict({})

    old = tsnow() - 2678400  # 1 month old
    batch = Attack.objects.bulk_operation()
    for k, v in attacks.items():
        if v["timestamp_ended"] < old:
            continue

        if full:
            v["attacker_name"] = "Player"
            v["attacker_factionname"] = "Faction"
            v["defender_name"] = "Player"
            v["defender_factionname"] = "Faction"
            v["chain"] = 0
            v["modifiers"] = {"fair_fight": 1, "war": 1, "retaliation": 1, "group_attack": 1, "overseas": 1, "chain_bonus": 1, "warlord_bonus": 1}

        # ignore stealth incoming
        if v.get("stealthed") and v["defender_id"] == player.tId:
            continue

        if v["attacker_id"] == player.tId:
            v["attacker"] = True
            v["targetId"] = v["defender_id"]
        else:
            v["attacker"] = False
            v["targetId"] = v["attacker_id"]

        if v["chain"] in BONUS_HITS:
            # case attacker and bonus hit
            v["flat_respect"] = float(v["respect"]) / float(v["modifiers"]["chain_bonus"])
            v["bonus"] = v["chain"]
        else:
            allModifiers = 1.0
            for mod in ["fair_fight", "war", "retaliation", "group_attack", "overseas", "chain_bonus", "warlord_bonus"]:
                allModifiers *= float(v["modifiers"].get(mod, 1))
            if v["result"] == "Mugged":
                allModifiers *= 0.75
            base_respect = float(v["respect"]) / allModifiers
            level = 1 if full else round(198 * (base_respect - (197 / 198)))
            v["base_respect"] = base_respect
            v["flat_respect"] = float(v["modifiers"]["fair_fight"]) * base_respect
            v["bonus"] = 0
            v["level"] = level

        if v["defender_name"] == "Gareth-Bale":
            print(f"{allModifiers}")

        v = modifiers2lvl1(v)

        batch.update_or_create(tId=int(k), player_id=int(player.id), defaults=v)

    if batch.count():
        batch.run()
    player.attack_set.filter(timestamp_ended__lt=old).delete()

    player.attacksUpda = int(timestamp)
    player.save()

    return False, player.attack_set.order_by("-timestamp_ended").all()


def getTargets(player):
    targets = dict({})

    # get Target Info of the player
    for targetInfo in player.targetinfo_set.all():
        _, target_id, target = targetInfo.getTarget()
        targets[target_id] = target

    return targets


def updateRevives(player):
    player.tId
    key = player.getKey()

    req = apiCall("user", "", "revives,timestamp", key)
    if "apiError" in req:
        return req, player.revive_set.order_by("-timestamp").all()
    else:
        revives = req.get("revives", dict({}))
        timestamp = req.get("timestamp", 0)

        # needs to convert to dict if empty because if empty returns []
        if not len(revives):
            revives = dict({})

        # get database revives and delete 1 month old
        player_revives = player.revive_set.all()
        lastMonth = timestamp - 31 * 24 * 3600
        player_revives.filter(timestamp__lt=lastMonth).delete()

        for k, v in revives.items():
            # exists = len(player_revives.filter(tId=int(k)))
            old = v.get("timestamp", 0) < lastMonth
            if not old:
                revives[k]["target_last_action_status"] = revives[k]["target_last_action"].get("status", "Unknown")
                revives[k]["target_last_action_timestamp"] = revives[k]["target_last_action"].get("timestamp", 0)
                del v["target_last_action"]
                v["result"] = v["result"] == "success"
                try:
                    player.revive_set.get_or_create(tId=int(k), defaults=v)
                except BaseException:
                    player.revive_set.filter(tId=int(k)).all().delete()
                    player.revive_set.get_or_create(tId=int(k), defaults=v)

        player.revivesUpda = int(timestamp)
        player.save()

    return False, player.revive_set.order_by("-timestamp").all()


def convertElaspedString(str):
    return str.replace("minute", "min").replace("hour", "hr").replace("second", "sec")
