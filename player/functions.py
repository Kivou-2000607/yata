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

from yata.handy import *
from awards.functions import updatePlayerAwards
from faction.models import Faction
# from chain.models import Faction
from awards.models import AwardsData
from target.functions import getTargets
from company.models import CompanyDescription
from company.models import Company

def updatePlayer(player, i=None, n=None):
    """ update player information

    """

    progress = "{:04}/{:04}: ".format(i, n) if i is not None else ""

    if player.tId == -1:
        print("[player.functions.updatePlayer] {}{} action: ignore".format(progress, player.nameAligned()))
        return 0

    # API Calls
    player.updateKeyLevel()

    if player.key_level == 1:
        selection = [
            "personalstats",
            "profile",
            "discord"
        ]
    elif player.key_level == 2:
        selection = [
            "personalstats",
            "crimes",
            "education",
            "workstats",
            "perks",
            "gym",
            "merits",
            "profile",
            "medals",
            "honors",
            "icons",
            "bars",
            "discord",
            "weaponexp"
        ]
    elif player.key_level >= 3:
        selection = [
            "personalstats",
            "crimes",
            "education",
            "battlestats",
            "workstats",
            "perks",
            "gym",
            "networth",
            "merits",
            "profile",
            "medals",
            "honors",
            "icons",
            "bars",
            "discord",
            "weaponexp",
            "hof"
        ]
    else:
        selection = []

    user = apiCall('user', '', ','.join(selection), player.getKey(), verbose=False)

    # set active
    player.active = int(timezone.now().timestamp()) - player.lastActionTS < 60 * 60 * 24 * 31

    # change to false if error code 2
    player.validKey = False if user.get('apiErrorCode', 0) in [1, 2, 10] else player.validKey

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
        print("[player.functions.updatePlayer] {}{} action: {:010} active: {:1} api: {:1} -> delete user".format(progress, player.nameAligned(), player.lastActionTS, player.active, player.validKey))
        # player.delete()
        player.save()
        return 0

    elif 'apiError' in user: # skip if api error (not invalid key)
        print("[player.functions.updatePlayer] {}{} action: {:010} active: {:1} api: {:1} -> api error {}".format(progress, player.nameAligned(), player.lastActionTS, player.active, player.validKey, user["apiError"]))
        player.key_last_code = user["apiErrorCode"]
        player.save()
        return 0

    else:
        player.key_last_code = 0
        print("[player.functions.updatePlayer] {}{} action: {:010} active: {:1} api: {:1}".format(progress, player.nameAligned(), player.lastActionTS, player.active, player.validKey))

    # update basic info (and chain)
    player.name = user.get("name", "?")
    player.factionId = user.get("faction", dict({})).get("faction_id", 0)
    player.factionNa = user.get("faction", dict({})).get("faction_name", "N/A")

    # update chain info
    if player.factionId:
        faction = Faction.objects.filter(tId=player.factionId).first()
        if faction is None:
            faction = Faction.objects.create(tId=player.factionId)
        faction.name = player.factionNa

        if 'money' in apiCall('faction', '', 'currency', player.getKey()):
            player.factionAA = True
            player.chainInfo = "{}".format(player.factionNa)
        else:
            player.factionAA = False
            player.chainInfo = "{}".format(player.factionNa)
        faction.manageKey(player)

        faction.save()

    else:
        player.factionAA = False
        player.chainInfo = "N/A"
    player.chainUpda = int(timezone.now().timestamp())

    # update company info
    player.companyId = user.get("job", {}).get("company_id", 0)
    if player.companyId:
        player.companyTy = user.get("job", {}).get("company_type", 0)
        player.companyNa = user.get("job", {}).get("company_name", "-")
        player.companyDi = True if user.get("job", {}).get("position") == "Director" else False
        company_description = CompanyDescription.objects.filter(tId=player.companyTy).first()
        defaults = {"name": player.companyNa}
        if player.companyDi:
            defaults["director"] = player.tId
        company, create = Company.objects.update_or_create(company_description=company_description, tId=player.companyId, defaults=defaults)
    else:
        player.companyTy = 0
        player.companyNa = "-"
        player.companyDi = False

    player.wman = user.get("manual_labor", 0)
    player.wint = user.get("intelligence", 0)
    player.wend = user.get("endurance", 0)

    # update awards info
    # only award score
    player.getAwards(userInfo=user)

    # clean targets
    old = tsnow() - 2678400  # 1 month old
    targets = getTargets(player)
    player.attack_set.filter(timestamp_ended__lt=old).delete()
    player.revive_set.filter(timestamp__lt=old).delete()
    player.targetInfo = len(targets)

    player.lastUpdateTS = int(timezone.now().timestamp())
    player.save()

    # print("[player.functions.updatePlayer] {} / {}".format(player.chainInfo, player.awardsInfo))
