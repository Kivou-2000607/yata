from django.contrib import admin

from .models import *


class DiscordAppAdmin(admin.ModelAdmin):
    list_display = ['name', 'pk', 'token']


class GuildAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'guildContactName', 'guildContactId']
    search_fields = ['guildContactName', 'guildContactId']
    list_filter = ['guildContactName',]
    autocomplete_fields = ("masterKeys", "verifyFactions")


class ChatAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'name', 'uid']


admin.site.register(Chat, ChatAdmin)
admin.site.register(DiscordApp, DiscordAppAdmin)
admin.site.register(Guild, GuildAdmin)
