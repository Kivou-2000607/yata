"""
Copyright 2020 kivou.2000607@gmail.com

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

from django.shortcuts import render, redirect

from yata.handy import getPlayer

def index(request):
    # error codes:
    # 1: server error -> status 500
    # 2: user error -> status 400
    # 3: rate limit -> 429
    # 4: torn API error -> 400
    return redirect('api:documentation')
    # return render(request, 'api.html', {'player': getPlayer(request.session.get('player', {'tId': -1})['tId'])})

def documentation(request):
    # error codes:
    # 1: server error -> status 500
    # 2: user error -> status 400
    # 3: rate limit -> 429
    # 4: torn API error -> 400

    return render(request, 'api.html', {'player': getPlayer(request.session.get('player', {'tId': -1})['tId'])})
