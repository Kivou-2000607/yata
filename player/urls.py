from django.urls import re_path

from . import views

app_name = "player"
urlpatterns = [
    re_path(r'^$', views.merits, name='index'),

    re_path(r'^merits/$', views.merits, name='merits'),
    re_path(r'^stats/$', views.stats, name='stats'),
    re_path(r'^gym/$', views.gym, name='gym'),
    ]
