"""
Copyright 2019 kivou.2000607@gmail.com

This file is part of yata.

    yata is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    yata is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with yata. If not, see <https://www.gnu.org/licenses/>.
"""

from django.contrib import admin

from .models import Faction
from .models import Chain
from .models import Member
from .models import Report
from .models import Count
from .models import Bonus
from .models import Attacks
from .models import FactionData
from .models import Crontab
from .models import Wall
from .models import Territory
from .models import Racket
from .models import Stat
from .models import Revive
from .models import ReviveContract
from .models import Attack
from .models import AttacksBreakdown

from yata.handy import timestampToDate

import json


class ReviveAdmin(admin.ModelAdmin):
    list_display = ['contract', 'timestamp']


admin.site.register(Revive, ReviveAdmin)


class ReviveContractAdmin(admin.ModelAdmin):
    list_display = ['faction', 'start', 'end', 'computing']


admin.site.register(ReviveContract, ReviveContractAdmin)


class AttacksBreakdownAdmin(admin.ModelAdmin):
    list_display = ['faction', 'tss', 'tse', 'live']


admin.site.register(AttacksBreakdown, AttacksBreakdownAdmin)


class FactionDataAdmin(admin.ModelAdmin):
    list_display = ['__str__']


admin.site.register(FactionData, FactionDataAdmin)


class AttacksInline(admin.TabularInline):
    model = Attacks
    extra = 0
    show_change_link = True
    can_delete = False
    readonly_fields = ('tss', 'tse',)
    exclude = ['req']


class AttacksAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'date_start', 'date_end']

    def report(self, instance):
        return instance.report

    def date_start(self, instance):
        return timestampToDate(instance.tss)

    def date_end(self, instance):
        return timestampToDate(instance.tse)


admin.site.register(Attacks, AttacksAdmin)


class BonusInline(admin.TabularInline):
    model = Bonus
    extra = 0
    show_change_link = True
    can_delete = False
    readonly_fields = ('tId', 'name', 'hit', 'respect', 'respectMax', 'targetId', 'targetName')


class BonusAdmin(admin.ModelAdmin):
    list_display = ['report', 'name', 'hit']


admin.site.register(Bonus, BonusAdmin)


class CountInline(admin.TabularInline):
    model = Count
    extra = 0
    show_change_link = True
    can_delete = False
    readonly_fields = ('attackerId', 'name', 'hits', 'bonus', 'wins', 'respect', 'fairFight', 'war', 'retaliation', 'groupAttack', 'overseas', 'daysInFaction', 'beenThere', 'watcher', 'warhits')
    exclude = ['graph']


class CountAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'name', 'hits']


admin.site.register(Count, CountAdmin)


class ReportInline(admin.TabularInline):
    model = Report
    extra = 0
    show_change_link = True


class ReportAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}
    list_display = ['__str__']
    inlines = [AttacksInline, CountInline, BonusInline]


admin.site.register(Report, ReportAdmin)


def chain_on_report(modeladmin, request, queryset):
    queryset.update(status=True)


def chain_off_report(modeladmin, request, queryset):
    queryset.update(status=False)


class ChainInline(admin.TabularInline):
    model = Chain
    extra = 0
    show_change_link = True
    can_delete = False
    readonly_fields = ('tId', 'reportNHits', 'nHits', 'nAttacks', 'respect', 'start', 'end', 'status', 'createReport', 'hasReport', 'jointReport', 'graph')


class ChainAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}

    list_display = ['__str__', 'hasReport', 'tId', 'nHits', 'respect', 'status']
    actions = [chain_on_report, chain_off_report]
    inlines = [ReportInline]
    search_fields = ['tId']


admin.site.register(Chain, ChainAdmin)


class StatAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}

    list_display = ['pk', 'faction', 'name']
    search_fields = ['author']


admin.site.register(Stat, StatAdmin)


class MemberInline(admin.TabularInline):
    model = Member
    extra = 0
    show_change_link = True
    can_delete = False
    readonly_fields = ('tId', 'name', 'daysInFaction', 'lastAction', 'status')


admin.site.register(Member)


class FactionAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}

    list_display = ['tId', 'name', 'createLive', 'createReport', 'ongoing_reports', 'number_of_reports', 'numberOfKeys', 'last_api_call', 'lastAPICall', 'crontabs', 'armoryRecord']
    # inlines = [ChainInline, MemberInline]
    list_filter = ['createLive', 'createReport', 'armoryRecord']
    search_fields = ['name', 'tId']
    exclude = ['factionTree', 'simuTree', 'memberStatus', 'armoryString', 'fundsString', 'networthString']

    # def live_chain(self, instance):
    #     return(bool(len(instance.chain_set.filter(tId=0))))
    # live_chain.boolean = True

    def number_of_reports(self, instance):
        return("{}/{}".format(len(instance.chain_set.filter(hasReport=True)), len(instance.chain_set.all())))

    def ongoing_reports(self, instance):
        return("{}/{}".format(len(instance.chain_set.filter(createReport=True)), len(instance.chain_set.all())))

    # def number_of_keys(self, instance):
    #     return(len(json.loads(instance.apiString)))

    def last_api_call(self, instance):
        return(timestampToDate(instance.lastAPICall))

    def crontabs(self, instance):
        return ", ".join([str(crontab) for crontab in instance.crontab_set.all()])


admin.site.register(Faction, FactionAdmin)


class CrontabAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'tabNumber', 'open', 'number_of_factions', 'list_of_factions']
    filter_horizontal = ('faction',)

    def number_of_factions(self, instance):
        return len(instance.faction.all())

    def list_of_factions(self, instance):
        return ", ".join([str(f) for f in instance.faction.all()])


admin.site.register(Crontab, CrontabAdmin)


class WallAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}

    list_display = ['tId', 'tss', 'attackerFactionName', 'defenderFactionName', 'territory']


admin.site.register(Wall, WallAdmin)


class TerritoryAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}

    list_display = ['tId', 'faction', 'have_racket']
    search_fields = ['tId', 'faction']

    def have_racket(self, instance):
        racket = json.loads(instance.racket)
        if len(racket):
            return racket.get("name")


admin.site.register(Territory, TerritoryAdmin)


class RacketAdmin(admin.ModelAdmin):
    list_display = ['tId', 'name']
    search_fields = ['tId', 'name']


admin.site.register(Racket, RacketAdmin)
