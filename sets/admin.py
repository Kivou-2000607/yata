from django.contrib import admin
from django.utils.html import format_html

from .models import *


class MarketDataInline(admin.TabularInline):
    model = MarketData
    extra = 0


class MarketDataAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'quantity', 'cost']


admin.site.register(MarketData, MarketDataAdmin)


class userStockInline(admin.TabularInline):
    model = userStock
    extra = 0


class userStockAdmin(admin.ModelAdmin):
    list_display = ['item', 'user', 'quantity']


admin.site.register(userStock, userStockAdmin)


def remove_from_market(modeladmin, request, queryset):
    queryset.update(onMarket=False)


def put_on_market(modeladmin, request, queryset):
    queryset.update(onMarket=True)


class ItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'tId', 'tName', 'tType', 'tMarketValue', 'tImage', 'onMarket']
    inlines = [MarketDataInline]
    actions = [remove_from_market, put_on_market]
    list_filter = ['tType']


admin.site.register(Item, ItemAdmin)


class configAdmin(admin.ModelAdmin):
    list_display = ['id', 'nItems', 'key', 'stockKeys']


admin.site.register(config, configAdmin)


# login

class loginDateInline(admin.TabularInline):
    model = loginDate
    extra = 0

class loginDateAdmin(admin.ModelAdmin):
    list_display = ['date']

admin.site.register(loginDate, loginDateAdmin)


class loginAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'date', 'n_log', 'show_url']
    list_filter = ['user_name', 'user_id']
    inlines = [loginDateInline]

    def show_url(self, instance):
        return format_html('<a href="{url}" target="_blank">{url}</a>'.format(url=instance.torn_url_page()))
    show_url.allow_tags = True

admin.site.register(login, loginAdmin)
