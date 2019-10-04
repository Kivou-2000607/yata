from django.urls import re_path

from . import views

app_name = "chain"
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^live/$', views.live, name='live'),
    re_path(r'^list/$', views.list, name='list'),
    re_path(r'^jointReport/$', views.jointReport, name='jointReport'),
    re_path(r'^members/$', views.members, name='members'),
    re_path(r'^aa/$', views.aa, name='aa'),
    re_path(r'^tree/$', views.tree, name='tree'),
    re_path(r'^armory/$', views.armory, name='armory'),

    re_path(r'^report/(?P<chainId>\w+)$', views.report, name='report'),
    re_path(r'^createReport/(?P<chainId>\w+)$', views.createReport, name='createReport'),
    re_path(r'^deleteReport/(?P<chainId>\w+)$', views.deleteReport, name='deleteReport'),
    re_path(r'^toggleReport/(?P<chainId>\w+)$', views.toggleReport, name='toggleReport'),
    re_path(r'^toggleLiveReport/$', views.toggleLiveReport, name='toggleLiveReport'),
    re_path(r'^toggleKey/(?P<id>\w+)$', views.toggleKey, name='toggleKey'),
    re_path(r'^togglePoster/$', views.togglePoster, name='togglePoster'),
    re_path(r'^toggleArmoryRecord/$', views.toggleArmoryRecord, name='toggleArmoryRecord'),
    re_path(r'^resetArmoryRecord/$', views.resetArmoryRecord, name='resetArmoryRecord'),
    re_path(r'^chainThreshold/$', views.chainThreshold, name='chainThreshold'),
    re_path(r'^renderIndividualReport/(?P<chainId>\w+)/(?P<memberId>\w+)$', views.renderIndividualReport, name='renderIndividualReport'),

    re_path(r'^walls/$', views.walls, name='walls'),
    re_path(r'^deleteWall/(?P<wallId>\w+)$', views.deleteWall, name='deleteWall'),
    re_path(r'^importWall/$', views.importWall, name='importWall'),

    re_path(r'^territories/$', views.territories, name='territories'),
    re_path(r'^territoriesFullGraph/$', views.territoriesFullGraph, name='territoriesFullGraph'),
    ]
