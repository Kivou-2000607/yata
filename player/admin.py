from django.contrib import admin

from .models import *
from yata.handy import timestampToDate

class KeyInline(admin.TabularInline):
    model = Key
    extra = 0

class KeyAdmin(admin.ModelAdmin):
    list_display = ['player']

class PlayerAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}
    list_display = ['tId', 'name', 'botPerm', 'active', 'validKey', 'dId']
    search_fields = ['name', 'tId']
    list_filter = ['active', 'validKey']
    inlines = [KeyInline]

    def last_update(self, instance):
        return timestampToDate(instance.lastUpdateTS)

    def last_action(self, instance):
        return timestampToDate(instance.lastActionTS)


class NewsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'date', 'type', 'authorName', 'authorId', 'read']
    filter_horizontal = ('player',)


class MessageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'date', 'section', 'authorName', 'authorId']


class DonationAdmin(admin.ModelAdmin):
    list_display = ['__str__']


class PlayerDataAdmin(admin.ModelAdmin):
    list_display = ['__str__']

admin.site.register(Key, KeyAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(Donation, DonationAdmin)
admin.site.register(PlayerData, PlayerDataAdmin)
