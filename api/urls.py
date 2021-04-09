from django.urls import re_path

from .views import main
from .views import loot
from .views import stocks
from .views import travel
from .views import targets
from .views import spies
from .views import faction
from .views import auth
from .views import setup

app_name = "api"
urlpatterns = [
    re_path(r'^$', main.index, name='index'),
    re_path(r'^v1/$', main.documentation, name='documentation'),

    # loot
    re_path(r'^v1/loot/$', loot.loot, name="loot"),

    # stocks
    re_path(r'^v1/stocks/alerts/$', stocks.alerts, name="stocksAlerts"),

    # travel
    re_path(r'^v1/travel/export/$', travel.exportStocks, name="exportStocks"),
    re_path(r'^v1/travel/import/$', travel.importStocks, name="importStocks"),

    # targets
    re_path(r'^v1/targets/export/$', targets.exportTargets, name="exportTargets"),
    re_path(r'^v1/targets/import/$', targets.importTargets, name="importTargets"),

    # spies
    re_path(r'^v1/spies/$', spies.getSpies, name="getSpies"),
    re_path(r'^v1/spy/(?P<target_id>[0-9]*)/$', spies.getSpy, name="getSpy"),

    # faction
    re_path(r'^v1/faction/crimes/export/$', faction.getCrimes, name="getCrimes"),
    re_path(r'^v1/faction/crimes/import/ranking/$', faction.updateRanking, name="updateRanking"),
    re_path(r'^v1/faction/walls/import/$', faction.importWall, name="importWall"),

    # auth
    re_path(r'^v1/auth/$', auth.index, name="auth"),

    # setup
    re_path(r'^v1/setup/donations/$', setup.donations, name="donations"),
    re_path(r'^v1/setup/players/$', setup.players, name="players"),
    ]
