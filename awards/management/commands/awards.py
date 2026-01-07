from django.core.management.base import BaseCommand
from django.conf import settings

from awards.models import AwardsData
from yata.handy import logdate

import os
import shutil
import requests


class Command(BaseCommand):
    help = "Download honor images (use --force to re-download existing files)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force re-download of honor images even if they already exist",
        )

    def handle(self, **options):
        force = options["force"]

        print(f"[CRON {logdate()}] START awards (force={force})")

        d = AwardsData.objects.first()
        d.updateApiCall()

        honors = d.loadAPICall()["honors"].items()
        n = len(honors)

        for i, (k, v) in enumerate(honors):
            image_file = os.path.join(
                settings.MEDIA_ROOT,
                "honors",
                f"{k}.png"
            )

            if os.path.isfile(image_file) and not force:
                continue

            action = "Re-downloading" if force and os.path.isfile(image_file) else "Downloading"
            print(
                f"{i + 1:03d}/{n:03d} {action} image for honor {v['name']} [{k}]",
                end="..."
            )

            image_url = f"https://www.torn.com/images/honors/{k}/f.png"
            r = requests.get(image_url, stream=True)

            if r.status_code != 200:
                print(f" error ({r.status_code})")
                continue

            os.makedirs(os.path.dirname(image_file), exist_ok=True)

            r.raw.decode_content = True
            with open(image_file, "wb") as f:
                shutil.copyfileobj(r.raw, f)

            print(" done")

        print(f"[CRON {logdate()}] END")
