from django.contrib import admin

from faction.models import *


# Faction
class FactionAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}

    list_display = ['__str__', 'nKeys']
    search_fields = ['tId', 'name']
    raw_id_fields = ("masterKeys", )


# Members
class MemberAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'faction', 'shareE', 'shareN']
    list_filter = ('faction__name', 'shareE', 'shareN')
    search_fields = ('faction__name', 'name', 'tId')


# Chains
# class CountInline(admin.TabularInline):
#     model = Count
#     extra = 0
#     # show_change_link = True
#     can_delete = False
#     readonly_fields = ('name', 'attackerId', 'hits', 'bonus', 'wins', 'respect', 'fairFight', 'war', 'retaliation', 'groupAttack', 'overseas', 'daysInFaction', 'beenThere', 'watcher', 'warhits')
#     exclude = ['graph']


class ChainAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}

    list_display = ['__str__', 'live', 'report', 'computing', 'crontab', 'current', 'chain', 'progress', 'state']
    list_filter = ('faction__name', 'live', 'report', 'computing', 'crontab', 'state')
    search_fields = ('faction__name', 'tId')
    exclude = ['graphs']
    # inlines = [CountInline]


class AttackChainAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'report']
    search_fields = ('tId',)


class AttacksReportAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}

    list_display = ['__str__', 'start', 'end', 'live', 'computing', 'state', 'progress', 'state']
    search_fields = ('pk', 'faction__name')
    list_filter = ('live', 'computing', 'crontab', 'state')




admin.site.register(AttacksReport, AttacksReportAdmin)
admin.site.register(AttackChain, AttackChainAdmin)
admin.site.register(Chain, ChainAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Faction, FactionAdmin)
