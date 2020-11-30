from django.contrib import admin

from loot.models import *

class ScheduledAttackInline(admin.TabularInline):
    model = ScheduledAttack
    extra = 0

class NPCAdmin(admin.ModelAdmin):
    list_display = ['tId', 'name', 'status', 'hospitalTS', 'updateTS']
    inlines = [ScheduledAttackInline]

admin.site.register(NPC, NPCAdmin)
# admin.site.register(ScheduledAttack, ScheduledAttackAdmin)
