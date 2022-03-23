from django.contrib import admin
from django.core.cache import cache

from .models import *
from faction.models import Faction
from yata.handy import timestampToDate


class KeyInline(admin.TabularInline):
    model = Key
    extra = 0


class KeyAdmin(admin.ModelAdmin):
    list_display = ['player', 'useFact', 'useSelf', 'access_type']
    list_filter = ['access_type',]
    search_fields = ['player__name', 'tId']
    readonly_fields = ['player', ]


class PlayerAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('yata/css/admin.css',)}

    list_display = ['tId', 'name', 'active', 'validKey', 'key_level', 'key_last_code']
    search_fields = ['name', 'tId']
    list_filter = ['active', 'validKey', 'key_level', 'key_last_code']
    inlines = [KeyInline]
    exclude = ['apikey', 'awardsJson', 'stocksJson']

    def last_update(self, instance):
        return timestampToDate(instance.lastUpdateTS)

    def last_action(self, instance):
        return timestampToDate(instance.lastActionTS)


def clear_message_cache(modeladmin, request, queryset):
    cache.delete("context_processor_message")

class MessageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'section', 'level', 'message']
    actions = [clear_message_cache]

class DonationAdmin(admin.ModelAdmin):
    list_display = ['__str__']

class PlayerDataAdmin(admin.ModelAdmin):
    list_display = ['__str__']

def fix(modeladmin, request, queryset):
    queryset.update(fixed=True)
def unfix(modeladmin, request, queryset):
    queryset.update(fixed=False)

class ErrorAdmin(admin.ModelAdmin):
    list_display = ['player', 'short_error', 'timestamp', 'date', 'fixed']
    search_fields = ['player__name', 'player__tId']
    list_filter = ['fixed', 'short_error']
    readonly_fields = ['player', ]
    actions = [fix, unfix]

    def date(self, instance):
        return timestampToDate(instance.timestamp)

admin.site.register(Error, ErrorAdmin)
admin.site.register(Key, KeyAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Message, MessageAdmin)
# admin.site.register(News, NewsAdmin)
admin.site.register(Donation, DonationAdmin)
admin.site.register(PlayerData, PlayerDataAdmin)
