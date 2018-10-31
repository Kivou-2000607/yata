from django.urls import re_path

from . import views

app_name = "chain"
urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^updateLive/$', views.updateLive, name='updateLive'),

    re_path(r'^members/$', views.members, name='members'),
    re_path(r'^createMembers/$', views.createMembers, name='createMembers'),

    re_path(r'^list/$', views.list, name='list'),
    re_path(r'^createList/$', views.createList, name='createList'),

    re_path(r'^report/(?P<chainId>\w+)$', views.report, name='report'),
    re_path(r'^createReport/(?P<chainId>\w+)$', views.createReport, name='createReport'),
    re_path(r'^deleteReport/(?P<chainId>\w+)$', views.deleteReport, name='deleteReport'),
    re_path(r'^toggleReport/(?P<chainId>\w+)$', views.toggleReport, name='toggleReport'),
    re_path(r'^toggleFactionKey/$', views.toggleFactionKey, name='toggleFactionKey'),
    re_path(r'^createIndividualReport/(?P<chainId>\w+)/(?P<memberId>\w+)$', views.createIndividualReport, name='createIndividualReport'),

    re_path(r'^jointReport/$', views.jointReport, name='jointReport'),

    re_path(r'^targets/$', views.targets, name='targets'),
    re_path(r'^refreshTarget/(?P<targetId>\w+)$', views.refreshTarget, name='refreshTarget'),
    re_path(r'^refreshAllTargets/$', views.refreshAllTargets, name='refreshAllTargets'),
    re_path(r'^deleteTarget/(?P<targetId>\w+)$', views.deleteTarget, name='deleteTarget'),
    re_path(r'^toggleTarget/(?P<targetId>\w+)$', views.toggleTarget, name='toggleTarget'),

    re_path(r'^tree/$', views.tree, name='tree'),

    re_path(r'^updateKey/$', views.updateKey, name='updateKey'),
    re_path(r'^logout/$', views.logout, name='logout'),

    # path('<int:tId>', views.details, name='details'),
    ]
