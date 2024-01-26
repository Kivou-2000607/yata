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

from django.core.management.base import BaseCommand
from django.conf import settings

from awards.models import AwardsData
from yata.handy import logdate

import os
import shutil
import requests

class Command(BaseCommand):
    def handle(self, **options):
        print(f"[CRON {logdate()}] START awards")
        d = AwardsData.objects.first()
        d.updateApiCall()

        honors = d.loadAPICall()["honors"].items()
        n = len(honors)
        for i, (k, v) in enumerate(honors):
            image_file = os.path.join(os.path.join(settings.MEDIA_ROOT, "honors"), f'{k}.png')

            if not os.path.isfile(image_file):
                print(f'{i + 1:03.0f}/{n:03.0f} Missing image for honor {v["name"]} [{k}]', end="...")
                image_url = f"https://www.torn.com/images/honors/{k}/f.png"
                # print(image_file, image_url)
                r = requests.get(image_url, stream = True)
                if not r.status_code == 200:
                    print(f" error downloading {r}")
                    continue
                r.raw.decode_content = True
                with open(image_file,'wb') as f:
                    shutil.copyfileobj(r.raw, f)

                print(f" downloaded {r}")


        print(f"[CRON {logdate()}] END")
