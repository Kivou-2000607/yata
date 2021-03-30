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
from django.forms.models import model_to_dict

import datetime
import random
import string
import requests
import json
from decouple import config
HISTORY_TIMES = {
    "one_day": 86400,
    "one_week": 604800,
    "two_weeks": 1209600,
    "one_month": 2678400,
    "two_months": 5356800,
    "three_months": 8035200,
    "six_months": 16070400,
    "one_year": 32140800,
    "two_years": 64281600,
}


def histTime(key):
    return " ".join([k for k in key.split("_")])

def datestr():
    now = datetime.datetime.utcnow()
    return f'{now.year}-{now.month:02d}-{now.day:02d} {now.hour:02d}:{now.minute:02d}:{now.second:02d}'

def tsnow():
    return int(timezone.now().timestamp())

def logdate():
    now = datetime.datetime.utcnow()
    return f'{now.year}-{now.month:02d}-{now.day:02d} {now.hour:02d}:{now.minute:02d}:{now.second:02d}'

def isProxyKey(key):
    # return True if isinstance(key, str) and len(key) == 32 else False
    return False



def apiCall(section, id, selections, key, sub=None, verbose=True):
    import requests

    key = str(key)
    proxy = isProxyKey(key)
    # DEBUG live chain
    # if selections in ["chain", "chain,timestamp"] and section == "faction":
    #     from django.utils import timezone
    #     print("[yata.function.apiCall] DEBUG chain/faction")
    #     chain = dict({"timestamp": int(timezone.now().timestamp())-4,
    #                   "chain": {"current": 76,
    #                             "timeout": 8,
    #                             "max": 100,
    #                             "modifier": 0.75,
    #                             "cooldown": 0,
    #                             "start": 1555211268
    #                             }})
    #     if sub is None:
    #         return chain
    #     else:
    #         return chain.get(sub)

    # DEBUG API error
    # return dict({"apiError": "API error code 42: debug error."})

    base_url = "https://torn-proxy.com" if proxy else "https://api.torn.com"
    url = f'{base_url}/{section}/{id}?selections={selections}&key={key}&comment={config("API_HOST", default="-")}'

    if verbose:
        print("[yata.function.apiCall] {}".format(url.replace("&key=" + key, "")))

    try:
        r = requests.get(url)
    except BaseException as e:
        return apiCallError({"error": {"code": 0, "error": f"can't reach {base_url}"}})

    err = False

    try:
        rjson = r.json()
    except ValueError as e:
        print("[yata.function.apiCall] API deserialization  error {}".format(e))
        err = dict({"error": {"code": 0, "error": "deserialization error... API going crazy #blameched"}})

    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("[yata.function.apiCall] API HTTPError {}".format(e))
        err = dict({"error": {"code": r.status_code, "error": "{} #blameched".format(r.reason)}})

    if not err:
        if "error" in rjson:  # standard api error
            err = rjson
        else:
            if sub is not None:
                if sub in rjson:
                    return rjson[sub]
                else:  # key not found
                    err = dict({"error": {"code": "", "error": "key not found... something went wrong..."}})
            else:
                return rjson
    return apiCallError(err)


def apiCallError(err):
    if err.get("proxy", False):
        # if err["proxy_code"] == 1 or err["proxy_code"] == 2:
        return {"apiError": f'Proxy error {err["proxy_code"]}: {err["proxy_error"]}',
                "apiErrorString": err["proxy_error"],
                "apiErrorCode": int(err["code"])}  # send API code instead of proxy code to have same behavior
    else:
        return {"apiError": "API error {}: {}.".format(err["error"]["code"], err["error"]["error"]),
                 "apiErrorString": err["error"]["error"],
                 "apiErrorCode": int(err["error"]["code"])}


def timestampToDate(timestamp, fmt=False):
    import datetime
    import pytz
    d = datetime.datetime.fromtimestamp(timestamp, tz=pytz.UTC)
    if fmt is False:
        return d
    elif type(fmt) == bool and fmt:
        return d.strftime("%Y/%m/%d %H:%M TCT")
    else:
        return d.strftime(fmt)


def cleanhtml(raw_html):
    import re
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def getPlayer(tId, skipUpdate=False, forceUpdate=False):
    from player.models import Player
    from player.functions import updatePlayer
    from django.http import HttpResponseForbidden
    from django.template.loader import render_to_string

    if skipUpdate:
        return Player.objects.filter(tId=tId).first()

    player, _ = Player.objects.get_or_create(tId=tId)
    player.lastActionTS = tsnow()
    player.active = True

    if tsnow() - player.lastUpdateTS > 3600 or forceUpdate:
        updatePlayer(player)

    player.save()
    return player


def getFool(tId):
    from player.models import Player
    from player.functions import updatePlayer

    player, _ = Player.objects.get_or_create(tId=tId)
    player.fight_club_gym_access = False

    return player


def randomSlug(length=32):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def returnError(type=500, exc=None, msg=None, home=True, session=None):
    import traceback
    from django.utils import timezone
    from django.shortcuts import redirect
    from django.urls import reverse
    from django.http import HttpResponseServerError
    from django.http import HttpResponseForbidden
    from django.http import HttpResponseNotFound
    from django.http import JsonResponse
    from django.template.loader import render_to_string
    from player.models import Player
    from django.conf import settings


    if session is not None and session.get('json-output'):
        return JsonResponse({'error': {'code': 1, 'error': 'Unkown error' if exc is None else str(exc)}}, status=type)

    if type == 403:
        msg = "Permission Denied" if msg is None else msg
        return HttpResponseForbidden(render_to_string('403.html', {'exception': msg, 'home': home, 'redirect': msg == "You might want to log in."}))
    if type == 404:
        msg = "Not Found" if msg is None else msg
        return HttpResponseNotFound(render_to_string('404.html', {'exception': msg, 'home': home}))
    else:
        message = traceback.format_exc().strip()
        print(exc)
        print(message)
        if session is not None and session.get("player", False):
            player = getPlayer(session["player"].get("tId"))
        else:
            player = Player.objects.filter(tId=-1).first()
        defaults = {"timestamp": tsnow()}
        try:
            if settings.SENTRY:
                from sentry_sdk import capture_exception
                capture_exception(exc)
            player.error_set.update_or_create(short_error=exc, long_error=message, defaults=defaults)
        except BaseException as e:
            print("Meta error", e)
        return HttpResponseServerError(render_to_string('500.html', {'exception': exc, 'home': home}))


def clear_cf_cache(urls):
    if config("ENABLE_CF", False):
        headers = {
            "X-Auth-Email": config("CF_EMAIL"),
            "X-Auth-Key": config("CF_API_KEY"),
        }
        data = {"files": urls}
        r = requests.post(f'https://api.cloudflare.com/client/v4/zones/{config("CF_ZONE")}/purge_cache', json=data, headers=headers)
        return r.json()
    else:
        return {'result': {'id': None}, 'success': False, 'errors': [], 'messages': ["No cloudflare configurations found"]}


def get_payload(request):
    if len(request.POST):
        return request.POST

    try:
        return json.loads(request.body)
    except BaseException as e:
        print(f"[handy.get_payload] {e}")
        string = request.body.decode('utf-8').replace("'", "\"")
        return json.loads(string)


def json_context(context):
    from django.db import models

    for k, v in context.items():
        if isinstance(v, models.query.QuerySet):
            # print(k, "queryset")
            context[k] = [sub_v.json() for sub_v in v]
        elif isinstance(v, models.Model):
            context[k] = v.json()
            # print(k, "model")
        # else:
        #     print(k, "?", type(v))
    return context
