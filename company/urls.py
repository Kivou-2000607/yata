from django.urls import re_path

from . import views

app_name = "company"
urlpatterns = [
    re_path(r"^$", views.index, name="index"),
    re_path(r"^supervise/$", views.supervise, name="supervise"),
    re_path(r"^supervise/manage/$", views.manageCompany, name="manage"),
    re_path(r"^supervise/financials/$", views.monthlyFinancials, name="financials"),
    re_path(r"^browse/$", views.browse, name="browse"),
    re_path(r"^browse/companies/$", views.companies, name="companies"),
    # re_path(r'^ws/$', views.ws, name='ws'),
]
