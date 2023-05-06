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

import random
import time

from django.core.management.base import BaseCommand

from player.models import Key
from target.models import DogTags
from yata.handy import apiCall


class Command(BaseCommand):
    def handle(self, **options):
        keys_id = [2000607, 2002288, 1880691, 1693153]
        keys = [k.value for k in Key.objects.filter(tId__in=keys_id)]
        print(keys)

        n_calls_max = 50
        delta_t_max = 60

        n_calls = 0
        ts_start = int(time.time())
        while True:
            n_calls += 1
            delta_t = int(time.time()) - ts_start

            # test if too many api calls
            if n_calls > n_calls_max:
                print(f"too many api calls, sleeping {delta_t_max - delta_t} seconds")
                time.sleep(delta_t_max - delta_t)
                n_calls = 0
                delta_t = 0
                ts_start = int(time.time())

            # print(f"Call number {n_calls} in {delta_t} seconds (iteration ({i}))")
            for n, key in enumerate(keys):
                randomID = random.randrange(100000, 2300000)
                string = f"Use key {n} for id {randomID:07d}"
                player = apiCall(
                    "user",
                    randomID,
                    "profile,personalstats,timestamp",
                    key,
                    verbose=False,
                )

                if "apiError" in player:
                    print(string + "\tIgnore")
                    continue

                dogtags = {
                    "target_id": player.get("player_id", 0),
                    "name": player.get("name", "???"),
                    "rank": player.get("rank", "???"),
                    "level": player.get("level", 0),
                    "age": player.get("age", 0),
                    "defendslost": player.get("personalstats", {}).get("defendslost", 0),
                    "attackswon": player.get("personalstats", {}).get("attackswon", 0),
                    "last_action": player.get("last_action", {}).get("timestamp", 0),
                    "last_update": player.get("timestamp"),
                }

                _, create = DogTags.objects.get_or_create(target_id=dogtags["target_id"], defaults=dogtags)
                if create:
                    print(string + "\tTarget created")
                else:
                    print(string + "\tTarget already exists")

                # for k, v in dogtags.items():
                #     print(k, v)

            # time.sleep(2)
