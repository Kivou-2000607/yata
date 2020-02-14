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

from bot.models import DiscordApp

import json


def saveBotsConfigs():
    for bot in DiscordApp.objects.all():
        var = dict({})
        # loop on configuration helpers attached to the bot
        for guild in bot.guild_set.all():
            # old config
            old = json.loads(bot.variables).get(str(guild.guildId), dict({}))

            # admin
            var[guild.guildId] = dict({})
            var[guild.guildId]["admin"] = {"pk": guild.pk,
                                           "name": guild.guildName,
                                           "owner": guild.guildOwnerName,
                                           "owner_id": guild.guildOwnerId,
                                           "contact": guild.guildContactName,
                                           "contact_id": guild.guildContactId}

            # # allowed channels
            # if guild.allowedChannels:
            #     var[guild.guildId]["admin"]["channels"] = json.loads(guild.allowedChannels)
            #
            # # allowed roles
            # if guild.allowedRoles:
            #     var[guild.guildId]["admin"]["roles"] = json.loads(guild.allowedRoles)

            # manage channels
            if guild.manageChannels:
                var[guild.guildId]["admin"]["manage"] = True

            if guild.systemChannel:
                var[guild.guildId]["admin"]["system"] = guild.systemChannel

            # loot module
            if guild.lootModule:
                var[guild.guildId]["loot"] = {"active": True, "channels": json.loads(guild.lootChannels)}

            # revive module
            if guild.reviveModule:
                # get past connected/backlist servers
                servers = old.get("revive", dict({})).get("servers", [])
                blacklist = old.get("revive", dict({})).get("blacklist", [])
                var[guild.guildId]["revive"] = {"active": True,
                                                "channels": json.loads(guild.reviveChannels),
                                                "servers": servers,
                                                "blacklist": blacklist}

            # stocks
            if guild.stockModule:
                var[guild.guildId]["stocks"] = {"active": True, "channels": json.loads(guild.stockChannels)}
                if guild.stockWSSB:
                    var[guild.guildId]["stocks"]["wssb"] = True
                if guild.stockTCB:
                    var[guild.guildId]["stocks"]["tcb"] = True
                if guild.stockAlerts:
                    var[guild.guildId]["stocks"]["alerts"] = True

            # chain
            if guild.chainModule:
                var[guild.guildId]["chain"] = {"active": True, "channels": json.loads(guild.chainChannels)}

            # repository
            # if guild.repoModule:
            #     var[guild.guildId]["repository"] = {"active": True, "name": guild.repoName, "token": guild.repoToken}

            # verify
            if guild.verifyModule:
                var[guild.guildId]["verify"] = {"active": True, "channels": json.loads(guild.verifyChannels)}
                if guild.verifyAppendFacId:
                    var[guild.guildId]["verify"]["id"] = True
                if guild.verifyForce:
                    var[guild.guildId]["verify"]["force"] = True
                if guild.verifyDailyVerify:
                    var[guild.guildId]["verify"]["dailyverify"] = True
                if guild.verifyDailyCheck:
                    var[guild.guildId]["verify"]["dailycheck"] = True
                if guild.verifyFacsRole:
                    var[guild.guildId]["verify"]["common"] = guild.verifyFacsRole
                factions = dict({})
                for f in guild.verifyFactions.all():
                    factions[f.tId] = f.discordName if f.discordName else f.name
                var[guild.guildId]["factions"] = factions

            # API module
            if guild.apiModule:
                var[guild.guildId]["api"] = {"active": True,
                                             "channels": json.loads(guild.apiChannels),
                                             "roles": json.loads(guild.apiRoles)}

            # loop over yata users to get their keys
            if len(guild.masterKeys.all()):
                var[guild.guildId]["keys"] = dict({p.tId: p.getKey() for p in guild.masterKeys.all() if p.botPerm})

        bot.variables = json.dumps(var)
        bot.save()
