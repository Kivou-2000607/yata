from django.contrib import admin

from faction.models import *


class FactionAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}

    list_display = ['__str__', 'nKeys']
    search_fields = ['tId', 'name']
    raw_id_fields = ("masterKeys", )


# class MemberAdmin(admin.ModelAdmin):
#     list_display = ['__str__', 'faction', 'shareE', 'shareN']
#     list_filter = ('faction__name', 'shareE', 'shareN')
#     search_fields = ('faction__name', 'name', 'tId')


class ChainAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}

    list_display = ['__str__', 'live', 'report', 'computing', 'crontab', 'current', 'chain', 'progress', 'state']
    list_filter = ('computing', 'report', 'live', 'crontab', 'state')
    search_fields = ('faction__name', 'tId')
    exclude = ['graphs']


class AttacksReportAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}

    list_display = ['__str__', 'start', 'end', 'live', 'computing', 'state', 'progress', 'state']
    search_fields = ('pk', 'faction__name')
    list_filter = ('live', 'computing', 'crontab', 'state')
    autocomplete_fields = ['wall']


class WallAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}

    list_display = ['__str__', 'attackerFactionName', 'defenderFactionName']
    search_fields = ('attackerFactionName', 'defenderFactionName', 'tId')


class NewsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'news', 'timestamp']
    list_filter = ('type', )
    search_fields = ('faction__name', 'type')


class LogAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'timestampday', 'timestamp']
    search_fields = ('faction__name', 'type')

admin.site.register(Log, LogAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(AttacksReport, AttacksReportAdmin)
admin.site.register(Wall, WallAdmin)
admin.site.register(Chain, ChainAdmin)
# admin.site.register(Member, MemberAdmin)
admin.site.register(Faction, FactionAdmin)
