from django.contrib import admin

from faction.models import *


### Faction
class FactionAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('perso/css/admin.css',)}

    list_display = ['__str__', 'nKeys']
    search_fields = ['tId', 'name']
    raw_id_fields = ("masterKeys", )
    # list_filter = ['createLive', 'createReport', 'armoryRecord']
    # exclude = ['factionTree', 'simuTree', 'memberStatus', 'armoryString', 'fundsString', 'networthString']


class MemberAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'faction', 'shareE', 'shareN']
    # search_fields = ['tId', 'name']
    # raw_id_fields = ("masterKeys", )
    list_filter = ('faction__name', 'shareE', 'shareN')
    search_fields = ('faction__name', 'name', 'tId')
    # exclude = ['factionTree', 'simuTree', 'memberStatus', 'armoryString', 'fundsString', 'networthString']

admin.site.register(Member, MemberAdmin)
admin.site.register(Faction, FactionAdmin)
