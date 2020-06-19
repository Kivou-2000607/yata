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


def deleteOldBots():
    for bot in DiscordApp.objects.all():
        var = json.loads(bot.variables)
        todel = []
        for guildId in var:
            if bot.guild_set.filter(guildId=guildId).first() is None:
                todel.append(str(guildId))

        for k in todel:
            del var[k]
        bot.variables = json.dumps(var)
        bot.save()


def saveBotsConfigs():

    # loop over all bots
    for bot in DiscordApp.objects.all():
        saveBotConfigs(bot)


def saveBotConfigs(bot):

    # loop over all
    for guild in bot.guild_set.all():
        saveGuildConfig(guild)


def saveGuildConfig(guild):
    # get bot
    bot = guild.configuration

    # old config
    # var: full config of the bot (all guilds)
    # old: tmp config of the guild (for this bot)
    var = json.loads(bot.variables)
    old = var.get(str(guild.guildId), dict({}))

    # admin
    var[str(guild.guildId)] = dict({})
    var[str(guild.guildId)]["admin"] = {"pk": guild.pk,
                                        "name": guild.guildName,
                                        "owner": guild.guildOwnerName,
                                        "owner_id": guild.guildOwnerId,
                                        "contact_torn": guild.guildContactTornName,
                                        "contact_torn_id": guild.guildContactTornId,
                                        "contact_discord": guild.guildContactDiscordName,
                                        "contact_discord_id": guild.guildContactDiscordId,
                                        "joined_at": guild.guildJoinedTime}

    # # allowed channels
    # if guild.allowedChannels:
    #     var[str(guild.guildId)]["admin"]["channels"] = json.loads(guild.allowedChannels)
    #
    # # allowed roles
    # if guild.allowedRoles:
    #     var[str(guild.guildId)]["admin"]["roles"] = json.loads(guild.allowedRoles)

    # manage channels
    if guild.manageChannels:
        var[str(guild.guildId)]["admin"]["manage"] = True

    if guild.systemChannel:
        var[str(guild.guildId)]["admin"]["system"] = guild.systemChannel

    if guild.welcomeMessage:
        var[str(guild.guildId)]["admin"]["welcome"] = guild.welcomeMessageText

    # loot module
    if guild.lootModule:
        channels = [c.lower() for c in json.loads(guild.lootChannels)]
        var[str(guild.guildId)]["loot"] = {"active": True, "channels": channels, "roles": ["Looter"]}

    # revive module
    if guild.reviveModule:
        # get past connected/backlist servers
        servers = old.get("revive", dict({})).get("servers", [])
        blacklist = old.get("revive", dict({})).get("blacklist", [])
        channels = [c.lower() for c in json.loads(guild.reviveChannels)]
        var[str(guild.guildId)]["revive"] = {"active": True,
                                             "channels": channels,
                                             "servers": servers,
                                             "blacklist": blacklist, "roles": ["Reviver"]}

    # stocks
    if guild.stockModule:
        channels = [c.lower() for c in json.loads(guild.stockChannels)]
        var[str(guild.guildId)]["stocks"] = {"active": True, "channels": channels, "roles": ["Trader"]}
        if guild.stockWSSB:
            var[str(guild.guildId)]["stocks"]["wssb"] = True
        if guild.stockTCB:
            var[str(guild.guildId)]["stocks"]["tcb"] = True
        if guild.stockAlerts:
            var[str(guild.guildId)]["stocks"]["alerts"] = True

    # racket
    if guild.racketModule:
        channels = [c.lower() for c in json.loads(guild.racketChannels)]
        roles = [c for c in json.loads(guild.racketRoles)]
        var[str(guild.guildId)]["rackets"] = {"active": True, "channels": channels, "roles": roles}

    # chain
    if guild.chainModule:
        retal = old.get("chain", dict({})).get("retal", dict({}))
        channels = [c.lower() for c in json.loads(guild.chainChannels)]
        var[str(guild.guildId)]["chain"] = {"active": True,
                                            "channels": channels,
                                            "retal": retal}

    # crimes
    if guild.crimesModule:
        oc = old.get("crimes", dict({})).get("oc", dict({}))
        channels = [c.lower() for c in json.loads(guild.crimesChannels)]
        var[str(guild.guildId)]["crimes"] = {"active": True,
                                             "channels": channels,
                                             "oc": oc}

    # repository
    # if guild.repoModule:
    #     var[str(guild.guildId)]["repository"] = {"active": True, "name": guild.repoName, "token": guild.repoToken}

    # verify
    if guild.verifyModule:
        channels = [c.lower() for c in json.loads(guild.verifyChannels)]
        var[str(guild.guildId)]["verify"] = {"active": True, "channels": channels, "roles": ["Verified"]}
        if guild.verifyAppendFacId:
            var[str(guild.guildId)]["verify"]["id"] = True
        if guild.verifyForce:
            var[str(guild.guildId)]["verify"]["force"] = True
        if guild.verifyDailyVerify:
            var[str(guild.guildId)]["verify"]["dailyverify"] = True
        if guild.verifyDailyCheck:
            var[str(guild.guildId)]["verify"]["dailycheck"] = True
        if guild.verifyWeeklyVerify:
            var[str(guild.guildId)]["verify"]["weeklyverify"] = True
        if guild.verifyWeeklyCheck:
            var[str(guild.guildId)]["verify"]["weeklycheck"] = True
        if guild.verifyFacsRole:
            var[str(guild.guildId)]["verify"]["common"] = guild.verifyFacsRole
        factions = dict({})
        for f in guild.verifyFactions.all():
            factions[f.tId] = f.discordName if f.discordName else f.name
        var[str(guild.guildId)]["factions"] = factions

    # API module
    if guild.apiModule:
        channels = [c.lower() for c in json.loads(guild.apiChannels)]
        var[str(guild.guildId)]["api"] = {"active": True,
                                          "channels": channels,
                                          "roles": json.loads(guild.apiRoles)}

    # loop over yata users to get their keys
    if len(guild.masterKeys.all()):
        var[str(guild.guildId)]["keys"] = [p.tId for p in guild.masterKeys.all()]

    bot.variables = json.dumps(var)
    bot.save()
