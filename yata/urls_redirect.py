from django.urls import re_path

from . import views_redirect

from api.views import travel
from api.views import targets
from api.views import faction
from api.views import loot
from setup.views import analytics

app_name = "yata"

urlpatterns = [
    # re_path(r'^api/v1/loot/$', loot.loot),
    re_path(r'^setup/analytics/$', analytics),
    re_path(r'^loot/timings/$', loot.loot),
    re_path(r'^api/v1/travel/import/$', travel.importStocks),
    re_path(r'^api/v1/targets/import/$', targets.importTargets),
    re_path(r'^api/v1/faction/crimes/import/ranking/$', faction.updateRanking),
    re_path(r'^api/v1/faction/walls/import/$', faction.importWall),
    re_path(r'^.*$', views_redirect.index),
]
