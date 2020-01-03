from django.urls import re_path

from . import views

app_name = "target"
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^attacks/$', views.attacks, name='attacks'),
    re_path(r'^targets/$', views.targets, name='targets'),
    re_path(r'^revives/$', views.revives, name='revives'),

    re_path(r'^toggleTarget/(?P<targetId>\w+)$', views.toggleTarget, name='toggleTarget'),
    re_path(r'^toggleRevive/$', views.toggleRevive, name='toggleRevive'),

    re_path(r'^updateNote/$', views.updateNote, name='updateNote'),
    re_path(r'^refresh/(?P<targetId>\w+)$', views.refresh, name='refresh'),
    re_path(r'^delete/(?P<targetId>\w+)$', views.delete, name='delete'),
    re_path(r'^add/$', views.add, name='add'),
    ]
