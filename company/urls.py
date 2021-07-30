from django.urls import re_path
from django.shortcuts import redirect
from django.views.generic.base import RedirectView

from . import views

app_name = "company"
urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^supervise/$', views.supervise, name='supervise'),
    re_path(r'^supervise/manage$', views.manageCompany, name='manage'),
    re_path(r'^browse/$', views.browse, name='browse'),
    # re_path(r'^ws/$', views.ws, name='ws'),
]
