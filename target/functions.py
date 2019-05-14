from django.utils import timezone

import json
import math

from yata.handy import apiCall
from chain.functions import BONUS_HITS


def updateAttacks(player):
    tId = player.tId
    key = player.key
    targetJson = json.loads(player.targetJson)

    error = False
    attacks = apiCall('user', "", 'attacks', key, sub='attacks')
    if 'apiError' in attacks:
        error = attacks

    else:
        remove = []
        for k, v in attacks.items():
            v["defender_id"] = str(v["defender_id"])  # have to string for json key
            if v["defender_id"] == str(tId):
                if v.get("attacker_name") is not None:
                    attacks[k]["defender_id"] = v.get("attacker_id")
                    attacks[k]["defender_name"] = v.get("attacker_name")
                    attacks[k]["bonus"] = 0
                    attacks[k]["result"] += " you"
                    attacks[k]["endTS"] = int(v["timestamp_ended"])
                else:
                    remove.append(k)

            elif int(v["chain"]) in BONUS_HITS:
                attacks[k]["endTS"] = int(v["timestamp_ended"])
                attacks[k]["flatRespect"] = float(v["respect_gain"]) / float(v['modifiers']['chainBonus'])
                attacks[k]["bonus"] = int(v["chain"])
            else:
                allModifiers = 1.0
                for mod, val in v['modifiers'].items():
                    allModifiers *= float(val)
                if v["result"] == "Mugged":
                    allModifiers *= 0.75
                baseRespect = float(v["respect_gain"]) / allModifiers
                level = int(math.exp(4. * baseRespect - 1))
                attacks[k]["endTS"] = int(v["timestamp_ended"])
                attacks[k]["flatRespect"] = float(v['modifiers']["fairFight"]) * baseRespect
                attacks[k]["bonus"] = 0
                attacks[k]["level"] = level

        for k in remove:
            del attacks[k]

        targetJson["attacks"] = attacks
        player.targetJson = json.dumps(targetJson)
        nTargets = 0 if "targets" not in targetJson else len(targetJson["targets"])
        player.targetInfo = "{}".format(nTargets)
        player.targetUpda = int(timezone.now().timestamp())
        player.lastUpdateTS = int(timezone.now().timestamp())
        player.save()

    return error
