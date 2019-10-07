from django.contrib import admin

from loot.models import NPC

class NPCAdmin(admin.ModelAdmin):
    list_display = ['tId', 'name', 'status', 'hospitalTS', 'updateTS']


admin.site.register(NPC, NPCAdmin)
