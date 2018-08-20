from django.contrib import admin
from django.utils.html import format_html

from .models import MarketData
from .models import Item
from .models import Config
from .models import Player
from .models import Login


class MarketDataInline(admin.TabularInline):
    model = MarketData
    extra = 0


class MarketDataAdmin(admin.ModelAdmin):
    list_display = ['userId', 'quantity', 'cost']


admin.site.register(MarketData, MarketDataAdmin)


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


class ConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'nItems', 'autorisedId', 'lastScan']


admin.site.register(Config, ConfigAdmin)


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'date', 'nLog', 'show_url']
    list_filter = ['name', 'playerId']

    def show_url(self, instance):
        return format_html('<a href="{url}" target="_blank">{url}</a>'.format(url=instance.torn_url_page()))
    show_url.allow_tags = True


admin.site.register(Player, PlayerAdmin)


class LoginAdmin(admin.ModelAdmin):
    list_display = ['id', 'player', 'date']
    list_filter = ['player', 'date']


admin.site.register(Login, LoginAdmin)
