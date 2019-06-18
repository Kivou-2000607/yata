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

import json

from .models import Faction
from .models import Chain
from .models import Member
from .models import Report
from .models import Count
from .models import Bonus
from .models import Attacks
from .models import Preference
from .models import Crontab

from yata.handy import timestampToDate


class PreferenceAdmin(admin.ModelAdmin):
    list_display = ['__str__']


admin.site.register(Preference, PreferenceAdmin)


class AttacksInline(admin.TabularInline):
    model = Attacks
    extra = 0


class AttacksAdmin(admin.ModelAdmin):
    list_display = ['report', 'date_start', 'date_end']

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


class BonusAdmin(admin.ModelAdmin):
    list_display = ['report', 'name', 'hit']


admin.site.register(Bonus, BonusAdmin)


class CountInline(admin.TabularInline):
    model = Count
    extra = 0
    show_change_link = True


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
    inlines = [BonusInline, CountInline, AttacksInline]


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

    list_display = ['tId', 'name', 'live_chain', 'ongoing_reports', 'number_of_reports', 'numberOfKeys', 'last_api_call', 'lastAPICall', 'crontabs']
    inlines = [ChainInline, MemberInline]
    list_filter = ['numberOfKeys']
    search_fields = ['name', 'tId']

    def live_chain(self, instance):
        return(bool(len(instance.chain_set.filter(tId=0))))
    live_chain.boolean = True

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
    list_display = ['__str__', 'number_of_factions', 'list_of_factions']

    def number_of_factions(self, instance):
        return len(instance.faction.all())

    def list_of_factions(self, instance):
        return ", ".join([str(f) for f in instance.faction.all()])


admin.site.register(Crontab, CrontabAdmin)
