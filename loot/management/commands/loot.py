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

from loot.models import NPC
from yata.handy import logdate
from yata.handy import clear_cf_cache
from django.core.cache import cache

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-c', '--clear-cache', action='store_true')
        parser.add_argument('-ts', '--torn-stats', action='store_true')

    def handle(self, **options):
        print(f"[CRON {logdate()}] start loot")

        # update NPC status
        for npc in NPC.objects.filter(show=True):
            print(f"[CRON {logdate()}] update {npc}")
            if options.get("torn_stats"):
                # backup plan in case of failure
                npc.update_from_torn_stats()
            else:
                npc.update()

        if options.get("clear_cache", False):
            print(f"[CRON {logdate()}] clear loot cache")
            cache.delete("context_processor_loot")
            # cache.delete("api_loot")
            r = clear_cf_cache(["https://yata.yt/api/v1/loot/", "https://yata.yt/api/v1/loot"])

        print(f"[CRON {logdate()}] end")
