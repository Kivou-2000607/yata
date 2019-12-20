from django.contrib import admin

from .models import Stock
from .models import History


class HistoryInline(admin.TabularInline):
    model = History
    extra = 0
    show_change_link = True
    readonly_fields = ('tCurrentPrice', 'tMarketCap', 'tTotalShares', 'tAvailableShares', 'tForecast', 'tDemand', 'timestamp')


class StockAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}
    list_display = ['__str__']
    # inlines = [HistoryInline]

admin.site.register(Stock, StockAdmin)


class HistoryAdmin(admin.ModelAdmin):
    list_display = ['__str__']


admin.site.register(History, HistoryAdmin)
