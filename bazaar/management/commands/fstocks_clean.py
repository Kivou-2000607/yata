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

import json
import os

from bazaar.models import AbroadStocks


wrong_items = {

  "mex" : [159, 432, 426, 260, 230, 99, 259, 110, 8, 175, 178, 111, 258, 26, 229, 409, 20, 231, 232, 177, 11, 327, 640, 107, 31, 50, 108, 21, 63, 399],

  "cay" : [618, 620, 619, 617, 626, 623, 624, 616, 622, 621, 625, 613, 612, 614, 615],

  "can" : [261, 253, 262, 263, 252, 402, 410, 413, 254, 645, 328, 196, 197, 201, 205, 206],

  "haw" : [243, 264, 265, 241, 242, 430, 419, 420, 421, 240],

  "uni" : [266, 439, 431, 218, 268, 416, 267, 221, 418, 220, 438, 411, 408, 415, 641, 217, 219, 397, 196, 197, 198, 201, 203, 205, 206],

  "arg" : [270, 269, 271, 407, 256, 257, 391, 255, 333, 196, 198, 199, 203, 204],

  "swi" : [273, 272, 224, 436, 222, 223, 361, 398, 435, 196, 198, 199, 201, 203, 204],

  "jap" : [429, 294, 427, 277, 433, 239, 238, 234, 434, 235, 278, 236, 279, 233, 237, 395, 334, 197, 198, 200, 203, 204, 205, 206],

  "chi" : [274, 246, 245, 244, 276, 249, 275, 247, 250, 335, 251, 326, 248, 400, 197, 199, 200, 201, 204],

  "uae" : [385, 412, 384, 414, 440, 381, 383, 386, 387, 388, 382],

  "sou" : [281, 280, 227, 4, 282, 228, 226, 406, 225, 654, 653, 652, 651, 332, 199, 200, 201, 203, 206],

}

class Command(BaseCommand):
    def handle(self, **options):

        stocks = AbroadStocks.objects.all()
        for country_key, items_id in wrong_items.items():
            print(stocks.filter(country_key=country_key).exclude(item__id__in=items_id).delete())
