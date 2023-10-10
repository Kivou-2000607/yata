# Copyright 2020 kivou.2000607@gmail.com
#
# This file is part of yata.
#
#     yata is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     any later version.
#
#     yata is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with yata. If not, see <https://www.gnu.org/licenses/>.

import time

import cloudpickle

# from django.views.decorators.cache import cache_page
import numpy

# import json
#
from django.core.cache import cache
from django.http import JsonResponse

# from django.views.decorators.csrf import csrf_exempt
# from scipy import stats
#
# from faction.models import Faction
from yata.handy import apiCall

try:
    MODEL = cloudpickle.load(open("model.pk", "rb"))
except Exception as e:
    MODEL = str(e)


# @cache_page(24 * 3600)
def bs(request, target_id):
    try:

        # get cache
        response = cache.get(f"nn-stats-{target_id}", False)
        if response:
            print(f"[bs] {target_id} (cache)")
            return JsonResponse(response, status=200)

        # check if API key is valid with api call
        key = request.GET.get("key", False)
        if not key:
            return JsonResponse({"error": {"code": 2, "error": "No keys provided"}}, status=400)

        # test model
        if isinstance(MODEL, str):
            return JsonResponse({"error": {"code": 1, "error": MODEL}}, status=500)

        selections = ["profile", "personalstats", "discord", "timestamp"]
        r = apiCall("user", target_id, ",".join(selections), key=key)
        if "apiError" in r:
            return JsonResponse({"error": {"code": 4, "error": r["apiErrorString"]}}, status=400)

        model = MODEL["model"]
        pipeline = MODEL["pipeline"]
        labels = MODEL["labels"]

        X = numpy.zeros((1, len(labels)))
        for icol, stat in enumerate(labels):  # loop over stats
            X[0, icol] = int(r["personalstats"].get(stat, 0))
        X, _, _ = pipeline[0].transform(X)

        yp = model.predict(X)
        yp, _, _ = pipeline[1].inverse_transform(yp)
        bs = int(yp[0][0])
        build_type = "Defensive" if yp[0][6] < 0 else "Offensive"
        skewness = abs(int(100 * yp[0][6]))
        build_type = "Balanced" if not bs else build_type

        response = {r["player_id"]: {"total": int(yp[0][0]), "type": build_type, "skewness": skewness, "timestamp": int(time.time())}}
        cache.set(f"nn-stats-{target_id}", response, 3600 * 24)

        return JsonResponse(response, status=200)

    except BaseException as e:
        return JsonResponse({"error": {"code": 1, "error": str(e)}}, status=500)
