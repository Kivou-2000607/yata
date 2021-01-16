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
from django.utils import timezone
from django.conf import settings

import requests
import os
import shutil

from bazaar.models import Item
from yata.handy import logdate


class Command(BaseCommand):
    def handle(self, **options):
        print(f"[CRON {logdate()}] START items_images")

        for item in Item.objects.all():
            image_file = os.path.join(os.path.join(settings.MEDIA_ROOT, "items"), f'{item.tId}.png')
            if not os.path.isfile(image_file):
                print(f"Missing image for {item}")
                print(image_file)
                image_url = f"https://www.torn.com/images/items/{item.tId}/large.png"
                r = requests.get(image_url, stream = True)
                r.raw.decode_content = True
                with open(image_file,'wb') as f:
                    shutil.copyfileobj(r.raw, f)

            # print(image_file, is_file)

        print(f"[CRON {logdate()}] END")
