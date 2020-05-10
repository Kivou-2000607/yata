from django.urls import re_path
from django.shortcuts import redirect

from . import views

app_name = "bot"
urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^welcome/$', views.welcome, name='welcome'),
    re_path(r'^documentation/$', views.documentation, name='documentation'),
    re_path(r'^host/$', views.host, name='host'),
    re_path(r'^admin/$', views.admin, name='admin'),
    re_path(r'^invite/$', lambda x: redirect('https://discordapp.com/oauth2/authorize?client_id=623862007434706986&scope=bot&permissions=8'), name="invite"),

    re_path(r'^updateId/$', views.updateId, name='updateId'),
    re_path(r'^togglePerm/$', views.togglePerm, name='togglePerm'),
    re_path(r'^toggleNoti/$', views.toggleNoti, name='toggleNoti'),
    # re_path(r'^togglePref/(?P<type>\w+)/$', views.togglePref, name='togglePref'),

    re_path(r'^secret/$', views.secret, name='secret'),
    ]
