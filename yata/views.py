from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone

import json

from player.models import Player
from yata.handy import apiCall


def index(request):
    if request.session.get('player'):
        print('[view.yata.index] get player id from session')
        tId = request.session["player"].get("tId")
        context = {"player": Player.objects.filter(tId=tId).first()}
    else:
        context = None

    return render(request, 'yata.html', context)


def login(request):
    print('[view.yata.login] START')

    if request.method == 'POST':
        p = request.POST
        print('[view.yata.login] API call with key: {}'.format(p.get('key')))
        user = apiCall('user', '', 'profile', p.get('key'))
        if 'apiError' in user:
            print('[view.yata.login] API error: {}'.format(user))
            context = user
            return render(request, 'yata/login.html', context)

        # create/update player in the database
        player = Player.objects.filter(tId=user.get('player_id')).first()
        print('[view.yata.login] get player from database: {}'.format(player))

        if player is None:
            print('[view.yata.login] create new player')
            player = Player.objects.create(tId=int(user.get('player_id')), name=user.get('name'))
        print('[view.yata.login] update player')
        player.key = p.get('key')
        player.lastUpdateTS = int(timezone.now().timestamp())

        # if user['faction']['faction_id'] in [33241, 23952, 42435]:
        # if user['faction']['faction_id'] in [2]:
        #     print('[view.yata.login] faction allowed: {}'.format(user['faction']['faction_id']))
        #     AArights = 'chains' in apiCall('faction', user['faction']['faction_id'], 'chains', p.get('key'))
        #     factionInfo = {'factionName': user['faction']['faction_name'],
        #                    'factionId': user['faction']['faction_id'],
        #                    'AA': AArights,
        #                    }
        # else:
        #     factionInfo = {}
        # player.factionInfo = json.dumps(factionInfo)

        print('[view.yata.login] save player')
        player.save()

        print('[view.yata.login] create session')
        request.session['player'] = {'tId': player.tId, 'name': str(player), 'login': True}

        check = json.loads(p.get('check'))
        if check:
            print('[view.yata.login] set session to expirate in 1 month')
            # request.session.set_expiry(31536000)  # 1 year
            request.session.set_expiry(111600)  # 1 month
        else:
            print('[view.yata.login] set session to expirate when browser closes')
            request.session.set_expiry(0)  # logout when close browser

        context = {"player": player}
        return render(request, 'yata/login.html', context)

    else:
        return HttpResponse('Don\'t try to be a smart ass, you need to post.')


def logout(request):
    try:
        print('[view.yata.logout] delete session')
        del request.session['player']
        print('[view.yata.logout] done')
    except:
        print('[view.yata.logout] error while deleting the session')
        pass
    print('[view.yata.logout] redirect to index')
    return HttpResponseRedirect(reverse('index'))
