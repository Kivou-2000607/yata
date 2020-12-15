from django.urls import re_path

from .views import main
from .views import loot
from .views import travel
from .views import targets
from .views import faction
from .views import auth

app_name = "api"
urlpatterns = [
    re_path(r'^$', main.index, name='index'),
    re_path(r'^v1/$', main.documentation, name='documentation'),

    # loot
    re_path(r'^v1/loot/$', loot.loot, name="loot"),

    # travel
    re_path(r'^v1/travel/export/$', travel.exportStocks, name="exportStocks"),
    re_path(r'^v1/travel/import/$', travel.importStocks, name="importStocks"),

    # targets
    re_path(r'^v1/targets/export/$', targets.exportTargets, name="exportTargets"),
    re_path(r'^v1/targets/import/$', targets.importTargets, name="importTargets"),

    # faction
    re_path(r'^v1/faction/crimes/export/$', faction.getCrimes, name="getCrimes"),
    re_path(r'^v1/faction/crimes/import/ranking/$', faction.updateRanking, name="updateRanking"),
    re_path(r'^v1/faction/walls/import/$', faction.importWall, name="importWall"),

    # auth
    re_path(r'^v1/auth/$', auth.index, name="auth"),
    ]
