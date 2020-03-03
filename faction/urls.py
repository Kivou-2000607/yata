from django.urls import re_path

from . import views

app_name = "faction"
urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^target/$', views.target, name='target'),

    # SECTION: configuration
    re_path(r'^configurations/$', views.configurations, name='configurations'),
    re_path(r'^configurations/key/$', views.configurationsKey, name='configurationsKey'),
    re_path(r'^configurations/threshold/$', views.configurationsThreshold, name='configurationsThreshold'),
    re_path(r'^configurations/poster/$', views.configurationsPoster, name='configurationsPoster'),
    re_path(r'^configurations/event/$', views.configurationsEvent, name='configurationsEvent'),

    # SECTION: members
    re_path(r'^members/$', views.members, name='members'),
    re_path(r'^updateMember/$', views.updateMember, name='updateMember'),
    re_path(r'^toggleMemberShare/$', views.toggleMemberShare, name='toggleMemberShare'),

    # SECTION: chain
    re_path(r'^chains/$', views.chains, name='chains'),
    re_path(r'^report/(?P<chainId>\w+)$', views.report, name='report'),
    re_path(r'^report/manage/$', views.manageReport, name='manageReport'),
    re_path(r'^report/individual/$', views.iReport, name='iReport'),
    re_path(r'^combined/$', views.combined, name='combined'),

    # SECTION: wall
    re_path(r'^walls/$', views.walls, name='walls'),
    re_path(r'^walls/manage/$', views.manageWall, name='manageWall'),
    re_path(r'^walls/import/$', views.importWall, name='importWall'),

    # SECTION: attacks
    re_path(r'^attacks/$', views.attacksReports, name='attacks'),
    re_path(r'^attacks/list/(?P<reportId>\w+)$', views.attacksList, name='attacksList'),
    re_path(r'^attacks/manage/$', views.manageAttacks, name='manageAttacks'),
    re_path(r'^attacks/(?P<reportId>\w+)$', views.attacksReport, name='attacks'),

    # SECTION: revives
    re_path(r'^revives/$', views.revivesReports, name='revives'),
    re_path(r'^revives/manage/$', views.manageRevives, name='manageRevives'),
    re_path(r'^revives/(?P<reportId>\w+)$', views.revivesReport, name='revives'),

    # SECTION: armory
    re_path(r'^armory/$', views.armory, name='armory'),
    re_path(r'^armory/news/$', views.armoryList, name='armoryList'),

    # SECTION: big brother
    re_path(r'^bigbrother/$', views.bigBrother, name='bigBrother'),
    re_path(r'^bigbrother/remove/$', views.removeContributors, name='removeContributors'),

    # SECTION: territories
    re_path(r'^territories/$', views.territories, name='territories'),
    re_path(r'^territories/fullmap/$', views.territoriesFullMap, name='territoriesFullMap'),

    # SECTION: territories
    re_path(r'^simulator/$', views.simulator, name='simulator'),
    re_path(r'^simulator/challenge/$', views.simulatorChallenge, name='simulatorChallenge'),

]
