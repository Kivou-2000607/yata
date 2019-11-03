from django.urls import re_path

from . import views

app_name = "bot"
urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^updateId/$', views.updateId, name='updateId'),
    re_path(r'^togglePref/(?P<type>\w+)/$', views.togglePref, name='togglePref'),

    ]
