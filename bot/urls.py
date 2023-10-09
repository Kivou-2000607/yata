from django.urls import re_path
from django.views.generic.base import RedirectView

app_name = "bot"
urlpatterns = [
    re_path(r"^$", RedirectView.as_view(url="https://bot.yata.yt", permanent=True), name="index"),
]
