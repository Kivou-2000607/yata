from django.urls import re_path

from . import views

app_name = "stocks"
urlpatterns = [
    # re_path(r'^$', views.index, name='index'),
    #
    # re_path(r'^list/$', views.index, name='list'),
    # re_path(r'^list/(?P<select>\w+)$', views.index, name='list'),
    # re_path(r'^details/(?P<tId>\w+)$', views.details, name='details'),
    # re_path(r'^prices/(?P<tId>\w+)$', views.prices, name='prices'),
    # re_path(r'^prices/(?P<tId>\w+)/(?P<period>\w+)$', views.prices, name='prices'),
]
