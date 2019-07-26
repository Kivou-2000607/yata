from django.urls import re_path

from . import views

app_name = "stock"
urlpatterns = [
    re_path(r'^$', views.list, name='index'),

    re_path(r'^list/$', views.list, name='list'),
    re_path(r'^details/(?P<tId>\w+)$', views.details, name='details'),
    re_path(r'^prices/(?P<tId>\w+)$', views.prices, name='prices'),

]
