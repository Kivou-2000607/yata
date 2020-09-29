from django.urls import re_path

from .views import loot
from .views import travel

app_name = "api"
urlpatterns = [
    # re_path(r'^$', views.index, name='index'),

    # loot
    re_path(r'^v1/loot/$', loot.loot, name='loot'),

    # items
    re_path(r'^v1/travel/export/$', travel.exportStocks, name='exportStocks'),
    re_path(r'^v1/travel/import/$', travel.importStocks, name='importStocks'),
    ]
