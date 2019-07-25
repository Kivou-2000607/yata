from django.urls import re_path

from . import views

app_name = "stock"
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^list/$', views.list, name='list'),

]
