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
    print("Load models")
    load_lvl1 = ["10k_to_20b"]
    load_lvl2 = ["10k_to_100m", "100m_to_20b", "90m_to_110m"]
    load_lvl3 = ["10k_to_1m", "1m_to_100m", "100m_to_1b", "1b_to_20b"]

    MODELS = []
    MODELS.append([cloudpickle.load(open(f"nn/model_{name}.pk", "rb")) for name in load_lvl1])
    MODELS.append([cloudpickle.load(open(f"nn/model_{name}.pk", "rb")) for name in load_lvl2])
    MODELS.append([cloudpickle.load(open(f"nn/model_{name}.pk", "rb")) for name in load_lvl3])

    # MODEL = cloudpickle.load(open("model.pk", "rb"))
except Exception:
    MODELS = []


def human_format(num):
    num = float(f"{num:.3g}")
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return f"{num:f}".rstrip("0").rstrip(".") + ["", "k", "m", "b", "t"][magnitude]


def predict(models, d):
    def predict_from_single_model(m, d):
        model = m["model"]
        pipeline = m["pipeline"]
        labels = m["labels"]
        model_min = m["meta"]["stats"][0] if "meta" in m else m["min"]
        model_max = m["meta"]["stats"][1] if "meta" in m else m["max"]

        X = numpy.zeros((1, len(labels)))
        for icol, stat in enumerate(labels):  # loop over stats
            X[0, icol] = int(d.get(stat, 0))
        X, _, _ = pipeline[0].transform(X)
        yp = model.predict(X)
        yp, _, _ = pipeline[1].inverse_transform(yp)

        return yp[0], model_min, model_max

    # level 0
    lvl = 0
    prediction, model_min, model_max = predict_from_single_model(models[lvl][0], d)
    bs = prediction[1]
    # print(f"LVL1__: {human_format(model_min):>6} {human_format(model_max):>6} / {human_format(bs):>6}")

    # level 1
    lvl = 1
    i = 1 if bs > models[lvl][0]["meta"]["stats"][1] else 0
    if models[lvl][2]["meta"]["stats"][0] < bs < models[lvl][2]["meta"]["stats"][1]:
        i = 2
    prediction, model_min, model_max = predict_from_single_model(models[lvl][i], d)
    bs = prediction[1]
    # print(f"LVL2_{i}: {human_format(model_min):>6} {human_format(model_max):>6} / {human_format(bs):>6}")

    # level 2
    lvl = 2
    i = 1 if bs > models[lvl][1]["meta"]["stats"][1] else 0
    j = 1 if bs > models[lvl][2 * i]["meta"]["stats"][1] else 0
    prediction, model_min, model_max = predict_from_single_model(models[lvl][2 * i + j], d)
    bs = prediction[1]
    score = prediction[0]
    skewness = prediction[2]
    # print(f"LVL3_{2 * i + j}: {human_format(model_min):>6} {human_format(model_max):>6} / {human_format(bs):>6}")

    # print(bs, score, skewness)
    return bs, score, skewness


# @cache_page(24 * 3600)
def bs(request, target_id):
    try:
        # get cache
        response = cache.get(f"nn-stats-{target_id}", False)
        # response = False
        if response:
            print(f"[bs] {target_id} (cache)")
            return JsonResponse(response, status=200)

        # check if API key is valid with api call
        key = request.GET.get("key", False)
        if not key:
            return JsonResponse({"error": {"code": 2, "error": "No keys provided"}}, status=400)

        # test model
        if not len(MODELS):
            return JsonResponse({"error": {"code": 1, "error": "no models found"}}, status=500)

        selections = ["profile", "personalstats", "discord", "timestamp"]
        r = apiCall("user", target_id, ",".join(selections), key=key)
        if "apiError" in r:
            return JsonResponse({"error": {"code": 4, "error": r["apiErrorString"]}}, status=400)

        bs, score, skewness = predict(MODELS, r["personalstats"])
        build_type = "Defensive" if skewness < 0 else "Offensive"
        skewness = abs(int(100 * skewness))
        build_type = "Balanced" if not bs else build_type

        response = {
            r["player_id"]: {
                "total": int(bs),
                "score": int(score),
                "type": build_type,
                "skewness": int(skewness),
                "timestamp": int(time.time()),
                "version": 1,
            }
        }
        cache.set(f"nn-stats-{target_id}", response, 3600 * 24)

        return JsonResponse(response, status=200)

    except BaseException as e:
        return JsonResponse({"error": {"code": 1, "error": str(e)}}, status=500)
