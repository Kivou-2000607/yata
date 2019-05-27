from django.contrib import admin

from .models import Player
from yata.handy import timestampToDate


class PlayerAdmin(admin.ModelAdmin):
    class Media:
        css = { 'all': ('perso/css/admin.css',) }
    list_display = ['tId', 'name', 'last_update', 'lastUpdateTS']
    search_fields = ['name', 'tId']

    def last_update(self, instance):
        return timestampToDate(instance.lastUpdateTS)

admin.site.register(Player, PlayerAdmin)
