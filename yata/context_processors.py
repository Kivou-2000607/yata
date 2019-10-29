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
from django.utils import timezone

from player.models import News
from player.models import Player
from player.models import Message
from player.models import SECTION_CHOICES
from loot.models import NPC


def news(request):
    if request.session.get('player'):
        tId = request.session["player"].get("tId")
        player = Player.objects.filter(tId=tId).first()
        news = News.objects.all().order_by("-date").first()
        news = False if news in player.news_set.all() or news.date > (timezone.datetime.now(timezone.utc) + timezone.timedelta(weeks=2)) else news
        return {"lastNews": news}
    else:
        return {}


def sectionMessage(request):
    if request.session.get('player'):
        section = request.get_full_path().split("/")[1]
        # HACK because faction is under /chain/
        section = 'faction' if section == 'chain' else section
        section_short = ""
        for k, v in SECTION_CHOICES:
            if v == section:
                section_short = k
        sectionMessage = Message.objects.filter(section=section_short).order_by("date").last()
        if sectionMessage is not None:
            return {"sectionMessage": sectionMessage}
        else:
            return {"sectionMessage": False}
    else:
        return {}


def nextLoot(request):
    try:
        # get smaller due time
        due = int(timezone.now().timestamp())
        for npc in NPC.objects.filter(show=True).order_by('tId'):
            due = max(min(npc.lootTimings(lvl=4)["due"], due), 0)
        return {"nextLoot": due}
    except BaseException:
        return {"nextLoot": 0}
