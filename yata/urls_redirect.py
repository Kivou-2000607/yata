from django.urls import include, re_path

from . import views_redirect

from api.views import travel
from api.views import targets
from api.views import faction
from api.views import loot
from awards import views as views_awards

app_name = "yata"

urlpatterns = [

    # for torn PDA
    re_path(r'^awards/', include('awards.urls')),

    # to support CORS
    re_path(r'^api/v1/loot/$', loot.loot),
    re_path(r'^api/v1/travel/export/$', travel.exportStocks),

    # to close at the very end
    re_path(r'^api/v1/travel/import/$', travel.importStocks),
    re_path(r'^api/v1/targets/import/$', targets.importTargets),
    re_path(r'^api/v1/faction/crimes/import/ranking/$', faction.updateRanking),
    re_path(r'^api/v1/faction/walls/import/$', faction.importWall),

    # hacks
    re_path(r'', views_redirect.index, name="logout"),
    re_path(r'', views_redirect.index, name="discord"),
    re_path(r'', include('player.urls')),
    re_path(r'', include('bazaar.urls')),
    re_path(r'', include('company.urls')),
    re_path(r'', include('stock.urls')),
    re_path(r'', include('faction.urls')),
    re_path(r'', include('target.urls')),
    re_path(r'', include('loot.urls')),

    # the redirection page
    re_path(r'^.*$', views_redirect.index, name="index"),
]
