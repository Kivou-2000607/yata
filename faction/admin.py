from django.contrib import admin

from faction.models import *
from yata.handy import timestampToDate
from django_json_widget.widgets import JSONEditorWidget


class EventAdmin(admin.TabularInline):
    model = Event
    extra = 1

class FactionTreeAdmin(admin.ModelAdmin):
    pass
class FactionAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('yata/css/admin.css',)}

    list_display = ['__str__', 'nKeys']
    autocomplete_fields = ("masterKeys", )
    search_fields = ['tId', 'name']
    inlines = [EventAdmin, ]


class MemberAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'faction', 'shareE', 'shareN']
    list_filter = ('faction__name', 'shareE', 'shareN')
    search_fields = ('faction__name', 'name', 'tId')

class AttackChainAdmin(admin.StackedInline):
    model = AttackChain
    extra = 0
    fields = ["tId"]
    max_num = 10
    readonly_fields = ["tId"]
    can_delete = False


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
        print("{} delete attack: {}".format(q, q.attackchain_set.all().delete()))
        q.count_set.all().delete()
        q.bonus_set.all().delete()
        print("{} assign crontab {}".format(q, q.assignCrontab()))


def start_computing_special(modeladmin, request, queryset):
    queryset.update(computing=True, crontab=11)


def stop_computing(modeladmin, request, queryset):
    queryset.update(computing=False, crontab=0)


def start_computing(modeladmin, request, queryset):
    queryset.update(computing=True)


def delete_attacks(modeladmin, request, queryset):
    for q in queryset:
        print("{} delete attack: {}".format(q, q.attackchain_set.all().delete()))


def assign_crontab(modeladmin, request, queryset):
    for q in queryset:
        print("{} assign crontab {}".format(q, q.assignCrontab()))


def delete_chain(modeladmin, request, queryset):
    for q in queryset:
        q.delete()


reset_chain.short_description = "Reset chain"
start_computing_special.short_description = "Start computing (crontab 11)"
start_computing.short_description = "Start computing"
stop_computing.short_description = "Stop computing"
delete_attacks.short_description = "Delete all attacks"
assign_crontab.short_description = "Assign Crontab"
delete_chain.short_description = "Delete chain"


class ChainAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('yata/css/admin.css',)}

    list_display = ['__str__', 'live', 'computing', 'cooldown', 'current', 'attacks', 'chain', 'progress', 'crontab', 'state', 'status', '_update', 'elapsed']
    list_filter = ('computing', 'live', 'cooldown', 'state', 'report', 'crontab')
    search_fields = ('faction__name', 'tId')
    exclude = ['graphs']
    actions = [reset_chain, start_computing, start_computing_special, stop_computing, assign_crontab, delete_attacks, delete_chain]
    # inlines = [AttackChainAdmin]

    def status(self, instance):
        return CHAIN_ATTACKS_STATUS.get(instance.state, "?")

    def _update(self, instance):
        return timestampToDate(instance.update, fmt="%m/%d %H:%M")


def reset_report_a(modeladmin, request, queryset):
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


reset_report_a.short_description = "Reset report"


class AttacksFactionAdmin(admin.TabularInline):
    model = AttacksFaction
    readonly_fields = ["faction_id", "faction_name", "hits", "attacks", "defends", "attacked", "showA", "showD"]
    extra = 0
    can_delete = False


class AttacksPlayerAdmin(admin.TabularInline):
    model = AttacksPlayer
    readonly_fields = ["player_id", "player_name", "player_faction_id", "player_faction_name", "hits", "attacks", "defends", "attacked", "showA", "showD"]
    extra = 0
    can_delete = False


class AttacksReportAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('yata/css/admin.css',)}

    list_display = ['__str__', 'live', 'computing', 'progress', 'crontab', 'state', 'status', 'update', 'start', 'last', 'end', 'elapsed']
    search_fields = ('pk', 'faction__name')
    list_filter = ('computing', 'live', 'state', 'crontab')
    # autocomplete_fields = ['wall']
    actions = [reset_report_a, start_computing, assign_crontab]
    # inlines = [AttacksFactionAdmin, AttacksPlayerAdmin]

    def status(self, instance):
        return REPORT_ATTACKS_STATUS.get(instance.state, "?")


class RevivesReportAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('yata/css/admin.css',)}

    list_display = ['__str__', 'live', 'computing', 'progress', 'crontab', 'state', 'status', 'update', 'start', 'last', 'end', 'elapsed']
    search_fields = ('pk', 'faction__name')
    list_filter = ('computing', 'live', 'state', 'crontab')
    # actions = [reset_report]

    def status(self, instance):
        return REPORT_REVIVES_STATUS.get(instance.state, "?")


class ArmoryReportAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': JSONEditorWidget},
    }

    list_display = ['__str__', 'live', 'computing', 'progress', 'crontab', 'state', 'status', 'update', 'start', 'last', 'end', 'elapsed']
    search_fields = ('pk', 'faction__name')
    list_filter = ('computing', 'live', 'state', 'crontab')
    # actions = [reset_report]

    def status(self, instance):
        return REPORTS_STATUS.get(instance.state, "?")



class LogAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'timestampday', 'timestamp']
    search_fields = ('faction__name', 'type')


class ContributorsAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('yata/css/admin.css',)}

    list_display = ['__str__', 'stat', 'timestamphour', 'timestamp']
    search_fields = ('faction__name', 'stat')
    list_filter = ('stat', )


class FactionDataAdmin(admin.ModelAdmin):
    list_display = ['__str__']


class FactionTreeAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'branch', 'name', 'tId', 'level']
    search_fields = ('branch', 'shortname')
    list_filter = ('branch', 'shortname')


class UpgradeAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'getTree', 'shortname', 'branch', 'tId', 'level', 'branchorder', 'active', 'simu', ]
    search_fields = ('faction__name', 'faction__tId', 'tId', 'level', 'unlocked',)
    list_filter = ('active', 'simu', 'branch', 'shortname')


class CrimesAdmin(admin.ModelAdmin):
    list_display = ['pk', 'tId', 'initiated', 'success', 'ready']
    search_fields = ('tId',)
    list_filter = ('faction__name', 'initiated', 'success', 'ready')


class SpyAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'database']
    search_fields = ('target_id', 'target_faction_name', )


class SpyDatabaseAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'secret']
    search_fields = ('factions', )

class FactionTargetAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'faction_name']
    search_fields = ('factions', )


admin.site.register(Crimes, CrimesAdmin)
admin.site.register(SpyDatabase, SpyDatabaseAdmin)
admin.site.register(Spy, SpyAdmin)
# admin.site.register(Upgrade, UpgradeAdmin)
# admin.site.register(FactionTree, FactionTreeAdmin)
admin.site.register(FactionData, FactionDataAdmin)
admin.site.register(Contributors, ContributorsAdmin)
# admin.site.register(Log, LogAdmin)
admin.site.register(ArmoryReport, ArmoryReportAdmin)
admin.site.register(RevivesReport, RevivesReportAdmin)
admin.site.register(AttacksReport, AttacksReportAdmin)
admin.site.register(Chain, ChainAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(FactionTarget, FactionTargetAdmin)
admin.site.register(Faction, FactionAdmin)
admin.site.register(FactionTree,FactionTreeAdmin)
