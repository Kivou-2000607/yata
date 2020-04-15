from django.urls import re_path

from . import views

app_name = "target"
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^attacks/$', views.attacks, name='attacks'),
    re_path(r'^attack/$', views.attack, name='attack'),

    re_path(r'^targets/$', views.targets, name='targets'),
    re_path(r'^targets/list/$', views.targetsList, name='targetsList'),
    re_path(r'^target/$', views.target, name='target'),

    re_path(r'^revives/$', views.revives, name='revives'),
    re_path(r'^revive/$', views.revive, name='revive'),


    ]
