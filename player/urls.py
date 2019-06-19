from django.urls import re_path

from . import views

app_name = "player"
urlpatterns = [
    # re_path(r'^$', views.index, name='index'),

    re_path(r'^readNews/$', views.readNews, name='readNews'),
    ]
