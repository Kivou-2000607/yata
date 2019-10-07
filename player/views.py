from django.http import HttpResponse
from django.utils import timezone

from player.models import Player
from player.models import News
from yata.handy import returnError


def readNews(request):
    try:
        if request.session.get('player') and request.method == 'POST':
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            news = News.objects.last()
            news.player.add(player)
            return HttpResponse("{} marked as read".format(news.type))
        else:
            message = "You might want to log in." if request.method == "POST" else "You need to post. Don\'t try to be a smart ass."
            return returnError(type=403, msg=message)

    except Exception:
        return returnError()
