from django.http import HttpResponse, HttpResponseServerError
from django.template.loader import render_to_string
from django.utils import timezone

import traceback

from player.models import Player
from player.models import News


def readNews(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            news = News.objects.last()
            news.player.add(player)
            return HttpResponse("{} maked as read".format(news.type))
        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return HttpResponseServerError(render_to_string('403.html', {'exception': message}))

    except Exception:
        print("[{:%d/%b/%Y %H:%M:%S}] ERROR 500 \n{}".format(timezone.now(), traceback.format_exc()))
        return HttpResponse(traceback.format_exc().strip())
