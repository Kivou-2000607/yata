from django.contrib import admin

from .models import DiscordApp
from .models import Guild


class DiscordAppAdmin(admin.ModelAdmin):
    list_display = ['name', 'pk', 'token']


admin.site.register(DiscordApp, DiscordAppAdmin)


class GuildAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    raw_id_fields = ("masterKeys", "verifyFactions")


admin.site.register(Guild, GuildAdmin)
