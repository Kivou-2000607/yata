from django.urls import re_path

from . import views

app_name = "faction"
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^configurations/$', views.configurations, name='configurations'),
    re_path(r'^configurationsKey/$', views.configurationsKey, name='configurationsKey'),
    re_path(r'^configurationsThreshold/$', views.configurationsThreshold, name='configurationsThreshold'),
    re_path(r'^configurationsPoster/$', views.configurationsPoster, name='configurationsPoster'),

    ]
