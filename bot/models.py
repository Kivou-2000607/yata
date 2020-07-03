from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import re
import json

from player.models import Player
from faction.models import Faction

def channel_names_reg(value):
    # thanks Pyrit [2111649]
    # match = re.match(r"\[(\s*(\"([a-z])+(\-?[a-z])*\")+(\s*,|\s*\]$))+|\[\s*\]", value)
    # match = re.match(r"\[(\s*(\"(\u00a9|\u00ae|[\u2000-\u3300]|\ud83c[\ud000-\udfff]|\ud83d[\ud000-\udfff]|\ud83e[\ud000-\udfff]|[a-z])+(\-?[a-z])*\")+(\s*,|\s*\]$))+|\[\s*\]", value)
    match = re.match(r"\[\s*((\"[a-z])+(\-?[a-z_])*\"\s*,{1}\s*)*((\"[a-z])+(\-?[a-z_])*\"\s*)?\]", value)
    if match is None and value != '["*"]':
        raise ValidationError(
            _('%(value)s is not valid'),
            params={'value': value},
        )


def check_json(value):
    try:
        json.loads(value)
    except BaseException as e:
        raise ValidationError(
            _('Configuration is not valid json: %(error)s'),
            params={'error': e},
        )

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
    guildOwnerId = models.BigIntegerField(default=0, help_text="Automatically filled by the bot (automatic)")
    guildOwnerName = models.CharField(default="guild_owner", max_length=32, help_text="Automatically filled by the bot (automatic)")
    guildContactTornId = models.IntegerField(default=0, help_text="The torn ID of the player that want the bot")
    guildContactTornName = models.CharField(default="guild_contact", max_length=32, help_text="The torn name of the player that want the bot")
    guildContactDiscordId = models.BigIntegerField(default=0, help_text="The discord ID of the player that want the bot")
    guildContactDiscordName = models.CharField(default="guild_contact", max_length=32, help_text="The discord name of the player that want the bot")
    botContactId = models.IntegerField(default=0, help_text="Your torn ID")
    botContactName = models.CharField(default="", max_length=32, help_text="Your torn name")
    guildJoinedTime = models.IntegerField(default=0, help_text="Timestamp when the bot joined the guild (automatic)")

    # general options
    masterKeys = models.ManyToManyField(Player, blank=True, help_text="Enter torn ID or name to find the player. If it doesn't show up it means the player is not on YATA.")
    manageChannels = models.BooleanField(default=True, help_text="The bot will create channels and roles. Better keep True at least on setup.")
    welcomeMessage = models.BooleanField(default=True, help_text="The bot sends a welcome message in the system channel.")
    welcomeMessageText = models.TextField(default="", blank=True, help_text="Welcome message automatically starts with \"Welcome @member.\" Then it appends what you put here. You can put #channel and @role in plain text they'll be mentionned if they exist. If you put nothing it will just say \"Welcome @member.\"")
    systemChannel = models.CharField(default='', blank=True, max_length=32, help_text="Dummy")

    # verify module
    verifyModule = models.BooleanField(default=False, help_text="Enable the Verify module")
    verifyForce = models.BooleanField(default=False, help_text="PM players on join or not")
    verifyFactions = models.ManyToManyField(Faction, blank=True, help_text="Enter faction ID or name to find the faction. If it doesn't show up it means that the faction is not on YATA.")
    verifyFacsRole = models.CharField(default="", blank=True, max_length=16, help_text="Name of the faction role.")
    verifyAppendFacId = models.BooleanField(default=True, help_text="Append or not the ID in the faction role.")
    verifyDailyVerify = models.BooleanField(default=False, help_text="Do automatic '!verifyAll force' every 24 hours")
    verifyDailyCheck = models.BooleanField(default=False, help_text="Do automatic '!checkFactions force' every 24 hours")
    verifyWeeklyVerify = models.BooleanField(default=False, help_text="Do automatic '!verifyAll force' every 7x24 hours")
    verifyWeeklyCheck = models.BooleanField(default=False, help_text="Do automatic '!checkFactions force' every 7x24 hours")
    verifyChannels = models.CharField(default='["verify-id"]', blank=True, max_length=64, help_text="Name of the verify channels. Can be multiple channels. It has to be the exact channel name: [\"channel-a\", \"my-other-channel\"]", validators=[channel_names_reg])

    # stock module
    stockModule = models.BooleanField(default=False, help_text="Enable the Stock module")
    stockWSSB = models.BooleanField(default=False, help_text="Enable WSSB")
    stockTCB = models.BooleanField(default=False, help_text="Enable TCB")
    stockAlerts = models.BooleanField(default=False, help_text="Enable Alerts")
    stockChannels = models.CharField(default='["stocks"]', blank=True, max_length=64, help_text="Name of the stock alert channels. Can be multiple channels. It has to be the exact channel name: [\"channel-a\", \"my-other-channel\"]", validators=[channel_names_reg])

    # chain module
    chainModule = models.BooleanField(default=False, help_text="Enable the Chain module")
    chainChannels = models.CharField(default='["chain"]', blank=True, max_length=64, help_text="Name of the chain channels. Can be multiple channels. It has to be the exact channel name: [\"channel-a\", \"my-other-channel\"]", validators=[channel_names_reg])

    # racket module
    racketModule = models.BooleanField(default=False, help_text="Enable the Racket module")
    racketChannels = models.CharField(default='["territory"]', blank=True, max_length=64, help_text="Name of the racket channels. Can be multiple channels. It has to be the exact channel name: [\"channel-a\", \"my-other-channel\"]", validators=[channel_names_reg])
    racketRoles = models.CharField(default='[]', blank=True, max_length=64, help_text="Name of the role to mention. It has to be the exact role name: [\"Role a\"] or empty array [] for no mentions.")

    # loot module
    lootModule = models.BooleanField(default=False, help_text="Enable the Loot module")
    lootChannels = models.CharField(default='["loot"]', blank=True, max_length=64, help_text="Name of the loot channels. Can be multiple channels. It has to be the exact channel name: [\"channel-a\", \"my-other-channel\"]", validators=[channel_names_reg])

    # revive module
    reviveModule = models.BooleanField(default=False, help_text="Enable the Revive module")
    reviveChannels = models.CharField(default='["revive"]', blank=True, max_length=64, help_text="Name of the revive channels. Can be multiple channels. It has to be the exact channel name: [\"channel-a\", \"my-other-channel\"]", validators=[channel_names_reg])

    # API module
    apiModule = models.BooleanField(default=False, help_text="Enable the API module")
    apiChannels = models.CharField(default='["*"]', blank=True, max_length=64, help_text="Name of the channels where API commands are allowed. Keep [\"*\"] for all channels allowed. It has to be the exact channel name: [\"channel-a\", \"my-other-channel\"]", validators=[channel_names_reg])
    apiRoles = models.CharField(default='["*"]', blank=True, max_length=64, help_text="Name of the role allowed to use the API commands. Keep [\"*\"] for all roles allowed. It has to be the exact role name: [\"RoleA\", \"MyOtherRole\"] (no @)")

    # Crimes module
    crimesModule = models.BooleanField(default=False, help_text="Enable Crimes module")
    crimesChannels = models.CharField(default='["oc"]', blank=True, max_length=64, help_text="Name of the channels where OC commands are allowed. Keep [\"*\"] for all channels allowed. It has to be the exact channel name: [\"channel-a\", \"my-other-channel\"]", validators=[channel_names_reg])

    # verify repository
    # repoModule = models.BooleanField(default=False)
    # repoName = models.CharField(default="repo_token", max_length=64)
    # repoToken = models.CharField(default="repo_name", max_length=32)

    def __str__(self):
        return "{} on {} [{}]".format(self.configuration, self.guildName, self.guildId)


