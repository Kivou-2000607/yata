from django.urls import re_path, path

from . import views

app_name = "awards"
urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^l/(?P<type>\w+)/$', views.list, name='list'),
    ]
