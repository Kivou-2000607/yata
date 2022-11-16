from django.contrib import admin
from django.utils.html import format_html
from django.contrib.postgres import fields
from django_json_widget.widgets import JSONEditorWidget
from django.utils.safestring import mark_safe

import json
import time

from .models import *
from yata.handy import *


class BotAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'token']
    formfield_overrides = {
        models.TextField: {'widget': JSONEditorWidget},
    }


class ServerAdmin(admin.ModelAdmin):
    list_display = ['bot', 'sub', 'date_end', 'name', 'admins', 'readonly_dashboard', ]
    # readonly_fields = ('bot', 'discord_id', 'name', 'secret',)
    autocomplete_fields = ("server_admin", )
    search_fields = ['name', 'discord_id', "server_admin__name", "server_admin__tId"]
    formfield_overrides = {
        models.TextField: {'widget': JSONEditorWidget},
    }

    def sub(self, instance):
        return instance.end > time.time() if instance.start else True
    sub.boolean = True

    def date_end(self, instance):
        return timestampToDate(instance.end, fmt="%Y/%m/%d") if instance.start else "-"

    def get_form(self, request, obj=None, **kwargs):
        if not request.user.is_superuser:
            self.exclude = ("configuration", )
        form = super(ServerAdmin, self).get_form(request, obj, **kwargs)
        return form

    def admins(self, instance):
        lst = []
        for player in instance.server_admin.all():
            lst.append('<a href="https://www.torn.com/profiles.php?XID={idt}" target="_blank">{name} [{idt}]</a> ({idd})'.format(name=player.name, idt=player.tId, idd=player.dId))
        return mark_safe(", ".join(lst))

    def readonly_dashboard(self, instance):
        if instance.secret != 'x':
            return mark_safe('<a href="/bot/dashboard/{}/" target="_blank">{}</a>'.format(instance.secret, instance.secret))
    readonly_dashboard.allow_tags = True


# class CredentialInline(admin.TabularInline):
#     model = Credential
#     extra = 0
#     show_change_link = True
#     can_delete = True
#     readonly_fields = ('uid', 'secret', 'timestamp',)
#
#
# class CredentialAdmin(admin.ModelAdmin):
#     list_display = ['__str__', 'uid', 'timestamp']
#     list_filter = ['chat__name']
#
#
# class ChatAdmin(admin.ModelAdmin):
#     list_display = ['__str__', 'name', 'uid']
#     inlines = [CredentialInline, ]


class RacketsAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'date', 'ago']
    formfield_overrides = {
        models.TextField: {'widget': JSONEditorWidget},
    }

    def date(self, instance):
        return timestampToDate(instance.timestamp, fmt="%Y/%m/%d %H:%M")

    def ago(self, instance):
        return "{:.1f}".format((tsnow() - instance.timestamp) / float(60))

class WarsAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'date', 'ago']
    formfield_overrides = {
        models.TextField: {'widget': JSONEditorWidget},
    }

    def date(self, instance):
        return timestampToDate(instance.timestamp, fmt="%Y/%m/%d %H:%M")

    def ago(self, instance):
        return "{:.1f}".format((tsnow() - instance.timestamp) / float(60))

class StocksAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'date', 'ago']
    formfield_overrides = {
        models.TextField: {'widget': JSONEditorWidget},
    }

    def date(self, instance):
        return timestampToDate(instance.timestamp, fmt="%Y/%m/%d %H:%M")

    def ago(self, instance):
        return "{:.1f}".format((tsnow() - instance.timestamp) / float(60))


admin.site.register(Stocks, StocksAdmin)
admin.site.register(Rackets, RacketsAdmin)
admin.site.register(Wars, WarsAdmin)
# admin.site.register(Credential, CredentialAdmin)
# admin.site.register(Chat, ChatAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(Bot, BotAdmin)
