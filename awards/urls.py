from django.urls import re_path

from . import views

app_name = "awards"
urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^bannersId/$', views.bannersId, name='bannersId'),
    re_path(r'^hof/$', views.hof, name='hof'),
    re_path(r'^hof/list$', views.hofList, name='hofList'),
    re_path(r'^(?P<type>\w+)/$', views.list, name='list'),
    ]
