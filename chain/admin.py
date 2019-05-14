from django.contrib import admin

# Register your models here.

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


class CountAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'name', 'hits']


admin.site.register(Count, CountAdmin)


class ReportInline(admin.TabularInline):
    model = Report
    extra = 0


class ReportAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'date']
    inlines = [AttacksInline]


admin.site.register(Report, ReportAdmin)


def chain_on_report(modeladmin, request, queryset):
    queryset.update(status=True)


def chain_off_report(modeladmin, request, queryset):
    queryset.update(status=False)


class ChainInline(admin.TabularInline):
    model = Chain
    extra = 0


class ChainAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'tId', 'nHits', 'respect', 'status']
    actions = [chain_on_report, chain_off_report]
    inlines = [ReportInline]


admin.site.register(Chain, ChainAdmin)


class MemberInline(admin.TabularInline):
    model = Member
    extra = 0


admin.site.register(Member)


class FactionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'number_of_chains', 'hitsThreshold']
    # inlines = [ChainInline, MemberInline]
    # inlines = [AttacksInline]

    def number_of_chains(self, instance):
        return(len(instance.chain_set.all()))

    # def crontabs(self, instance):
        # return ", ".join([str(crontab.id) for crontab in instance.crontab.all()])


admin.site.register(Faction, FactionAdmin)



class CrontabAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'number_of_factions']

    def number_of_factions(self, instance):
        return len(instance.faction.all())

admin.site.register(Crontab, CrontabAdmin)
