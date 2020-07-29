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

# from player.models import News
from player.models import Player
from faction.models import Member
from player.models import Message
from player.models import SECTION_CHOICES
from loot.models import NPC


# def news(request):
#     if request.session.get('player'):
#         tId = request.session["player"].get("tId")
#         player = Player.objects.filter(tId=tId).first()
#         news = News.objects.all().order_by("-date").first()
#         news = False if news in player.news_set.all() or news.date > (timezone.datetime.now(timezone.utc) + timezone.timedelta(weeks=2)) else news
#         return {"lastNews": news}
#     else:
#         return {}

def sectionMessage(request):
    if request.session.get('player'):
        section = request.get_full_path().split("/")[1]
        section_short = ""
        for k, v in SECTION_CHOICES:
            if v == section:
                section_short = k
        sectionMessage = Message.objects.filter(section=section_short).order_by("date").last()

        # temprorary
        # del request.session['player']['seen_message']
        if request.session['player'].get('seen_message', False):
            new_player = False
        else:
            new_player = True
            tmp = dict(request.session['player'])
            tmp['seen_message'] = True
            request.session['player'] = dict(tmp)
            try:
                for member in Member.objects.filter(tId=int(request.session['player']['tId'])):
                    member.shareE = 1
                    member.shareN = 1
                    member.shareS = 1
                    member.save()

            except BaseException as e:
                print(e)
                pass


        if sectionMessage is not None:
            return {"sectionMessage": sectionMessage, "new_player": new_player}
        else:
            return {"sectionMessage": False, "new_player": new_player}
    else:
        return {}


def nextLoot(request):
    try:
        # get smaller due time
        next = NPC.objects.filter(show=True).exclude(status="Loot level V").order_by('hospitalTS').first()
        ts = max(next.lootTimings(lvl=4)["ts"], 0)
        return {"nextLoot": [next.name, next.tId, ts]}
    except BaseException:
        return {"nextLoot": ["None", 0, 0]}
