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

from yata.handy import apiCall


class APIKey(models.Model):
    tId = models.IntegerField(default=0)
    tName = models.CharField(max_length=16, blank=True)
    key = models.CharField(max_length=16, blank=True)
    lastCheckTS = models.IntegerField(default=0)
    status = models.BooleanField(default=True)
    error = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return "API key of {} [{}]".format(self.tName, self.tId)

    def checkKey(self):
        req = apiCall("user", "", "", self.key, verbose=False)
        if 'apiError' in req:
            self.status = False
            self.error = req['apiError']
            print("[setup.models.checkKey] {} {}".format(self, self.error))
        else:
            self.status = True
            self.tName = req.get("name", "?")
            self.tId = req.get("player_id", "0")
            self.error = ""
            print("[setup.models.checkKey] {} checked".format(self))

        self.lastCheckTS = int(timezone.now().timestamp())
        self.save()
