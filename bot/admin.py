from django.contrib import admin

# from .models import Preference
# from .models import Event
# from .models import BotData
from .models import Configuration


# class EventInline(admin.TabularInline):
#     model = Event
#     extra = 0
#     show_change_link = True
#     readonly_fields = ('timestamp', 'eventId')
#
#
# class PreferenceAdmin(admin.ModelAdmin):
#     list_display = ['player', 'yataServer', 'notificationsEvents']
#     inlines = [EventInline]
#
#
# admin.site.register(Preference, PreferenceAdmin)


# class BotDataAdmin(admin.ModelAdmin):
#     list_display = ['token']
#
#
# admin.site.register(BotData, BotDataAdmin)


class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ['pk', 'token']


admin.site.register(Configuration, ConfigurationAdmin)
