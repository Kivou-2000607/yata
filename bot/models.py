from django.db import models
from django.utils import timezone

from player.models import Player
from faction.models import Faction


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
    guildOwnerId = models.BigIntegerField(default=0)
    guildOwnerName = models.CharField(default="guild_owner", max_length=32)
    guildContactId = models.IntegerField(default=0)
    guildContactName = models.CharField(default="guild_contact", max_length=32)
    botContactId = models.IntegerField(default=2000607)
    botContactName = models.CharField(default="Kivou", max_length=32)


    # general options
    masterKeys = models.ManyToManyField(Player, blank=True)
    manageChannels = models.BooleanField(default=True)
    systemChannel = models.CharField(default='', blank=True, max_length=32)

    # verify module
    verifyModule = models.BooleanField(default=False)
    verifyForce = models.BooleanField(default=False)
    verifyFactions = models.ManyToManyField(Faction, blank=True)
    verifyFacsRole = models.CharField(default="", blank=True, max_length=16)
    verifyAppendFacId = models.BooleanField(default=True)
    verifyDailyVerify = models.BooleanField(default=False)
    verifyDailyCheck = models.BooleanField(default=False)
    verifyChannels = models.CharField(default='["verify-id"]', blank=True, max_length=64)

    # stock module
    stockModule = models.BooleanField(default=False)
    stockWSSB = models.BooleanField(default=False)
    stockTCB = models.BooleanField(default=False)
    stockAlerts = models.BooleanField(default=False)
    stockChannels = models.CharField(default='["stocks"]', blank=True, max_length=64)

    # chain module
    chainModule = models.BooleanField(default=False)
    chainChannels = models.CharField(default='["chain"]', blank=True, max_length=64)

    # loot module
    lootModule = models.BooleanField(default=False)
    lootChannels = models.CharField(default='["loot"]', blank=True, max_length=64)

    # loot module
    reviveModule = models.BooleanField(default=False)
    reviveChannels = models.CharField(default='["revive"]', blank=True, max_length=64)

    # API module
    apiModule = models.BooleanField(default=False)
    apiChannels = models.CharField(default='["*"]', blank=True, max_length=64)
    apiRoles = models.CharField(default='["*"]', blank=True, max_length=64)

    # verify repository
    # repoModule = models.BooleanField(default=False)
    # repoName = models.CharField(default="repo_token", max_length=64)
    # repoToken = models.CharField(default="repo_name", max_length=32)

    def __str__(self):
        return "{} on {} [{}]".format(self.configuration, self.guildName, self.guildId)


class Chat(models.Model):
    name = models.CharField(default="secret", max_length=128)
    uid = models.IntegerField(default=0)
    secret = models.CharField(default="secret", max_length=128)
    check = models.CharField(default="check", max_length=128)
    key = models.CharField(default="key", max_length=128)
    hookurl = models.CharField(default="url", max_length=512)

    def __str__(self):
        return "Chat {}".format(self.name)

    def setNewestSecret(self):
        cred = self.credential_set.all().order_by("-timestamp").first()
        self.secret = cred.secret
        self.uid = cred.uid
        self.save()


class Credential(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    uid = models.IntegerField(default=0)
    secret = models.CharField(default="secret", max_length=128)
    timestamp = models.IntegerField(default=0)

    def __str__(self):
        return "Credential [{}] for {}".format(self.uid, self.chat)
