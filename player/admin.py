from django.contrib import admin

from .models import Player
from yata.handy import timestampToDate


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'last_update']

    def report(self, instance):
        return instance.report

    def last_update(self, instance):
        return timestampToDate(instance.lastUpdateTS)

admin.site.register(Player, PlayerAdmin)
