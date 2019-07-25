from django.contrib import admin

from .models import Stock


class StockAdmin(admin.ModelAdmin):
    list_display = ['tName', 'tAcronym', 'tAvailableShares']


admin.site.register(Stock, StockAdmin)
