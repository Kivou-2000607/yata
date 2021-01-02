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

from yata.handy import timestampToDate

from .models import *

class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'key', 'lastCheckTS', 'last_check', 'status', 'error']

    def last_check(self, instance):
        return timestampToDate(instance.lastCheckTS)

admin.site.register(APIKey, APIKeyAdmin)


class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ['report_section', 'report_period', 'report_timestamp']

admin.site.register(Analytics, AnalyticsAdmin)


class PayPalAdmin(admin.ModelAdmin):
    list_display = ['__str__']

admin.site.register(PayPal, PayPalAdmin)


class DropletAdmin(admin.ModelAdmin):
    list_display = ['__str__']

admin.site.register(Droplet, DropletAdmin)


class DropletSpecAdmin(admin.ModelAdmin):
    list_display = ['__str__']

admin.site.register(DropletSpec, DropletSpecAdmin)


class BalanceAdmin(admin.ModelAdmin):
    list_display = ['date', 'droplet_month_cost', 'paypal_balance', 'paypal_currency', 'droplet_account_balance', 'droplet_month_to_date_usage', 'droplet_month_to_date_balance']

    list_filter = ['paypal_currency']
    search_fields = []

    def date(self, instance):
        return timestampToDate(instance.timestamp)

admin.site.register(Balance, BalanceAdmin)
