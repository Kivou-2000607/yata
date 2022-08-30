from django.urls import re_path
from django.shortcuts import redirect
from django.views.generic.base import RedirectView

from . import views

app_name = "bot"
urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^legacy/$', views.legacy, name='welcome'),
    re_path(r'^legacy/documentation/$', views.documentation, name='documentation'),
    re_path(r'^legacy/host/$', views.host, name='host'),
    re_path(r'^legacy/dashboard/$', views.dashboard, name='dashboard'),
    re_path(r'^legacy/dashboard/option/$', views.dashboardOption, name='dashboardOption'),
    re_path(r'^legacy/dashboard/(?P<secret>\w+)/$', views.dashboard, name='dashboardReadOnly'),

    re_path(r'^invite/$', RedirectView.as_view(url='https://discordapp.com/oauth2/authorize?client_id=623862007434706986&scope=bot&permissions=8'), name="invite"),

    re_path(r'^updateId/$', views.updateId, name='updateId'),
    re_path(r'^toggleNoti/$', views.toggleNoti, name='toggleNoti'),

    re_path(r'^legacy/secret/$', views.secret, name='secret'),
]
