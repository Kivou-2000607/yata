from django.contrib import admin

from .models import *
from faction.models import Faction
from yata.handy import timestampToDate


class KeyInline(admin.TabularInline):
    model = Key
    extra = 0


class KeyAdmin(admin.ModelAdmin):
    list_display = ['player', 'useFact', 'useSelf']
    search_fields = ['player__name', 'tId']
    readonly_fields = ['player', ]


class PlayerAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}

    list_display = ['tId', 'name', 'active', 'validKey', 'dId']
    search_fields = ['name', 'tId']
    list_filter = ['active', 'validKey']
    inlines = [KeyInline]
    exclude = ['apikey', 'bazaarJson', 'awardsJson', 'stocksJson']

    def last_update(self, instance):
        return timestampToDate(instance.lastUpdateTS)

    def last_action(self, instance):
        return timestampToDate(instance.lastActionTS)

# class NewsAdmin(admin.ModelAdmin):
#     list_display = ['__str__', 'date', 'type', 'authorName', 'authorId', 'read']
#     filter_horizontal = ('player',)


class MessageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'date', 'section', 'authorName', 'authorId']


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


class SpinnerAdmin(admin.ModelAdmin):
    list_display = ['pk', 'factionId', 'faction', 'spinner']

    def faction(self, instance):
        return Faction.objects.filter(tId=instance.factionId).first()


def add_gym_book_20(modeladmin, request, queryset):
    queryset.update(perks_gym_book=20)


def add_gym_book_30(modeladmin, request, queryset):
    queryset.update(perks_gym_book=30)


def recompute_error(modeladmin, request, queryset):
    for q in queryset:
        q.set_error()


def remove_gym_book(modeladmin, request, queryset):
    queryset.update(perks_gym_book=0)


class TrainFullAdmin(admin.ModelAdmin):
    list_display = ['pk', 'id_key', 'stat_type', 'error', 'single_train', 'timestamp']
    search_fields = ['id_key', 'pk']
    list_filter = ('single_train', )
    actions = [add_gym_book_20, add_gym_book_30, recompute_error, remove_gym_book]

    def diff(self, instance):
        return instance.current_diff()


admin.site.register(Error, ErrorAdmin)
admin.site.register(TrainFull, TrainFullAdmin)
admin.site.register(Spinner, SpinnerAdmin)
admin.site.register(Key, KeyAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Message, MessageAdmin)
# admin.site.register(News, NewsAdmin)
admin.site.register(Donation, DonationAdmin)
admin.site.register(PlayerData, PlayerDataAdmin)
