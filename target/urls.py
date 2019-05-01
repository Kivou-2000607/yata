from django.urls import re_path

from . import views

app_name = "target"
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^attacks/$', views.attacks, name='attacks'),
    re_path(r'^toggleTarget/(?P<targetId>\w+)$', views.toggleTarget, name='toggleTarget'),

    re_path(r'^targets/$', views.targets, name='targets'),
    re_path(r'^refresh/(?P<targetId>\w+)$', views.refresh, name='refresh'),
    re_path(r'^delete/(?P<targetId>\w+)$', views.delete, name='delete'),

    # re_path(r'^refreshTargets/(?P<select>\w+)$', views.refreshTargets, name='refreshTargets'),
    # re_path(r'^reloadAllTargets/$', views.reloadAllTargets, name='reloadAllTargets'),
    # re_path(r'^toggleTargetRefreshStatus/(?P<targetId>\w+)$', views.toggleTargetRefreshStatus, name='toggleTargetRefreshStatus'),
    # re_path(r'^changeTargetList/(?P<targetId>\w+)/(?P<newList>\w+)$', views.changeTargetList, name='changeTargetList'),

    ]
