from django.urls import re_path

from . import views

app_name = "bazaar"
urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^default/$', views.default, name='default'),
    re_path(r'^custom/$', views.custom, name='custom'),
    re_path(r'^sets/$', views.sets, name='sets'),
    re_path(r'^all/$', views.all, name='all'),
    re_path(r'^top10/$', views.top10, name='top10'),

    re_path(r'^update/(?P<itemId>\w+)$', views.update, name='update'),
    # re_path(r'^update/type/(?P<tType>\w+)$', views.updateType, name='updateType'),
    re_path(r'^delete/(?P<itemId>\w+)$', views.delete, name='delete'),

    re_path(r'^toggle/(?P<itemId>\w+)$', views.toggle, name='toggle'),
    re_path(r'^details/(?P<itemId>\w+)$', views.details, name='details'),
    re_path(r'^prices/(?P<itemId>\w+)$', views.prices, name='prices'),

    # re_path(r'^logout/$', views.logout, name='logout'),
    # re_path(r'^updateKey/$', views.updateKey, name='updateKey'),
    # re_path(r'^deleteItemBazaar/$', views.deleteItemBazaar, name='deleteItemBazaar'),
    # re_path(r'^updateTypeBazaar/$', views.updateTypeBazaar, name='updateTypeBazaar'),
    # re_path(r'^details/$', views.details, name='details'),

    # path('<int:tId>', views.details, name='details'),
]
