from django.urls import re_path

from . import views

app_name = "awards"
urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^crimes/$', views.crimes, name='crimes'),
    re_path(r'^drugs/$', views.drugs, name='drugs'),
    re_path(r'^attacks/$', views.attacks, name='attacks'),
    re_path(r'^faction/$', views.faction, name='faction'),
    re_path(r'^items/$', views.items, name='items'),
    re_path(r'^travel/$', views.travel, name='travel'),
    re_path(r'^work/$', views.work, name='work'),
    re_path(r'^gym/$', views.gym, name='gym'),
    re_path(r'^money/$', views.money, name='money'),
    re_path(r'^competitions/$', views.competitions, name='competitions'),
    re_path(r'^commitment/$', views.commitment, name='commitment'),
    re_path(r'^miscellaneous/$', views.miscellaneous, name='miscellaneous'),

    re_path(r'^updateKey/$', views.updateKey, name='updateKey'),
    re_path(r'^logout/$', views.logout, name='logout'),

    # path('<int:tId>', views.details, name='details'),
    ]
