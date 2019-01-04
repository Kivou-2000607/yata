from django.urls import re_path

from . import views

app_name = "awards"
urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^crimes/$', views.crimes, name='crimes'),
    re_path(r'^drugs/$', views.drugs, name='drugs'),
    re_path(r'^attacks/$', views.attacks, name='attacks'),
    re_path(r'^items/$', views.items, name='items'),
    re_path(r'^travel/$', views.travel, name='travel'),
    re_path(r'^education/$', views.education, name='education'),
    re_path(r'^gym/$', views.gym, name='gym'),

    re_path(r'^updateKey/$', views.updateKey, name='updateKey'),
    re_path(r'^logout/$', views.logout, name='logout'),

    # path('<int:tId>', views.details, name='details'),
    ]
