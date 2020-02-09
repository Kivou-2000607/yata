from django.contrib import admin

from .models import *


class DiscordAppAdmin(admin.ModelAdmin):
    list_display = ['name', 'pk', 'token']


class GuildAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'guildContactName', 'guildContactId']
    search_fields = ['guildContactName', 'guildContactId']
    list_filter = ['guildContactName']
    autocomplete_fields = ("masterKeys", "verifyFactions")

    fieldsets = (
                ('Server and contact', {
                    'fields': ('configuration', 'guildId', 'guildName', 'guildOwnerId', 'guildOwnerName', 'guildContactId', 'guildContactName')
                }),
                ('General Settings', {
                    'fields': ('masterKeys', 'manageChannels')
                }),
                ('Verify module', {
                    'fields': ('verifyModule', 'verifyForce', 'verifyFactions', 'verifyFacsRole', 'verifyAppendFacId', 'verifyDailyVerify', 'verifyDailyCheck')
                }),
                ('Stock module', {
                    'fields': ('stockModule', 'stockWSSB', 'stockTCB', 'stockAlerts', 'stockChannel')
                }),
                ('Other module', {
                    'fields': ('chainModule', 'lootModule', 'reviveModule',)
                }),
                ('API module', {
                    'fields': ('allowedChannels', 'allowedRoles')
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
