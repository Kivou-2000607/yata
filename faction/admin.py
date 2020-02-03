from django.contrib import admin

from faction.models import *


class FactionAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}

    list_display = ['__str__', 'nKeys']
    autocomplete_fields = ("masterKeys", )
    search_fields = ['tId', 'name']


# class MemberAdmin(admin.ModelAdmin):
#     list_display = ['__str__', 'faction', 'shareE', 'shareN']
#     list_filter = ('faction__name', 'shareE', 'shareN')
#     search_fields = ('faction__name', 'name', 'tId')

def reset_chain(modeladmin, request, queryset):
    queryset.update(last=0,
                    update=0,
                    computing=True,
                    report=True,
                    state=0,
                    current=0,
                    attacks=0,
                    graphs="{}")
    for q in queryset:
        q.attackchain_set.all().delete()
        q.count_set.all().delete()
        q.bonus_set.all().delete()
        q.assignCrontab()
    # queryset.objects.attackchain_set.all().delete()


reset_chain.short_description = "Reset chain"


class ChainAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}

    list_display = ['__str__', 'live', 'report', 'computing', 'crontab', 'update', 'current', 'chain', 'progress', 'state', 'status', 'start', 'last', 'end']
    list_filter = ('computing', 'report', 'live', 'crontab', 'state')
    search_fields = ('faction__name', 'tId')
    exclude = ['graphs']
    actions = [reset_chain]

    def status(self, instance):
        return CHAIN_ATTACKS_STATUS.get(instance.state, "?")


def reset_report(modeladmin, request, queryset):
    queryset.update(last=0,
                    update=0,
                    computing=True,
                    state=0,
                    attackerFactions="[]",
                    defenderFactions="[]",
                    defends=0,
                    attacks=0)
    for q in queryset:
        q.attackreport_set.all().delete()
        q.assignCrontab()


reset_report.short_description = "Reset report"


class AttacksReportAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}

    list_display = ['__str__', 'live', 'computing', 'state', 'update', 'progress', 'state', 'status', 'start', 'last', 'end']
    search_fields = ('pk', 'faction__name')
    list_filter = ('live', 'computing', 'crontab', 'state')
    autocomplete_fields = ['wall']
    actions = [reset_report]

    def status(self, instance):
        return REPORT_ATTACKS_STATUS.get(instance.state, "?")


class WallAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}

    list_display = ['__str__', 'attackerFactionName', 'defenderFactionName']
    search_fields = ('attackerFactionName', 'defenderFactionName', 'tId')


class NewsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'news', 'timestamp']
    list_filter = ('type', )
    search_fields = ('faction__name', 'type')


class LogAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'timestampday', 'timestamp']
    search_fields = ('faction__name', 'type')


class ContributorsAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}

    list_display = ['__str__', 'stat', 'timestamphour', 'timestamp']
    search_fields = ('faction__name', 'stat')
    list_filter = ('stat', )


class FactionDataAdmin(admin.ModelAdmin):
    list_display = ['__str__']


admin.site.register(FactionData, FactionDataAdmin)
admin.site.register(Contributors, ContributorsAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(AttacksReport, AttacksReportAdmin)
admin.site.register(Wall, WallAdmin)
admin.site.register(Chain, ChainAdmin)
# admin.site.register(Member, MemberAdmin)
admin.site.register(Faction, FactionAdmin)
