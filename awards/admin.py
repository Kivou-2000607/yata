from django.contrib import admin

from .models import AwardsData

class AwardsDataAdmin(admin.ModelAdmin):
    list_display = ['__str__']


admin.site.register(AwardsData, AwardsDataAdmin)
