from django.urls import re_path

from .views import auth, bse, faction, loot, main, setup, spies, targets, travel

app_name = "api"
urlpatterns = [
    re_path(r"^$", main.index, name="index"),
    re_path(r"^v1/$", main.documentation, name="documentation"),
    # loot
    re_path(r"^v1/loot/$", loot.loot, name="loot"),
    # stocks
    # re_path(r'^v1/stocks/get/$', stocks.getStocks, name="getStocks"),
    # travel
    re_path(r"^v1/travel/export/$", travel.exportStocks, name="exportStocks"),
    re_path(r"^v1/travel/import/$", travel.importStocks, name="importStocks"),
    # targets
    re_path(r"^v1/targets/export/$", targets.exportTargets, name="exportTargets"),
    re_path(r"^v1/targets/import/$", targets.importTargets, name="importTargets"),
    # spies
    re_path(r"^v1/spies/$", spies.getSpies, name="getSpies"),
    re_path(r"^v1/spies/import/$", spies.importSpies, name="importSpies"),
    re_path(r"^v1/spy/(?P<target_id>[0-9]*)/$", spies.getSpy, name="getSpy"),
    # faction
    re_path(r"^v1/faction/crimes/export/$", faction.getCrimes, name="getCrimes"),
    re_path(
        r"^v1/faction/crimes/import/ranking/$",
        faction.updateRanking,
        name="updateRanking",
    ),  # deprecated
    re_path(r"^v1/faction/members/$", faction.getMembers, name="getMembers"),
    re_path(r"^v1/faction/livechain/$", faction.livechain, name="livechain"),
    # auth
    re_path(r"^v1/auth/$", auth.index, name="auth"),
    # setup
    re_path(r"^v1/setup/players/$", setup.players, name="players"),
    # bse
    re_path(r"^v1/bs/(?P<target_id>[0-9]*)/$", bse.bs, name="bs"),
]
