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

from django.db import models
from django.utils import timezone

import json
import numpy

from yata.handy import apiCall
from setup.functions import randomKey
from awards.honors import d
from awards.functions import HONORS_UNREACH
from awards.functions import computeRarity


class AwardsData(models.Model):
    timestamp = models.IntegerField(default=0)
    apicall = models.TextField(default="{}")
    hofHistogram = models.TextField(default="{}")

    def __str__(self):
        return "Awards Data #{}".format(self.pk)

    def updateApiCall(self):
        req = apiCall("torn", "", "medals,honors", randomKey())

        if 'apiError' in req:
            print(req["apiError"])
        else:
            self.timestamp = int(timezone.now().timestamp())
            popTotal = 0
            for awardType in ["honors", "medals"]:
                to_del = []
                for k, v in req[awardType].items():
                    circulation = int(req[awardType][k].get("circulation", 0))
                    if v.get("type") in [1]:
                        to_del.append(k)
                    else:
                        if circulation > 1:
                            popTotal += 1. / computeRarity(circulation)
                    if awardType in ["honors"]:
                        req[awardType][k]["img"] = "https://awardimages.torn.com/{}.png".format(d.get(int(k), 0))
                        req[awardType][k]["unreach"] = 1 if int(k) in HONORS_UNREACH else 0
                    elif awardType in ["medals"]:
                        req[awardType][k]["img"] = "{}".format(k)
                for k in to_del:
                    del req[awardType][k]

            for awardType in ["honors", "medals"]:
                for k, v in req[awardType].items():
                    if v["circulation"] > 1:
                        req[awardType][k]["rScore"] = 100. / computeRarity(v["circulation"]) / popTotal

            self.apicall = json.dumps(req)
            self.save()

    def loadAPICall(self):
        return json.loads(self.apicall)
