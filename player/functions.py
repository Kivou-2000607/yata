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

from django.db import models
from django.utils import timezone

import json

from yata.handy import apiCall
from awards.functions import updatePlayerAwards
# from faction.models import Faction
from chain.models import Faction
from awards.models import AwardsData


def updatePlayer(player, i=None, n=None):
    """ update player information

    """

    progress = "{:04}/{:04}: ".format(i, n) if i is not None else ""
    print(player.key_set.all())
    # API Calls
    user = apiCall('user', '', 'personalstats,crimes,education,battlestats,workstats,perks,networth,merits,profile,medals,honors,icons,bars,discord,weaponexp', player.getKey(), verbose=False)

    # set active
    player.active = int(timezone.now().timestamp()) - player.lastActionTS < 60 * 60 * 24 * 31

    # change to false if error code 2
    player.validKey = False if user.get('apiErrorCode', 0) == 2 else player.validKey

    # change to true if fetch result
    player.validKey = True if user.get('name', False) else player.validKey

    # delete key if not valid
    if not player.validKey:
        player.key_set.all().delete()

    # discrod id
    dId = user.get('discord', {'discordID': ''})['discordID']
    player.dId = 0 if dId in [''] else dId

    # skip if not yata active and no valid key
    if not player.active and not player.validKey:
        player.key_set.all().delete()
        print("[player.functions.updatePlayer] {}{} action: {:010} active: {:1} api: {:1} -> delete user".format(progress, player, player.lastActionTS, player.active, player.validKey))
        # player.delete()
        player.save()
        return 0

    # skip if api error (not invalid key)
    elif 'apiError' in user:
        print("[player.functions.updatePlayer] {}{} action: {:010} active: {:1} api: {:1} -> api error {}".format(progress, player, player.lastActionTS, player.active, player.validKey, user["apiError"]))
        player.save()
        return 0

    # skip if not active in torn since last update
    # elif player.lastUpdateTS > int(user.get("last_action")["timestamp"]):
    #     print("[player.functions.updatePlayer] {}{} skip since not active since last update".format(progress, player))
    #     return 0

    # do update
    else:
        print("[player.functions.updatePlayer] {}{} action: {:010} active: {:1} api: {:1}".format(progress, player, player.lastActionTS, player.active, player.validKey))

    # update basic info (and chain)
    player.name = user.get("name", "?")
    player.factionId = user.get("faction", dict({})).get("faction_id", 0)
    player.factionNa = user.get("faction", dict({})).get("faction_name", "N/A")

    # update chain info
    # if player.factionId:
    #     faction = Faction.objects.filter(tId=player.factionId).first()
    #     if faction is None:
    #         faction = Faction.objects.create(tId=player.factionId)
    #     faction.name = player.factionNa
    #
    #     chains = apiCall("faction", "", "chains", player.getKey(), verbose=False)
    #     if chains.get("chains") is not None:
    #         player.factionAA = True
    #         player.chainInfo = "{} [AA]".format(player.factionNa)
    #     else:
    #         player.factionAA = False
    #         player.chainInfo = "{}".format(player.factionNa)
    #     faction.manageKey(player)
    #
    #     faction.save()

    # update chain info
    if player.factionId:
        faction = Faction.objects.filter(tId=player.factionId).first()
        if faction is None:
            faction = Faction.objects.create(tId=player.factionId)
        faction.name = player.factionNa

        chains = apiCall("faction", "", "chains", player.getKey(), verbose=False)
        if chains.get("chains") is not None:
            player.factionAA = True
            player.chainInfo = "{} [AA]".format(player.factionNa)
            faction.addKey(player.tId, player.getKey())
        else:
            player.factionAA = False
            player.chainInfo = "{}".format(player.factionNa)
            faction.delKey(player.tId)

        faction.save()

    else:
        player.factionAA = False
        player.chainInfo = "N/A"
    player.chainUpda = int(timezone.now().timestamp())

    # update awards info
    # tornAwards = apiCall('torn', '', 'honors,medals', player.getKey())
    tornAwards = AwardsData.objects.first().loadAPICall()
    if 'apiError' in tornAwards:
        player.awardsJson = json.dumps(tornAwards)
        player.awardsInfo = "0"
    else:
        updatePlayerAwards(player, tornAwards, user)
    player.awardsUpda = int(timezone.now().timestamp())

    # clean '' targets
    targetsAttacks = json.loads(player.targetJson)
    if len(targetsAttacks):
        targets = targetsAttacks.get("targets", dict({}))
        for k, v in targets.items():
            if k == '':
                print("[player.functions.updatePlayer] delete target of player {}: {}".format(player, v))
        if targets.get('') is not None:
            del targets['']
        targetsAttacks["targets"] = targets
        player.targetJson = json.dumps(targetsAttacks)
        player.targetInfo = len(targets)

    player.lastUpdateTS = int(timezone.now().timestamp())
    player.save()

    # print("[player.functions.updatePlayer] {} / {}".format(player.chainInfo, player.awardsInfo))
