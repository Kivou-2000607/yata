from django.contrib import admin

from target.models import *


class TargetAdmin(admin.ModelAdmin):

    list_display = ['__str__', 'update_timestamp', 'n_players']
    # autocomplete_fields = ("masterKeys", )
    # search_fields = ['tId', 'name']

    def n_players(self, instance):
        return len(TargetInfo.objects.only("target_id").filter(target_id=instance.target_id))


class TargetInfoAdmin(admin.ModelAdmin):

    list_display = ['__str__', 'update_timestamp', ]
    # autocomplete_fields = ("masterKeys", )
    # search_fields = ['tId', 'name']

admin.site.register(Target, TargetAdmin)
admin.site.register(TargetInfo, TargetInfoAdmin)
