from django.contrib import admin

from .models import Player
from .models import News
from yata.handy import timestampToDate


class PlayerAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}
    list_display = ['tId', 'name', 'last_action', 'lastActionTS', 'last_update', 'lastUpdateTS']
    search_fields = ['name', 'tId']

    def last_update(self, instance):
        return timestampToDate(instance.lastUpdateTS)

    def last_action(self, instance):
        return timestampToDate(instance.lastActionTS)


admin.site.register(Player, PlayerAdmin)


class NewsAdmin(admin.ModelAdmin):
    list_display = ['pk', 'date', 'type', 'timestamp']
    search_fields = ['name', 'tId']

    def date(self, instance):
        return timestampToDate(instance.timestamp)


admin.site.register(News, NewsAdmin)
