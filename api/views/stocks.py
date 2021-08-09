# """
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
# """
# # django
# from django.http import JsonResponse
# from django.views.decorators.cache import cache_page
# from django.core import serializers
#
# import json
#
# from stocks.models import Stock
#
#
# @cache_page(60)
# def getStocks(request):
#     try:
#         stocks = Stock.objects.all()
#         stocks_dict = {}
#         for stock in json.loads(serializers.serialize('json', stocks)):
#             stocks_dict[stock["fields"]["torn_id"]] = { k: round(v, 2) if isinstance(v, float) else v for k, v in stock["fields"].items() if k not in ["torn_id", "description", "name"] }
#             # if request.GET.get("history"):
#             #     history = {}
#             #     fetch_back = int(request.GET.get("history")) if request.GET.get("history").isdigit() else 3600
#             #     for h in stocks.filter(torn_id=stock["fields"]["torn_id"]).first().history_set.filter(timestamp__gte=(int(time.time()) - fetch_back)):
#             #         history[str(h.timestamp)] = h.current_price
#             #     stocks_dict[stock["fields"]["torn_id"]]["history"] = history
#
#         # get data from payload
#         return JsonResponse({"stocks": stocks_dict}, status=200)
#
#     except BaseException as e:
#         return JsonResponse({"message": f"Server error: {e}"}, status=500)
