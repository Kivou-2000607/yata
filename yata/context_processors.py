"""
Copyright 2019 kivou.2000607@gmail.com

This file is part of yata.

    yata is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    yata is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with yata. If not, see <https://www.gnu.org/licenses/>.
"""
from player.models import News
from player.models import Player
from django.utils import timezone


def news(request):
    if request.session.get('player'):
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        news = News.objects.all().order_by("-date").first()
        news = False if news in player.news_set.all() or news.date > (timezone.datetime.now(timezone.utc) + timezone.timedelta(weeks=2)) else news
        return {"lastNews": news}
    else:
        print("[yata.context_processors.news] out")
        return {}
