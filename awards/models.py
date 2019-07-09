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

from yata.handy import apiCall


class Call(models.Model):
    timestamp = models.IntegerField(default=0)
    key = models.CharField(max_length=20)
    a = models.TextField(default="{}")

    def __str__(self):
        return f"Call #{self.pk}"

    def update(self):
        req = apiCall("torn", "", "medals,honors", self.key)
        if 'apiError' in req:
            print(req["apiError"])
        else:
            self.timestamp = int(timezone.now().timestamp())
            self.a = json.dumps(req)
            self.save()

    def load(self):
        return json.loads(self.a)
