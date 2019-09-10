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

from django.shortcuts import render
from django.utils import timezone

import json
import numpy

from yata.handy import apiCall
from yata.handy import returnError
from awards.functions import createAwards
from awards.functions import updatePlayerAwards
from awards.functions import AWARDS_CAT
from player.models import Player
from awards.models import Call


def index(request):
    try:
        if request.session.get('player'):
            print('[view.awards.index] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            awardsJson = json.loads(player.awardsJson)
            userInfo = awardsJson.get('userInfo')

            error = False
            tornAwards = Call.objects.first().load()
            userInfo = apiCall('user', '', 'personalstats,crimes,education,battlestats,workstats,perks,networth,merits,profile,medals,honors,icons', player.key)
            if 'apiError' in userInfo:
                error = userInfo
            else:
                print("[view.awards.index] update awards")
                awardsJson["userInfo"] = userInfo
                player.awardsJson = json.dumps(awardsJson)
                updatePlayerAwards(player, tornAwards, userInfo)
                player.save()

            # get graph data
            awards = awardsJson.get('awards')
            graph = []
            for k, h in sorted(tornAwards.get("honors").items(), key=lambda x: x[1]["circulation"], reverse=True):
                # if h.get("rarity") not in ["Unknown Rarity"]:
                if h.get("circulation", 0) > 0:
                    graph.append([h.get("name", "?"), h.get("circulation", 0), int(h.get("achieve", 0)), h.get("img", ""), h.get("rScore", 0), h.get("unreach", 0)])

            graph2 = []
            for k, h in sorted(tornAwards.get("medals").items(), key=lambda x: x[1]["circulation"], reverse=True):
                # if h.get("rarity") not in ["Unknown Rarity"]:
                if h.get("circulation", 0) > 0:
                    graph2.append([h.get("name", "?"), h.get("circulation", 0), int(h.get("achieve", 0)), h.get("img", ""), h.get("rScore", 0), h.get("unreach", 0)])

            context = {"player": player, "graph": graph, "graph2": graph2, "awardscat": True, "view": {"awards": True}}
            for k, v in json.loads(player.awardsJson).items():
                context[k] = v
            if error:
                context.update(error)
            return render(request, "awards.html", context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()


def list(request, type):
    try:
        if request.session.get('player'):
            print('[view.awards.list] get player id from session')
            tId = request.session["player"].get("tId")
            player = Player.objects.filter(tId=tId).first()
            player.lastActionTS = int(timezone.now().timestamp())
            player.save()

            awardsJson = json.loads(player.awardsJson)
            print('[view.awards.list] award type: {}'.format(type))

            tornAwards = Call.objects.first().load()
            userInfo = awardsJson.get('userInfo')
            summaryByType = awardsJson.get('summaryByType')

            if type in AWARDS_CAT:
                awards, awardsSummary = createAwards(tornAwards, userInfo, type)
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
                page = 'awards/list.html' if request.method == 'POST' else "awards.html"
                return render(request, page, context)

            elif type == "all":
                awards = awardsJson.get('awards')
                graph = []
                updatePlayerAwards(player, tornAwards, userInfo)
                for k, h in sorted(tornAwards.get("honors").items(), key=lambda x: x[1]["circulation"], reverse=True):
                    if h.get("circulation", 0) > 0:
                        graph.append([h.get("name", "?"), h.get("circulation", 0), int(h.get("achieve", 0)), h.get("img", ""), h.get("rScore", 0), h.get("unreach", 0)])

                graph2 = []
                for k, h in sorted(tornAwards.get("medals").items(), key=lambda x: x[1]["circulation"], reverse=True):
                    if h.get("circulation", 0) > 0:
                        graph2.append([h.get("name", "?"), h.get("circulation", 0), int(h.get("achieve", 0)), h.get("img", ""), h.get("rScore", 0), h.get("unreach", 0)])

                context = {"player": player, "view": {"awards": True}, "awardscat": True, "awards": awards, "summaryByType": summaryByType, "graph": graph, "graph2": graph2}
                page = 'awards/content-reload.html' if request.method == 'POST' else "awards.html"
                return render(request, page, context)

            elif type == "hof":
                hof = []
                hofGraph = []
                for p in Player.objects.exclude(awardsInfo="N/A").all():
                    try:
                        hof.append({"player": p,
                                    "rscore": float(p.awardsInfo),
                                    # "nAwarded": json.loads(p.awardsJson)["summaryByType"]["AllHonors"]["nAwarded"],
                                    # "nAwards": json.loads(p.awardsJson)["summaryByType"]["AllHonors"]["nAwards"],
                                    "nAwarded": json.loads(p.awardsJson)["summaryByType"]["AllAwards"]["nAwarded"],
                                    "nAwards": json.loads(p.awardsJson)["summaryByType"]["AllAwards"]["nAwards"],
                                    })
                        hofGraph.append(float(p.awardsInfo))
                    except BaseException:
                        print('[view.awards.list] error getting info on {}'.format(p))

                awards = awardsJson.get('awards')
                graph = []
                updatePlayerAwards(player, tornAwards, userInfo)
                for k, h in sorted(tornAwards.get("honors").items(), key=lambda x: x[1]["circulation"], reverse=True):
                    if h.get("circulation", 0) > 0:
                        graph.append([h.get("name", "?"), h.get("circulation", 0), int(h.get("achieve", 0)), h.get("img", ""), h.get("rScore", 0), h.get("unreach", 0)])

                graph2 = []
                for k, h in sorted(tornAwards.get("medals").items(), key=lambda x: x[1]["circulation"], reverse=True):
                    if h.get("circulation", 0) > 0:
                        graph2.append([h.get("name", "?"), h.get("circulation", 0), int(h.get("achieve", 0)), h.get("img", ""), h.get("rScore", 0), h.get("unreach", 0)])

                bins = numpy.logspace(-2, 2, num=101)
                bins[0] = 0
                histo, _ = numpy.histogram(hofGraph, bins=bins)
                cBins = [0.5 * float(a + b) for a, b in zip(bins[:-1], bins[1:])]
                hofGraph = [[x, y, xm, xp, 0] for x, y, xm, xp in zip(cBins, histo, bins[:-1], bins[1:])]
                hofGraph[0][4] = hofGraph[0][1]
                for i in range(len(hofGraph) - 1):
                    hofGraph[i + 1][4] = hofGraph[i + 1][1] + hofGraph[i][4]
                context = {"player": player, "view": {"hof": True}, "awardscat": True, "awards": awards, "summaryByType": summaryByType, "graph": graph, "graph2": graph2, "hof": sorted(hof, key=lambda x: -x["rscore"]), "hofGraph": hofGraph}
                page = 'awards/content-reload.html' if request.method == 'POST' else "awards.html"
                return render(request, page, context)

        else:
            return returnError(type=403, msg="You might want to log in.")

    except Exception:
        return returnError()
