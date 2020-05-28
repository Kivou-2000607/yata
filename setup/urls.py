from django.urls import re_path

from . import views

app_name = "setup"
urlpatterns = [
    re_path(r'^prune/$', views.prune, name='prune'),
    re_path(r'^number/$', views.number, name='number'),
    ]
