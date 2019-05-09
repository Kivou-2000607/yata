from django.contrib import admin

from .models import MarketData
from .models import Item
from .models import Preference
#
# from django.contrib.sessions.models import Session
#
#
# class SessionAdmin(admin.ModelAdmin):
#     list_display = ['session_key', 'expire_date']
#
#
# admin.site.register(Session, SessionAdmin)


class MarketDataInline(admin.TabularInline):
    model = MarketData
    extra = 0


class MarketDataAdmin(admin.ModelAdmin):
    list_display = ['item', 'sellId', 'quantity', 'cost']


admin.site.register(MarketData, MarketDataAdmin)


def remove_from_market(modeladmin, request, queryset):
    queryset.update(onMarket=False)


def put_on_market(modeladmin, request, queryset):
    queryset.update(onMarket=True)


class ItemAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'tType', 'lastUpdateTS', 'tMarketValue', 'tImage', 'onMarket']
    inlines = [MarketDataInline]
    actions = [remove_from_market, put_on_market]
    list_filter = ['tType', 'lastUpdateTS']


admin.site.register(Item, ItemAdmin)


class PreferenceAdmin(admin.ModelAdmin):
    list_display = ['id', 'nItems', 'lastScanTS']


admin.site.register(Preference, PreferenceAdmin)
