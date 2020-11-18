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


class EmployeeInline(admin.TabularInline):
    model = Employee
    extra = 0

class CompanyDataInline(admin.TabularInline):
    model = CompanyData
    extra = 0


class CompanyAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'company_description', 'tId', 'name', 'rating', 'director']
    list_filter = ['company_description']
    inlines = [EmployeeInline, CompanyDataInline]

admin.site.register(Company, CompanyAdmin)
