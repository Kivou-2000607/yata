from django.db import models
from django.utils import timezone

from player.models import Player
from chain.models import Faction


# bot
class DiscordApp(models.Model):
    name = models.CharField(default="BOT_NAME", max_length=32)
    token = models.CharField(default="BOT_TOKEN", max_length=512, unique=True)
    variables = models.TextField(default="{}")

    def __str__(self):
        return "{}".format(self.name)


# bot configuration on a guild
class Guild(models.Model):
    configuration = models.ForeignKey(DiscordApp, on_delete=models.CASCADE)
    guildId = models.BigIntegerField(default=0)
    guildName = models.CharField(default="guild_name", max_length=32)

    # general options
    manageChannels = models.BooleanField(default=False)

    # stock module
    stockModule = models.BooleanField(default=False)
    stockWSSB = models.BooleanField(default=False)
    stockTCB = models.BooleanField(default=False)
    stockChannel = models.CharField(default="", blank=True, max_length=16)

    # chain module
    chainModule = models.BooleanField(default=False)
    chainChannel = models.CharField(default="", blank=True, max_length=16)

    # loot module
    lootModule = models.BooleanField(default=False)

    # verify module
    verifyModule = models.BooleanField(default=False)
    verifyForce = models.BooleanField(default=False)
    verifyKeys = models.ManyToManyField(Player, blank=True)
    verifyFactions = models.ManyToManyField(Faction, blank=True)

    # verify repository
    repoModule = models.BooleanField(default=False)
    repoName = models.CharField(default="repo_token", max_length=64)
    repoToken = models.CharField(default="repo_name", max_length=32)

    def __str__(self):
        return "{} on {} [{}]".format(self.configuration, self.guildName, self.guildId)
