from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator

import re
import json

from player.models import Player
from faction.models import Faction

NPCS = [(4, "Duke"), (10, "Scrooge"), (15, "Leslie"), (17, "Easter Bunny"), (19, "Jimmy"), (20, "Fernando"), (21, "Tiny")]

def check_json(value):
    try:
        json.loads(value)
    except BaseException as e:
        raise ValidationError(
            _('Configuration is not valid json: %(error)s'),
            params={'error': e},
        )


class Bot(models.Model):
    name = models.CharField(default="Default Name", max_length=32)
    token = models.CharField(default="Default Token", max_length=512, unique=True)
    number_of_servers = models.IntegerField(default=0, help_text="Number of servers")

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

    def get_admins(self):
        return [v for k, v in json.loads(self.configuration).get("admin", {}).get("server_admins", {}).items()]

    def get_channels(self):
        return {k: v for k, v in json.loads(self.configuration).get("admin", {}).get("channels", {}).items()}

    def get_roles(self):
        return {k: v for k, v in json.loads(self.configuration).get("admin", {}).get("roles", {}).items() if v not in ["@everyone"]}
        #return {k: v for k, v in json.loads(self.configuration).get("admin", {}).get("roles", {}).items()}

    def get_admin(self):
        from_db = json.loads(self.configuration).get("admin", {})
        admins = [f'{v["name"]} [{v["torn_id"]}] ({k})' for k, v in from_db.get("server_admins", {}).items()]
        if from_db.get("guild_id") is not None:
            for_template = {
                "server_info": [["Server name", from_db.get("guild_name"), False],
                                ["Server discord ID", from_db.get("guild_id"), False],
                                ["Server owner name", from_db.get("owner_dname"), False],
                                ["Server owner discord ID", from_db.get("owner_did"), False],
                                ["Server secret", from_db.get("secret"), "Read only access to the dashboard:&#10http://yata.yt/bot/dashboard/" + str(from_db.get("secret"))],
                                ["Server admins", ", ".join(admins), "When needed the admins API keys will be used.&#10You can ask an @Helper to change this list."]],
                "prefix": {"type": "prefix", "all": {'!': '!', '.': '.', '>': '>', '<': '<', '$': '$', '-': '-', '_': '_', '?': '?', '#': '#'}, "selected": from_db.get("prefix", "!"), "prefix": "", "title": "Bot prefix", "help": "Select the bot prefix", "mandatory": False},
                "channels_admin": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_admin", {}), "prefix": "#", "title": "Admin channel for the bot", "help": "Select one channel for administration purposes", "tooltip": "Errors will be sent to this channel along with potential messages from me.", "mandatory": True},
                "message_welcome": {"type": "message", "selected": from_db.get("message_welcome", {}), "prefix": "", "title": "Welcome message", "help": "Type your welcome message", "tooltip": "Use \\n for a newline, # before a channel, @ before a role (use `_` instead of spaces) and @new_member to ping new members&#10If left empty no messages will be sent.", "mandatory": False},
                "channels_welcome": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_welcome", {}), "prefix": "#", "title": "Welcome channel", "help": "Select one channel for the welcome messages", "tooltip": "If none selected, the default server channel will be used.", "mandatory": False},
                "other": {"type": "bool", "all": ["beta"], "selected": from_db.get("other", []), "title": "Other settings", "prefix": "", "help": "Beta: Select it if you want to use the latest untested features.", "tooltip": "Don't complain if it doesn't work ^^", "mandatory": False},
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

    def get_elim(self):
        from_db = json.loads(self.configuration).get("elim", False)
        all_teams = ["victorious-secret", "short-bus", "sea-men", "pandemic", "dongs", "snowflakes", "illuminati", "keyboard-warriors", "lettuce-win", "chicken-nuggets", "cereal-killers", "goat"]
        if from_db:
            for_template = {
                "team_name": {"type": "bool", "all": all_teams, "selected": from_db.get("team_name", []), "title": "Server team", "prefix": "", "help": "Select your server's team", "mandatory": False},
                "roles_team": {"type": "role", "all": self.get_roles(), "selected": from_db.get("roles_team", {}), "prefix": "@", "title": "Team role", "help": "Select one role for your team", "mandatory": False},
                "channels_scores": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_scores", {}), "prefix": "#", "title": "Channel for the scores", "help": "Select one channel to display the current scores", "mandatory": False},
            }
            return for_template
        else:
            return False

    def get_war(self):
        from_db = json.loads(self.configuration).get("wars", False)
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
                "channels_allowed": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_allowed", {}), "prefix": "#", "title": "Allowed channels for the command", "help": "Select one or several channels for the <tt>!loot</tt> commands", "mandatory": True},
                "roles_alerts": {"type": "role", "all": self.get_roles(), "selected": from_db.get(f"roles_alerts"), "prefix": "@", "title": f"Generic role", "help": f"Select one role for the <tt>!assign loot</tt> command", "mandatory": False}
            }
            for i, v in NPCS:
                for_template[f"channels_alerts_{i}"] = {"type": "channel", "all": self.get_channels(), "selected": from_db.get(f"channels_alerts_{i}", {}), "prefix": "#", "title": f"Channel for {v} alerts", "help": f"Select one channel for the {v} alerts", "mandatory": True}
                if for_template[f"channels_alerts_{i}"]["selected"]:
                    for_template[f"roles_alerts_{i}"] = {"type": "role", "all": self.get_roles(), "selected": from_db.get(f"roles_alerts_{i}"), "prefix": "@", "title": f"Role for the {v} alerts", "help": f"Select one role for the {v} alerts", "mandatory": False}
                    for_template[f"loot_level_{i}"] = {"type": "bool", "all": ["level_1", "level_2", "level_3", "level_4", "level_5"], "selected": from_db.get(f"loot_level_{i}", []), "title": f"Loot level for {v}", "prefix": "", "help": "Send alerts for these loot levels.", "mandatory": True}

            return for_template
        else:
            return False

    def get_stocks(self):
        from_db = json.loads(self.configuration).get("stocks", False)
        if from_db:
            for_template = {
                "channels_alerts": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_alerts", {}), "prefix": "#", "title": "Channel for the alerts", "help": "Select one channel for the alerts", "mandatory": False},
                "roles_alerts": {"type": "role", "all": self.get_roles(), "selected": from_db.get("roles_alerts", {}), "prefix": "@", "title": "Role for the alerts", "help": "Select one role for the alerts", "mandatory": False},
                "channels_wssb": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_wssb", {}), "prefix": "#", "title": "WSSB channel", "help": "Select one channel for the <tt>!wssb</tt> commands", "mandatory": True},
                "roles_wssb": {"type": "role", "all": self.get_roles(), "selected": from_db.get("roles_wssb", {}), "prefix": "@", "title": "WSSB role", "help": "Select one role for the alerts", "mandatory": True},
                "channels_tcb": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_tcb", {}), "prefix": "#", "title": "TCB channel", "help": "Select one channel for the <tt>!wssb</tt> commands", "mandatory": True},
                "roles_tcb": {"type": "role", "all": self.get_roles(), "selected": from_db.get("roles_tcb", {}), "prefix": "@", "title": "TCB role", "help": "Select one role for the alerts", "mandatory": True},
            }
            return for_template
        else:
            return False

    def get_revive(self, page=None):

        def get_revive_public(s):
            return json.loads(s.configuration).get("revive", {}).get("other", {}).get("public")

        def get_revive_freevive(s):
            return json.loads(s.configuration).get("revive", {}).get("other", {}).get("freevive")

        def get_revive_sending(s):
            return json.loads(s.configuration).get("revive", {}).get("sending", {})

        from_db = json.loads(self.configuration).get("revive", False)
        all = [{"server_id": str(s.discord_id), "server_name": s.name, "freevive": get_revive_freevive(s), "public": get_revive_public(s), "admins": s.get_admins(), "sending": get_revive_sending(s)} for s in Server.objects.filter(bot=self.bot).order_by("name") if len(json.loads(s.configuration).get('revive', {}).get('channels_alerts', {})) and s != self]

        all = Paginator(all, 25).get_page(page)

        if from_db:
            for_template = {
                "channels_allowed": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_allowed", {}), "prefix": "#", "title": "Allowed channels for the command", "help": "Select one or several channels for the <tt>!revive</tt> commands", "mandatory": True},
                "channels_alerts": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_alerts", {}), "prefix": "#", "title": "Channel for the alerts", "help": "Select one channel for the alerts", "tooltip": "You will receive the calls from your server and from the other servers in this channel (it can be the same as one of the allowed channels).", "mandatory": True},
                "roles_alerts": {"type": "role", "all": self.get_roles(), "selected": from_db.get("roles_alerts", {}), "prefix": "@", "title": "Role for the alerts", "help": "Select one role for the alerts", "mandatory": False},
                "revive_servers": {"type": "server", "all": all, "sending": from_db.get("sending", {}), "blacklist": from_db.get("blacklist", {}), "title": "Linked servers", "tooltip": "send: the bot will send your calls to the servers you select&#10blacklist: the bot will block incoming calls from the servers you select&#10&#10If the server is not public please contact the admins before sending them your calls", "help": "Select the servers the bot will be sending the messages to", "mandatory": False},
                "other": {"type": "bool", "all": ["public", "freevive", "delete"], "selected": from_db.get("other", []), "title": "Other settings", "prefix": "", "help": "Delete: delete revive calls after 5 minutes. Freevive: accept freevive calls. Public: state to others that you accept their calls", "mandatory": False},
            }
            return for_template
        else:
            return False

    def get_verify(self):
        from_db = json.loads(self.configuration).get("verify", False)
        all = ["daily_check", "weekly_check", "daily_verify", "weekly_verify", "force_verify", "tag", "disable_id"]
        if from_db:
            for_template = {
                "channels_allowed": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_allowed", {}), "prefix": "#", "title": "Allowed channels for the commands", "help": "Select one or several channels for the <tt>!verify</tt> commands", "mandatory": True},
                "channels_welcome": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_welcome", {}), "prefix": "#", "title": "Welcome channel", "help": "Select one channel for the verified welcome message", "tooltip": "If none selected, no messages will be sent.", "mandatory": False},
                "roles_verified": {"type": "role", "all": self.get_roles(), "selected": from_db.get("roles_verified", {}), "prefix": "@", "title": "Role for the verified members", "help": "Select one role for the verified players", "tooltip": "This role will be attributed the the player if the verification is successful (whatever the faction it belongs to).", "mandatory": True},
                "factions": {"type": "role", "selected": from_db.get("factions", {}), "positions": from_db.get("positions", {}), "title": "Factions roles", "prefix": "@", "help": "Select factions and roles for each of them", "tooltip": "Additional roles can be attributed to members on verification depending on their faction.&#10You can choose as many factions as you want and linked them to as many roles as you want.&#10You can remove a role from the configuration by selecting the same faction and the same role (toggle).", "mandatory": False},
                "other": {"type": "bool", "all": all, "selected": from_db.get("other", []), "title": "Other options", "prefix": "", "help": "Select the different other options", "tooltip": "check: !checkFactions&#10verify: !verifyAll&#10force: sends a pm when a member joins and is not verified&#10tag: enable the !tag command&#10disable id: does not append torn ID in the nickname (not recommanded)", "mandatory": False},
                # ["roles_alerts", self.get_roles(), from_db.get("roles_alerts", {}), "@", "Role for the alerts"],
            }
            return for_template
        else:
            return False

    def get_oc(self):
        from_db = json.loads(self.configuration).get("oc", False)
        all = { "1": "Blackmailing", "2": "Kidnapping", "3": "Bomb threat", "4": "Planned robbery", "5": "Robbing of a money train", "6": "Taking over a cruise liner", "7": "Plane hijacking", "8": "Political Assassination"}
        if from_db:
            for_template = {
                "channels_allowed": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_allowed", {}), "prefix": "#", "title": "Allowed channels for the commands", "help": "Select one or several channels for the OC module commands", "tooltip": "The notifications will be in the same channel you typed !oc.", "mandatory": True},
                "currents": {"type": "oc", "all": from_db.get("currents", {}), "title": "Current OC tracking", "prefix": "", "help": "List of the current trackings", "tooltip": "This is an overview of the current !oc. If for some reason you need it, you can stop them here (don't forget to !sync)", "mandatory": False},
                "notifications": {"type": "oc", "all": all, "selected": from_db.get("notifications", {}), "title": "Notifications", "prefix": "", "help": "Select the OC types you want to be notified", "tooltip": "The other ones will be displayed but you will not get pinged", "mandatory": False},
            }
            return for_template
        else:
            return False

    def get_chain(self):
        from_db = json.loads(self.configuration).get("chain", False)
        if from_db:
            for_template = {
                "channels_allowed": {"type": "channel", "all": self.get_channels(), "selected": from_db.get("channels_allowed", {}), "prefix": "#", "title": "Allowed channels for the commands", "help": "Select one or several channels for the chain module commands", "tooltip": "The notifications will be in the same channel you typed !retal.", "mandatory": True},
                "currents": {"type": "retal", "all": from_db.get("currents", {}), "title": "Current retals tracking", "tooltip": "This is an overview of the current !retal. If for some reason you need it, you can stop them here (don't forget to !sync)", "prefix": "", "help": "List of the current trackings", "mandatory": False},
                "chains": {"type": "chain", "all": from_db.get("chains", {}), "title": "Current chains tracking", "tooltip": "This is an overview of the current !chain. If for some reason you need it, you can stop them here (don't forget to !sync)", "prefix": "", "help": "List of the current trackings", "mandatory": False},
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


# class Chat(models.Model):
#     name = models.CharField(default="secret", max_length=128)
#     uid = models.IntegerField(default=0)
#     secret = models.CharField(default="secret", max_length=128)
#     check = models.CharField(default="check", max_length=128)
#     hookurl = models.TextField(default="{}")
#
#     def __str__(self):
#         return "Chat {}".format(self.name)
#
#     def setNewestSecret(self):
#         cred = self.credential_set.all().order_by("-timestamp").first()
#         self.secret = cred.secret
#         self.uid = cred.uid
#         self.save()


# class Credential(models.Model):
#     chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
#     uid = models.IntegerField(default=0)
#     secret = models.CharField(default="secret", max_length=128)
#     timestamp = models.IntegerField(default=0)
#
#     def __str__(self):
#         return "Credential [{}] for {}".format(self.uid, self.chat)


class Rackets(models.Model):
    timestamp = models.IntegerField(default=0)
    rackets = models.TextField(default="{}")


class Wars(models.Model):
    timestamp = models.IntegerField(default=0)
    wars = models.TextField(default="{}")


class Stocks(models.Model):
    timestamp = models.IntegerField(default=0)
    rackets = models.TextField(default="{}")

# needed for past migrations...
def channel_names_reg():
    return None
