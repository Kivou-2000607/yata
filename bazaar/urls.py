from django.urls import re_path

from . import views

app_name = "bazaar"
urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^default/$', views.default, name='default'),
    re_path(r'^custom/$', views.custom, name='custom'),
    re_path(r'^sets/$', views.sets, name='sets'),
    re_path(r'^fullList/$', views.fullList, name='fullList'),
    re_path(r'^logout/$', views.logout, name='logout'),
    re_path(r'^scan/$', views.scan, name='scan'),
    re_path(r'^updateKey/$', views.updateKey, name='updateKey'),
    re_path(r'^updateItemBazaar/$', views.updateItemBazaar, name='updateItemBazaar'),
    re_path(r'^deleteItemBazaar/$', views.deleteItemBazaar, name='deleteItemBazaar'),
    re_path(r'^updateTypeBazaar/$', views.updateTypeBazaar, name='updateTypeBazaar'),
    re_path(r'^toggleItem/$', views.toggleItem, name='toggleItem'),
    re_path(r'^details/$', views.details, name='details'),

    # path('<int:tId>', views.details, name='details'),
    ]
# from django.urls import path
#
# from . import views
#
# # app_name = "bazaar"
# urlpatterns = [
#     path('', views.index, name='index'),
#     path('default', views.default, name='default'),
#     path('custom', views.custom, name='custom'),
#     path('sets', views.sets, name='sets'),
#     path('fullList', views.fullList, name='fullList'),
#     path('logout', views.logout, name='logout'),
#     path('scan', views.scan, name='scan'),
#     path('updateKey', views.updateKey, name='updateKey'),
#     path('updateItemBazaar', views.updateItemBazaar, name='updateItemBazaar'),
#     path('deleteItemBazaar', views.deleteItemBazaar, name='deleteItemBazaar'),
#     path('updateTypeBazaar', views.updateTypeBazaar, name='updateTypeBazaar'),
#     path('toggleItem', views.toggleItem, name='toggleItem'),
#     path('details', views.details, name='details'),
#
#     # path('<int:tId>', views.details, name='details'),
#     ]
