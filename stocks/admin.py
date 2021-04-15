from django.contrib import admin

from .models import Stock
from .models import History


class StockAdmin(admin.ModelAdmin):
    list_display = [ '__str__', 'current_price_format', 'live']
    list_filter = ('acronym', )

    def current_price_format(self, obj):
        return f'${obj.current_price:,.3f}'
    current_price_format.admin_order_field = 'current_price'
    current_price_format.short_description = 'current price'

    def live(self, obj):
        return f'{obj.tendancy_l_a * 60:,.3f}$'
    current_price_format.admin_order_field = 'tendancy_l_a'

class HistoryAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'timestamp', 'current_price_format']
    list_filter = ('stock', )

    def current_price_format(self, obj):
        return f'${obj.current_price:,.3f}'
    current_price_format.admin_order_field = 'current_price'
    current_price_format.short_description = 'current price'

admin.site.register(Stock, StockAdmin)
admin.site.register(History, HistoryAdmin)
