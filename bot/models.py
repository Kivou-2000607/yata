from django.db import models
from django.utils import timezone

from player.models import Player
from faction.models import Faction


# bot
class DiscordApp(models.Model):
    name = models.CharField(default="BOT_NAME", max_length=32)
    token = models.CharField(default="BOT_TOKEN", max_length=512, unique=True)
    variables = models.TextField(default="{}")
    administrators = models.TextField(default="{}")

    def __str__(self):
        return "{}".format(self.name)


# bot configuration on a guild
class Guild(models.Model):
    configuration = models.ForeignKey(DiscordApp, on_delete=models.CASCADE, help_text="Select the bot")
    guildId = models.BigIntegerField(default=0, help_text="Get the server ID from the message sent by the bot when it joined the server")
    guildName = models.CharField(default="guild_name", max_length=32, help_text="")
    guildOwnerId = models.BigIntegerField(default=0, help_text="Automatically filled by the bot")
    guildOwnerName = models.CharField(default="guild_owner", max_length=32, help_text="Automatically filled by the bot")
    guildContactId = models.IntegerField(default=0, help_text="The torn ID of the player that want the bot")
    guildContactName = models.CharField(default="guild_contact", max_length=32, help_text="The torn name of the player that want the bot")
    botContactId = models.IntegerField(default=0, help_text="Your torn ID")
    botContactName = models.CharField(default="", max_length=32, help_text="Your torn name")


    # general options
    masterKeys = models.ManyToManyField(Player, blank=True, help_text="Enter torn ID or name to find the player. If it doesn't show up it means the player is not on YATA.")
    manageChannels = models.BooleanField(default=True, help_text="The bot will create channels and roles. Better keep True at least on setup.")
    welcomeMessage = models.BooleanField(default=True, help_text="The bot sends a welcome message in the system channel.")
    welcomeMessageText = models.TextField(default="", help_text="Welcome message automatically starts with \"Welcome @member.\" Then it appends what you put here. You can put #channel and @role in plain text they'll be mentionned if they exist. If you put nothing it will just say \"Welcome @member.\"")
    systemChannel = models.CharField(default='', blank=True, max_length=32, help_text="Dummy")

    # verify module
    verifyModule = models.BooleanField(default=False, help_text="Enable the Verify module")
    verifyForce = models.BooleanField(default=False, help_text="PM players on join or not")
    verifyFactions = models.ManyToManyField(Faction, blank=True, help_text="Enter faction ID or name to find the faction. If it doesn't show up it means that the faction is not on YATA.")
    verifyFacsRole = models.CharField(default="", blank=True, max_length=16, help_text="Name of the faction role.")
    verifyAppendFacId = models.BooleanField(default=True, help_text="Append or not the ID in the faction role.")
    verifyDailyVerify = models.BooleanField(default=False, help_text="Do automatic '!verifyAll force' every 12 hours")
    verifyDailyCheck = models.BooleanField(default=False, help_text="Do automatic '!checkFactions force' every 12 hours")
    verifyChannels = models.CharField(default='["verify-id"]', blank=True, max_length=64, help_text="Name of the verify channels. Can be multiple channels. It has to be the exact channel name: [\"channel-a\", \"my-other-channel\"]")

    # stock module
    stockModule = models.BooleanField(default=False, help_text="Enable the Stock module")
    stockWSSB = models.BooleanField(default=False, help_text="Enable WSSB")
    stockTCB = models.BooleanField(default=False, help_text="Enable TCB")
    stockAlerts = models.BooleanField(default=False, help_text="Enable Alerts")
    stockChannels = models.CharField(default='["stocks"]', blank=True, max_length=64, help_text="Name of the stock alert channels. Can be multiple channels. It has to be the exact channel name: [\"channel-a\", \"my-other-channel\"]")

    # chain module
    chainModule = models.BooleanField(default=False, help_text="Enable the Chain module")
    chainChannels = models.CharField(default='["chain"]', blank=True, max_length=64, help_text="Name of the chain channels. Can be multiple channels. It has to be the exact channel name: [\"channel-a\", \"my-other-channel\"]")

    # loot module
    lootModule = models.BooleanField(default=False, help_text="Enable the Loot module")
    lootChannels = models.CharField(default='["loot"]', blank=True, max_length=64, help_text="Name of the loot channels. Can be multiple channels. It has to be the exact channel name: [\"channel-a\", \"my-other-channel\"]")

    # revive module
    reviveModule = models.BooleanField(default=False, help_text="Enable the Revive module")
    reviveChannels = models.CharField(default='["revive"]', blank=True, max_length=64, help_text="Name of the revive channels. Can be multiple channels. It has to be the exact channel name: [\"channel-a\", \"my-other-channel\"]")

    # API module
    apiModule = models.BooleanField(default=False, help_text="Enable the API module")
    apiChannels = models.CharField(default='["*"]', blank=True, max_length=64, help_text="Name of the channels where API commands are allowed. Keep [\"*\"] for all channels allowed. It has to be the exact channel name: [\"channel-a\", \"my-other-channel\"]")
    apiRoles = models.CharField(default='["*"]', blank=True, max_length=64, help_text="Name of the role allowed to use the API commands. Keep [\"*\"] for all roles allowed. It has to be the exact role name: [\"RoleA\", \"MyOtherRole\"] (no @)")

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
