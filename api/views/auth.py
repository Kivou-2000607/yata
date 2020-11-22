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
# django
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.middleware.csrf import get_token

# cache and rate limit
from django.views.decorators.cache import cache_page
from ratelimit.decorators import ratelimit
from ratelimit.core import get_usage, is_ratelimited

# standards
import json
import base64

# yata
from player.models import Key

def index(request):

    # get auth
    auth = request.headers.get('Authorization')
    if auth is None:
        return JsonResponse({"error": {"code": 2, "error": "No Authorization found"}}, status=400)
    auth = auth.split()
    if len(auth) != 2:
        return JsonResponse({"error": {"code": 2, "error": "Wrong auth parameters"}}, status=400)
    if auth[0].lower() != "basic":
        return JsonResponse({"error": {"code": 2, "error": "Wrong auth parameters (needs basic auth)"}}, status=400)

    # get username and password
    uname, passwd = base64.b64decode(auth[1]).decode('utf-8').split(':')
    user = authenticate(username=uname, password=passwd)
    if user is None:
        return JsonResponse({"error": {"code": 2, "error": f"Fail to autenticate user {uname}"}}, status=400)

    # get torn API key
    api_key = request.headers.get('api-key')
    if api_key is None:
        return JsonResponse({"error": {"code": 2, "error": f"api-key not found in the request headers"}}, status=400)

    user_key = Key.objects.filter(value=api_key).first()
    if user_key is None:
        return JsonResponse({"error": {"code": 2, "error": f"Api key not registered in YATA"}}, status=400)

    # create session
    player = user_key.player
    request.session['player'] = {'tId': player.tId, 'name': str(player), 'login': True}
    request.session['json-output'] = {'tId': player.tId, 'name': str(player), 'login': True}
    request.session.set_expiry(10)
    response = JsonResponse({"auth": f"Login success {player}"}, status=200)
    response.set_cookie('csrftoken', get_token(request))
    return response
