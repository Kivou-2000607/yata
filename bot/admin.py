from django.contrib import admin

import json

from .models import *
from .functions import saveGuildConfig

admin.site.disable_action('delete_selected')

class DiscordAppAdmin(admin.ModelAdmin):
    list_display = ['name', 'pk', 'token']


def update_guild(modeladmin, request, queryset):
    for q in queryset:
        saveGuildConfig(q)

update_guild.short_description = "Push guild setup to bot configurations"

class GuildAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'configuration', 'guildContactName', 'guildContactId', 'validMasterKey', 'guildId', 'guildName']
    search_fields = ['guildContactName', 'guildName']
    list_filter = ['configuration__name', 'guildContactName', 'guildName']
    autocomplete_fields = ("masterKeys", "verifyFactions")
    actions = [update_guild]

    def validMasterKey(self, instance):
        try:
            v = json.loads(instance.configuration.variables)
            keys = v.get(str(instance.guildId), dict({})).get("keys")
            return True if len(keys) else False

        except BaseException:
            return False

    validMasterKey.boolean = True

    fieldsets = (
                ('Server and contact', {
                    'fields': ('configuration', 'guildId', 'guildName', 'guildOwnerId', 'guildOwnerName', 'guildContactId', 'guildContactName')
                }),
                ('General Settings', {
                    'fields': ('masterKeys', 'manageChannels')
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
    inlines = [CredentialInline,]


admin.site.register(Credential, CredentialAdmin)
admin.site.register(Chat, ChatAdmin)
admin.site.register(DiscordApp, DiscordAppAdmin)
admin.site.register(Guild, GuildAdmin)
