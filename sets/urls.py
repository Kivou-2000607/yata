from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('<int:tId>', views.index, name='index'),
    path('sets', views.sets, name='sets'),
    path('fullList', views.fullList, name='fullList'),
    path('logout', views.logout, name='logout'),
    path('scan', views.scan, name='scan'),
    path('updateKey', views.updateKey, name='updateKey'),
    path('updateItemBazaar', views.updateItemBazaar, name='updateItemBazaar'),
    path('deleteItemBazaar', views.deleteItemBazaar, name='deleteItemBazaar'),
    path('updateTypeBazaar', views.updateTypeBazaar, name='updateTypeBazaar'),
    path('details', views.details, name='details'),

    # path('<int:tId>', views.details, name='details'),
    ]
