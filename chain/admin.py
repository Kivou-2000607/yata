from django.contrib import admin

# Register your models here.

from .models import Faction
from .models import Chain
from .models import Member
from .models import Report
from .models import Count
from .models import Bonus
from .models import Target


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
    list_display = ['__str__', 'tId', 'nHits', 'startDate', 'endDate', 'respect', 'status']
    actions = [chain_on_report, chain_off_report]
    inlines = [ReportInline]


admin.site.register(Chain, ChainAdmin)


class TargetInline(admin.TabularInline):
    model = Target
    extra = 0


class TargetAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'targetName', 'targetId']


admin.site.register(Target, TargetAdmin)


class MemberInline(admin.TabularInline):
    model = Member
    extra = 0


class MemberAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'number_of_targets', 'lastAction']
    inlines = [TargetInline]

    def number_of_targets(self, instance):
        return(len(instance.target_set.all()))

admin.site.register(Member, MemberAdmin)


class FactionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'number_of_chains', 'hitsThreshold']
    inlines = [ChainInline, MemberInline]

    def number_of_chains(self, instance):
        return(len(instance.chain_set.all()))


admin.site.register(Faction, FactionAdmin)
