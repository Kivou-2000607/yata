from django.contrib import admin

# Register your models here.

from .models import Faction
from .models import Chain
from .models import Member
from .models import Report
from .models import Count
from .models import Bonus


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
    list_display = ['report', 'name', 'hits']


admin.site.register(Count, CountAdmin)


class ReportInline(admin.TabularInline):
    model = Report
    extra = 0


class ReportAdmin(admin.ModelAdmin):
    list_display = ['chain', 'date']
    inlines = [CountInline]


admin.site.register(Report, ReportAdmin)


def chain_on_report(modeladmin, request, queryset):
    queryset.update(status=True)


def chain_off_report(modeladmin, request, queryset):
    queryset.update(status=False)


class ChainInline(admin.TabularInline):
    model = Chain
    extra = 0


class ChainAdmin(admin.ModelAdmin):
    list_display = ['tId', 'nHits', 'startDate', 'startDate', 'respect', 'status']
    actions = [chain_on_report, chain_off_report]
    inlines = [ReportInline]


admin.site.register(Chain, ChainAdmin)


class MemberInline(admin.TabularInline):
    model = Member
    extra = 0


class MemberAdmin(admin.ModelAdmin):
    list_display = ['tId', 'name', 'daysInFaction', 'lastAction']
    # inlines = [CountInline]


admin.site.register(Member, MemberAdmin)


class FactionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'number_of_chains', 'hitsThreshold']
    inlines = [ChainInline, MemberInline]

    def number_of_chains(seld, instance):
        return(len(instance.chain_set.all()))


admin.site.register(Faction, FactionAdmin)
