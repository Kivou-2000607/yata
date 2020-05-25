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

from .models import MarketData
from .models import Item
from .models import BazaarData
from .models import AbroadStocks
from .models import VerifiedClient


class BazaarDataAdmin(admin.ModelAdmin):
    list_display = ['__str__']


admin.site.register(BazaarData, BazaarDataAdmin)


class MarketDataInline(admin.TabularInline):
    model = MarketData
    extra = 0
    show_change_link = True
    readonly_fields = ('quantity', 'cost')


class MarketDataAdmin(admin.ModelAdmin):
    list_display = ['item', 'quantity', 'cost', 'itemmarket']


admin.site.register(MarketData, MarketDataAdmin)


class AbroadStocksAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'item', 'country', 'cost', 'quantity', 'timestamp', 'last']
    list_filter = ['country', 'last', 'item__tType']


admin.site.register(AbroadStocks, AbroadStocksAdmin)


def remove_from_market(modeladmin, request, queryset):
    queryset.update(onMarket=False)


def put_on_market(modeladmin, request, queryset):
    queryset.update(onMarket=True)


class ItemAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}

    list_display = ['tName', 'tId', 'tType', 'lastUpdateTS', 'tMarketValue', 'onMarket']
    inlines = [MarketDataInline]
    actions = [remove_from_market, put_on_market]
    list_filter = ['onMarket', 'tType']
    search_fields = ['tName', 'tId', 'tType']


admin.site.register(Item, ItemAdmin)


def verify(modeladmin, request, queryset):
    queryset.update(verified=True)


def unverify(modeladmin, request, queryset):
    queryset.update(verified=False)


class VerifiedClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'author_name', 'author_id', 'version', 'verified']
    actions = [verify, unverify]


admin.site.register(VerifiedClient, VerifiedClientAdmin)
