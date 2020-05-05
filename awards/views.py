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

from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.core.paginator import Paginator

import json
import numpy

from yata.handy import apiCall
from yata.handy import returnError
from yata.handy import getPlayer
from awards.functions import createAwards
from awards.functions import AWARDS_CAT
from player.models import Player

from awards.models import AwardsData


def index(request):
    try:
        tId = request.session["player"].get("tId") if request.session.get('player') else -1
        player = getPlayer(tId)
        awardsPlayer, awardsTorn, error = player.getAwards()

        # get graph data
        awards = awardsPlayer.get('awards')
        graph = []
        for k, h in sorted(awardsTorn.get("honors").items(), key=lambda x: x[1]["circulation"], reverse=True):
            # if h.get("rarity") not in ["Unknown Rarity"]:
            if h.get("circulation", 0) > 0:
                graph.append([h.get("name", "?"), h.get("circulation", 0), int(h.get("achieve", 0)), h.get("img", ""), h.get("rScore", 0), h.get("unreach", 0)])

        graph2 = []
        for k, h in sorted(awardsTorn.get("medals").items(), key=lambda x: x[1]["circulation"], reverse=True):
            # if h.get("rarity") not in ["Unknown Rarity"]:
            if h.get("circulation", 0) > 0:
                graph2.append([h.get("name", "?"), h.get("circulation", 0), int(h.get("achieve", 0)), h.get("img", ""), h.get("rScore", 0), h.get("unreach", 0)])

        context = {"player": player, "graph": graph, "graph2": graph2, "awardscat": True, "view": {"awards": True}}
        for k, v in awardsPlayer.items():
            context[k] = v
        if error:
            context.update(error)
        return render(request, "awards.html", context)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def list(request, type):
    try:
        tId = request.session["player"].get("tId") if request.session.get('player') else -1
        player = getPlayer(tId)
        awardsPlayer, awardsTorn, error = player.getAwards()

        print('[view.awards.list] award type: {}'.format(type))

        userInfo = awardsPlayer.get('userInfo')
        summaryByType = awardsPlayer.get('summaryByType')

        if type in AWARDS_CAT:
            awards, awardsSummary = createAwards(awardsTorn, userInfo, type)
            graph = []
            graph2 = []
            for type, honors in awards.items():
                for k, h in honors.items():
                    # if h.get("rarity", "Unknown Rarity") not in ["Unknown Rarity"]:
                    if h.get("circulation", 0) > 0:
                        if h.get("awardType") in ["Honor"]:
                            graph.append([h.get("name", "?"), h.get("circulation", 0), int(h.get("achieve", 0)), h.get("img", ""), h.get("rScore", 0), h.get("unreach", 0)])
                        elif h.get("awardType") in ["Medal"]:
                            graph2.append([h.get("name", "?"), h.get("circulation", 0), int(h.get("achieve", 0)), h.get("img", ""), h.get("rScore", 0), h.get("unreach", 0)])

            graph = sorted(graph, key=lambda x: -x[1])
            graph2 = sorted(graph2, key=lambda x: -x[1])
            context = {"player": player, "view": {"awards": True}, "awardscat": True, "awards": awards, "awardsSummary": awardsSummary, "summaryByType": summaryByType, "graph": graph, "graph2": graph2}
            if error:
                context.update(error)
            page = 'awards/list.html' if request.method == 'POST' else "awards.html"
            return render(request, page, context)

        else:
            awards = awardsPlayer.get('awards')
            graph = []
            for k, h in sorted(awardsTorn.get("honors").items(), key=lambda x: x[1]["circulation"], reverse=True):
                if h.get("circulation", 0) > 0:
                    graph.append([h.get("name", "?"), h.get("circulation", 0), int(h.get("achieve", 0)), h.get("img", ""), h.get("rScore", 0), h.get("unreach", 0)])

            graph2 = []
            for k, h in sorted(awardsTorn.get("medals").items(), key=lambda x: x[1]["circulation"], reverse=True):
                if h.get("circulation", 0) > 0:
                    graph2.append([h.get("name", "?"), h.get("circulation", 0), int(h.get("achieve", 0)), h.get("img", ""), h.get("rScore", 0), h.get("unreach", 0)])

            context = {"player": player, "view": {"awards": True}, "awardscat": True, "awards": awards, "summaryByType": summaryByType, "graph": graph, "graph2": graph2}
            page = 'awards/content-reload.html' if request.method == 'POST' else "awards.html"
            return render(request, page, context)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def hof(request):
    try:
        tId = request.session["player"].get("tId") if request.session.get('player') else -1
        player = getPlayer(tId)
        awardsPlayer, awardsTorn, error = player.getAwards()
        userInfo = awardsPlayer.get('userInfo')
        summaryByType = awardsPlayer.get('summaryByType')

        hof = [{"player": p, "rank": i + 1} for i, p in enumerate(Player.objects.order_by('-awardsScor').exclude(tId=-1))]
        hof = Paginator(hof, 50).get_page(1)

        graph = []
        for k, h in sorted(awardsTorn.get("honors").items(), key=lambda x: x[1]["circulation"], reverse=True):
            if h.get("circulation", 0) > 0:
                graph.append([h.get("name", "?"), h.get("circulation", 0), int(h.get("achieve", 0)), h.get("img", ""), h.get("rScore", 0), h.get("unreach", 0)])

        graph2 = []
        for k, h in sorted(awardsTorn.get("medals").items(), key=lambda x: x[1]["circulation"], reverse=True):
            if h.get("circulation", 0) > 0:
                graph2.append([h.get("name", "?"), h.get("circulation", 0), int(h.get("achieve", 0)), h.get("img", ""), h.get("rScore", 0), h.get("unreach", 0)])

        context = {"player": player,
                   "view": {"hof": True},
                   "nAwards": len(awardsTorn["medals"]) + len(awardsTorn["honors"]),
                   "awardscat": True,
                   "awards": awardsPlayer.get('awards'),
                   "summaryByType": summaryByType,
                   "graph": graph,
                   "graph2": graph2,
                   "hof": hof,
                   "hofGraph": json.loads(AwardsData.objects.first().hofHistogram)}
        page = 'awards/content-reload.html' if request.method == 'POST' else "awards.html"
        return render(request, page, context)

    except Exception as e:
        return returnError(exc=e, session=request.session)


def hofList(request):
    try:
        tId = request.session["player"].get("tId") if request.session.get('player') else -1
        hof = [{"player": p, "rank": i + 1} for i, p in enumerate(Player.objects.order_by('-awardsScor').exclude(tId=-1))]
        awardsTorn = AwardsData.objects.first().loadAPICall()
        return render(request, "awards/hof-list.html", {"player": getPlayer(tId),
                                                        "nAwards": len(awardsTorn["medals"]) + len(awardsTorn["honors"]),
                                                        "hof": Paginator(hof, 50).get_page(request.GET.get("p_hof"))})

    except Exception as e:
        return returnError(exc=e, session=request.session)


def bannersId(request):
    from awards.honors import d
    return HttpResponse(json.dumps(d), content_type="application/json")
