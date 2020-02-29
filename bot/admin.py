from django.contrib import admin
from django.utils.html import format_html

import json

from .models import *
from .functions import saveGuildConfig

# admin.site.disable_action('delete_selected')


class DiscordAppAdmin(admin.ModelAdmin):
    list_display = ['name', 'pk', 'token']


def update_guild(modeladmin, request, queryset):
    for q in queryset:
        saveGuildConfig(q)


update_guild.short_description = "Push guild setup to bot configuration"


class GuildAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}

    list_display = ['guildName', 'configuration', 'admin', 'contact', 'owner', 'key', 'verifyModule', 'stockModule', 'lootModule', 'chainModule', 'reviveModule', 'apiModule']
    search_fields = ['guildContactName', 'guildName', 'botContactName']
    list_filter = ['configuration__name', 'botContactName', 'guildContactName']
    autocomplete_fields = ("masterKeys", "verifyFactions")
    actions = [update_guild]

    def key(self, instance):
        v = json.loads(instance.configuration.variables)
        keys = v.get(str(instance.guildId), dict({})).get("keys", [])
        return len(keys)

    def owner(self, instance):
        return '{name} [{id}]'.format(name=instance.guildOwnerName, id=instance.guildOwnerId)

    def contact(self, instance):
        return format_html('<a href="https://www.torn.com/profiles.php?XID={id}" target="_blank">{name} [{id}]</a>'.format(name=instance.guildContactName, id=instance.guildContactId))

    def admin(self, instance):
        return format_html('<a href="https://www.torn.com/profiles.php?XID={id}" target="_blank">{name} [{id}]</a>'.format(name=instance.botContactName, id=instance.botContactId))

    fieldsets = (
                ('Server and contact', {
                    'fields': ('botContactName', 'botContactId', 'configuration', 'guildId', 'guildName', 'guildContactId', 'guildContactName')
                }),
        ('General Settings', {
            'fields': ('masterKeys', 'manageChannels', 'welcomeMessage', 'welcomeMessageText')
        }),
        ('Verify module', {
            'fields': ('verifyModule', 'verifyChannels', 'verifyForce', 'verifyFactions', 'verifyFacsRole', 'verifyAppendFacId', 'verifyDailyVerify', 'verifyDailyCheck')
        }),
        ('Stock module', {
            'fields': ('stockModule', 'stockChannels', 'stockWSSB', 'stockTCB', 'stockAlerts')
        }),
        ('Revive module', {
            'fields': ('reviveModule', 'reviveChannels')
        }),
        ('Loot module', {
            'fields': ('lootModule', 'lootChannels')
        }),
        ('Chain module', {
            'fields': ('chainModule', 'chainChannels')
        }),
        ('API module', {
            'fields': ('apiModule', 'apiChannels', 'apiRoles')
        }),
    )


class CredentialInline(admin.TabularInline):
    model = Credential
    extra = 0
    show_change_link = True
    can_delete = True
    readonly_fields = ('uid', 'secret', 'timestamp',)


class CredentialAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'uid', 'timestamp']
    list_filter = ['chat__name']


class ChatAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'name', 'uid']
    inlines = [CredentialInline, ]


admin.site.register(Credential, CredentialAdmin)
admin.site.register(Chat, ChatAdmin)
admin.site.register(DiscordApp, DiscordAppAdmin)
admin.site.register(Guild, GuildAdmin)
