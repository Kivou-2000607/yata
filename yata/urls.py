"""yata URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path, re_path
from django.contrib import admin
from django.http import HttpResponse
# from django.conf import settings
# from django.conf.urls.static import static

from . import views

app_name = "yata"
urlpatterns = [
    # app
    re_path(r'^player/', include('player.urls')),
    re_path(r'^bazaar/', include('bazaar.urls')),
    re_path(r'^chain/', include('chain.urls')),
    re_path(r'^awards/', include('awards.urls')),
    re_path(r'^target/', include('target.urls')),
    re_path(r'^stock/', include('stock.urls')),
    re_path(r'^loot/', include('loot.urls')),
    re_path(r'^bot/', include('bot.urls')),
    path('admin/', admin.site.urls),

    # site
    path('', views.index, name="index"),
    path('login', views.login, name="login"),
    path('logout', views.logout, name="logout"),
    path('delete', views.delete, name="delete"),
    path('analytics', views.analytics, name="analytics"),

    # robot.txt
    path('robots.txt', lambda x: HttpResponse("User-Agent: *\nDisallow: /", content_type="text/plain"), name="robots_file"),

]
