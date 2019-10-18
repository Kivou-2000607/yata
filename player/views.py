from django.shortcuts import render
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


def prune(request):
    try:
        if request.session.get('player'):
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()

            players = Player.objects.all()
            nTotal = len(players)

            nValid = len(players.filter(active=True).exclude(validKey=False))
            nInact = len(players.filter(active=False))
            nInval = len(players.filter(validKey=False))

            prune = Player.objects.filter(active=False).exclude(validKey=True)
            nPrune = len(prune)

            context = {"player": player, "nTotal": nTotal, "nInact": nInact, "nValid": nValid, "nInval": nInval, "nPrune": nPrune, "prune": prune}
            return render(request, "player.html", context)
        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()
