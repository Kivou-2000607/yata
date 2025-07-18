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
from django.views.generic.base import RedirectView
from .views import bot_redirect
# for media and admin url obfuscation
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from . import views
from setup import views as setup_views

# for shared reports
from faction.views import report as chainReport
from faction.views import attacksReport
from faction.views import revivesReport
from company.views import supervise


# sentry
def trigger_error(request):
    division_by_zero = 1 / 0


app_name = "yata"
urlpatterns = [
    # app
    re_path(r"^player/", include("player.urls")),
    re_path(r"^bazaar/", include("bazaar.urls")),
    re_path(r"^awards/", include("awards.urls")),
    re_path(r"^target/", include("target.urls")),
    re_path(r"^loot/", include("loot.urls")),
    re_path(r"^faction/", include("faction.urls")),
    re_path(r"^setup/", include("setup.urls")),
    re_path(r"^api/", include("api.urls")),
    re_path(r"^company/", include("company.urls")),
    path(f"admin/", admin.site.urls),
    # site
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("delete", views.delete, name="delete"),
    path("update_session", views.update_session, name="update_session"),
    path(
        "discord",
        RedirectView.as_view(url="https://discord.gg/75J3VEWrwe"),
        name="discord",
    ),
    path("bot", bot_redirect, name="bot"),
    path("tos", views.tos, name="tos"),
    # robot.txt
    path(
        "robots.txt",
        lambda x: HttpResponse("User-Agent: *\nDisallow: /", content_type="text/plain"),
        name="robots_file",
    ),
    # shared reports
    path("<slug:share>/chains/<slug:chainId>/", chainReport, name="chainReport"),
    path("<slug:share>/attacks/<slug:reportId>/", attacksReport, name="attacksReport"),
    path("<slug:share>/revives/<slug:reportId>/", revivesReport, name="revivesReport"),
    path("share/company/<slug:shareId>/", supervise, name="company"),
    # sentry
    path("sentry-debug/", trigger_error),
    # redirect default favicon
    path(
        "favicon.ico", RedirectView.as_view(url="/static/favicon.ico", permanent=True)
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
