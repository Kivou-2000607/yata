from django.urls import re_path

from . import views_redirect

from api.views import travel
from api.views import targets
from api.views import faction

app_name = "yata"

urlpatterns = [
    re_path(r'^api/v1/travel/import/$', travel.importStocks, name="importStocks"),
    re_path(r'^api/v1/travel/import/$', travel.importStocks, name="importStocks"),
    re_path(r'^api/v1/targets/import/$', targets.importTargets, name="importTargets"),
    re_path(r'^api/v1/faction/crimes/import/ranking/$', faction.updateRanking, name="updateRanking"),
    re_path(r'^api/v1/faction/walls/import/$', faction.importWall, name="importWall"),
    re_path(r'^.*$', views_redirect.index),
]