class Bot(models.Model):
    name = models.CharField(default="Default Name", max_length=32)
    token = models.CharField(default="Default Token", max_length=512, unique=True)
    administrators = models.TextField(default="{}")

    def __str__(self):
        return "{}".format(self.name)


class Server(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, help_text="Select the bot")
    discord_id = models.BigIntegerField(default=0, help_text="Discrod server id")
    name = models.CharField(default="Default name", max_length=64, help_text="Discord server name")
    configuration = models.TextField(default='{}', help_text="Server name configuration (json)", validators=[check_json])
    server_admin = models.ManyToManyField(Player, blank=True, help_text="Enter torn ID or name to find the player. If it doesn't show up it means the player is not on YATA.")

    def __str__(self):
        return 'Server {}'.format(self.id)

    def get_prefixes(self):
        return

    def get_channels(self):
        return {k: v for k, v in json.loads(self.configuration).get("admin", {}).get("channels", {}).items()}

    def get_roles(self):
        return {k: v for k, v in json.loads(self.configuration).get("admin", {}).get("roles", {}).items() if v not in ["@everyone"]}

    def get_admin(self):
        from_db = json.loads(self.configuration).get("admin", {})
        admins = [f'{v["name"]} [{v["torn_id"]}] ({k})' for k, v in from_db.get("server_admins", {}).items()]
        if from_db.get("guild_id") is not None:
            for_template = {
                "server_info": [["Server name", from_db.get("guild_name")],
                                ["Server name", from_db.get("guild_name")],
                                ["Server discord ID", from_db.get("guild_id")],
                                ["Server owner name", from_db.get("owner_dname")],
                                ["Server owner discord ID", from_db.get("owner_did")],
                                ["Server admins", ", ".join(admins)]],
                "prefix": {"type": "prefix", "all": {'!': '!', '.': '.', '>': '>', '<': '<', '$': '$', '-': '-', '_': '_', '?': '?', '#': '#'}, "selected": from_db.get("prefix", "!"), "prefix": "", "title": "Bot prefix", "help": "Select the bot prefix", "mandatory": False},
                "channel_admin": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channel_admin", {}), "prefix": "#", "title": "Admin channel for the bot", "help": "Select one channel for administration purposes", "mandatory": True},
            }
            return for_template
        else:
            return False

    def get_racket(self):
        from_db = json.loads(self.configuration).get("rackets", False)
        if from_db:
            for_template = {
                "channels_alerts": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_alerts", {}), "prefix": "#", "title": "Channel for the alerts", "help": "Select one channel for the alerts", "mandatory": True},
                "roles_alerts": {"type": "role", "all": self.get_roles(), "selected": from_db.get("roles_alerts", {}), "prefix": "@", "title": "Role for the alerts", "help": "Select one role for the alerts", "mandatory": False},
                # ["roles_alerts", self.get_roles(), from_db.get("roles_alerts", {}), "@", "Role for the alerts"],
            }
            return for_template
        else:
            return False

    def get_loot(self):
        from_db = json.loads(self.configuration).get("loot", False)
        if from_db:
            for_template = {
                "channels_allowed": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_allowed", {}), "prefix": "#", "title": "Allowed channels for the comand", "help": "Select one or several channels for the <tt>!loot</tt> commands", "mandatory": True},
                "channels_alerts": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_alerts", {}), "prefix": "#", "title": "Channel for the alerts", "help": "Select one channel for the alerts", "mandatory": True},
                "roles_alerts": {"type": "role", "all": self.get_roles(), "selected": from_db.get("roles_alerts", {}), "prefix": "@", "title": "Role for the alerts", "help": "Select one role for the alerts", "mandatory": False},
            }
            return for_template
        else:
            return False




class Chat(models.Model):
    name = models.CharField(default="secret", max_length=128)
    uid = models.IntegerField(default=0)
    secret = models.CharField(default="secret", max_length=128)
    check = models.CharField(default="check", max_length=128)
    hookurl = models.TextField(default="{}")

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


class Rackets(models.Model):
    timestamp = models.IntegerField(default=0)
    rackets = models.TextField(default="{}")
