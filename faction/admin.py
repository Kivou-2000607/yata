from django.contrib import admin

from faction.models import *


### Faction
class FactionAdmin(admin.ModelAdmin):
    list_display = ['tId', 'name']
    search_fields = ['tId', 'name']
    raw_id_fields = ("masterKeys", )
    # list_filter = ['createLive', 'createReport', 'armoryRecord']
    # exclude = ['factionTree', 'simuTree', 'memberStatus', 'armoryString', 'fundsString', 'networthString']

admin.site.register(Faction, FactionAdmin)
