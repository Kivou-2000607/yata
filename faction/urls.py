from django.urls import re_path

from . import views

app_name = "faction"
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    # SECTION: configuration
    re_path(r'^configurations/$', views.configurations, name='configurations'),
    re_path(r'^configurationsKey/$', views.configurationsKey, name='configurationsKey'),
    re_path(r'^configurationsThreshold/$', views.configurationsThreshold, name='configurationsThreshold'),
    re_path(r'^configurationsPoster/$', views.configurationsPoster, name='configurationsPoster'),

    # SECTION: members
    re_path(r'^members/$', views.members, name='members'),
    re_path(r'^updateMember/$', views.updateMember, name='updateMember'),
    re_path(r'^toggleMemberShare/$', views.toggleMemberShare, name='toggleMemberShare'),

    # SECTION: chain
    re_path(r'^chains/$', views.chains, name='chains'),
    re_path(r'^report/(?P<chainId>\w+)$', views.report, name='report'),
    re_path(r'^manageReport/$', views.manageReport, name='manageReport'),
    re_path(r'^iReport/$', views.iReport, name='iReport'),
    re_path(r'^combined/$', views.combined, name='combined'),

    # SECTION: wall
    re_path(r'^walls/$', views.walls, name='walls'),
    re_path(r'^walls/manage/$', views.manageWall, name='manageWall'),
    re_path(r'^walls/import/$', views.importWall, name='importWall'),

    ]
