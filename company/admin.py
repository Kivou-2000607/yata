from django.contrib import admin

from company.models import *

class StockInline(admin.TabularInline):
    model = Stock
    extra = 0

class SpecialInline(admin.TabularInline):
    model = Special
    extra = 0

class PositionInline(admin.TabularInline):
    model = Position
    extra = 0


class CompanyDescriptionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'tId', 'name']
    list_filter = ['name']
    inlines = [PositionInline, SpecialInline, StockInline]


admin.site.register(CompanyDescription, CompanyDescriptionAdmin)
