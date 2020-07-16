from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator

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
    secret = models.CharField(default="x", max_length=16, help_text="Secret key to access read only configurations")

    def __str__(self):
        return '{} on bot {}'.format(self.bot, self.name)

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
                "server_info": [["Server name", from_db.get("guild_name"), False],
                                ["Server discord ID", from_db.get("guild_id"), False],
                                ["Server owner name", from_db.get("owner_dname"), False],
                                ["Server owner discord ID", from_db.get("owner_did"), False],
                                ["Server secret", from_db.get("secret"), "Read only access to the dashboard:&#10http://yata.alwaysdata.net/bot/dashboard/" + str(from_db.get("secret"))],
                                ["Server admins", ", ".join(admins), "When needed the admins API keys will be used.&#10You can ask an @Helper to change this list."]],
                "prefix": {"type": "prefix", "all": {'!': '!', '.': '.', '>': '>', '<': '<', '$': '$', '-': '-', '_': '_', '?': '?', '#': '#'}, "selected": from_db.get("prefix", "!"), "prefix": "", "title": "Bot prefix", "help": "Select the bot prefix", "mandatory": False},
                "channels_admin": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_admin", {}), "prefix": "#", "title": "Admin channel for the bot", "help": "Select one channel for administration purposes", "tooltip": "Errors will be sent to this channel along with potential messages from me.", "mandatory": True},
                "message_welcome": {"type": "message", "selected": from_db.get("message_welcome", {}), "prefix": "", "title": "Welcome message", "help": "Type your welcome message", "tooltip": "Use \\n for a newline, # before a channel, @ before a role and @new_member to ping new members&#10If left empty no messages will be sent.", "mandatory": False},
                "channels_welcome": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_welcome", {}), "prefix": "#", "title": "Welcome channel", "help": "Select one channel for the welcome messages", "tooltip": "If none selected, the default server channel will be used.", "mandatory": False},
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

    def get_stocks(self):
        from_db = json.loads(self.configuration).get("stocks", False)
        if from_db:
            for_template = {
                "channels_alerts": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_alerts", {}), "prefix": "#", "title": "Channel for the alerts", "help": "Select one channel for the alerts", "mandatory": False},
                "roles_alerts": {"type": "role", "all": self.get_roles(), "selected": from_db.get("roles_alerts", {}), "prefix": "@", "title": "Role for the alerts", "help": "Select one role for the alerts", "mandatory": False},
                "channels_wssb": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_wssb", {}), "prefix": "#", "title": "WSSB channel", "help": "Select one or several channels for the <tt>!wssb</tt> commands", "mandatory": True},
                "roles_wssb": {"type": "role", "all": self.get_roles(), "selected": from_db.get("roles_wssb", {}), "prefix": "@", "title": "WSSB role", "help": "Select one role for the alerts", "mandatory": True},
                "channels_tcb": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_tcb", {}), "prefix": "#", "title": "TCB channel", "help": "Select one or several channels for the <tt>!wssb</tt> commands", "mandatory": True},
                "roles_tcb": {"type": "role", "all": self.get_roles(), "selected": from_db.get("roles_tcb", {}), "prefix": "@", "title": "TCB role", "help": "Select one role for the alerts", "mandatory": True},
            }
            return for_template
        else:
            return False

    def get_revive(self, page=None):
        from_db = json.loads(self.configuration).get("revive", False)
        all = [{"server_id": str(s.discord_id), "server_name": s.name} for s in Server.objects.filter(bot=self.bot) if len(json.loads(s.configuration).get('revive', {}).get('channels_alerts', {})) and s != self]
        all = Paginator(all, 25).get_page(page)

        if from_db:
            for_template = {
                "channels_allowed": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_allowed", {}), "prefix": "#", "title": "Allowed channels for the comand", "help": "Select one or several channels for the <tt>!revive</tt> commands", "mandatory": True},
                "channels_alerts": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_alerts", {}), "prefix": "#", "title": "Channel for the alerts", "help": "Select one channel for the alerts", "tooltip": "You will receive the calls from your server and from the other servers in this channel (it can be the same as one of the allowed channels).", "mandatory": True},
                "roles_alerts": {"type": "role", "all": self.get_roles(), "selected": from_db.get("roles_alerts", {}), "prefix": "@", "title": "Role for the alerts", "help": "Select one role for the alerts", "mandatory": False},
                "revive_servers": {"type": "server", "all": all, "sending": from_db.get("sending", {}), "blacklist": from_db.get("blacklist", {}), "title": "Linked servers", "tooltip": "send: the bot will send your calls to the servers you select.&#10blacklist: the bot will block incoming calls from the servers you select.", "help": "Select the servers the bot will be sending the messages to", "mandatory": False}
            }
            return for_template
        else:
            return False

    def get_verify(self):
        from_db = json.loads(self.configuration).get("verify", False)
        all = ["daily_check", "weekly_check", "daily_verify", "weekly_verify", "force_verify"]
        if from_db:
            for_template = {
                "channels_allowed": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_allowed", {}), "prefix": "#", "title": "Allowed channels for the comands", "help": "Select one or several channels for the <tt>!verify</tt> commands", "mandatory": True},
                "channels_welcome": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_welcome", {}), "prefix": "#", "title": "Welcome channel", "help": "Select one channel for the verified welcome message", "tooltip": "If none selected, no messages will be sent.", "mandatory": False},
                "roles_verified": {"type": "role", "all": self.get_roles(), "selected": from_db.get("roles_verified", {}), "prefix": "@", "title": "Role for the verified members", "help": "Select one role for the verified members", "tooltip": "This role will be attributed the the member if the verification is successful.", "mandatory": True},
                "factions": {"type": "role", "selected": from_db.get("factions", {}), "title": "Factions roles", "prefix": "@", "help": "Select factions and roles for each of them", "tooltip": "Additional roles can be attributed to members on verification depending on their faction.&#10You can choose as many factions as you want and linked them to as many roles as you want.&#10You can remove a role from the configuration by selecting the same faction and the same role (toggle).", "mandatory": False},
                "other": {"type": "bool", "all": all, "selected": from_db.get("other", []), "title": "Other options", "prefix": "", "help": "Select the different other options", "tooltip": "check: !checkFactions&#10verify: !verifyAll&#10force: sends a pm when a member joins and is not verified", "mandatory": False},
                # ["roles_alerts", self.get_roles(), from_db.get("roles_alerts", {}), "@", "Role for the alerts"],
            }
            return for_template
        else:
            return False

    def get_oc(self):
        from_db = json.loads(self.configuration).get("oc", False)
        if from_db:
            for_template = {
                "channels_allowed": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_allowed", {}), "prefix": "#", "title": "Allowed channels for the comands", "help": "Select one or several channels for the OC module commands", "tooltip": "The notifications will be in the same channel you typed !oc.", "mandatory": True},
                "currents": {"type": "oc", "all": from_db.get("currents", {}), "title": "Current OC tracking", "prefix": "", "help": "List of the current trackings", "tooltip": "This is an overview of the current !oc. If for some reason you need it, you can stop them here (don't forget to !sync)", "mandatory": False},
            }
            return for_template
        else:
            return False

    def get_chain(self):
        from_db = json.loads(self.configuration).get("chain", False)
        if from_db:
            for_template = {
                "channels_allowed": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_allowed", {}), "prefix": "#", "title": "Allowed channels for the comands", "help": "Select one or several channels for the chain module commands", "tooltip": "The notifications will be in the same channel you typed !retal.", "mandatory": True},
                "currents": {"type": "retal", "all": from_db.get("currents", {}), "title": "Current retals tracking", "tooltip": "This is an overview of the current !retal. If for some reason you need it, you can stop them here (don't forget to !sync)", "prefix": "", "help": "List of the current trackings", "mandatory": False},
            }
            return for_template
        else:
            return False

    # def light_configuration(self):
    #     configuration = json.loads(self.configuration)
    #     for k, v in configuration.get("chain", {}).get("current", {}).items():
    #         del v["torn_user"]
    #
    #     for k, v in configuration.get("oc", {}).get("current", {}).items():
    #         del v["torn_user"]
    #
    #     return json.dumps(configuration)


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

class Stocks(models.Model):
    timestamp = models.IntegerField(default=0)
    rackets = models.TextField(default="{}")
