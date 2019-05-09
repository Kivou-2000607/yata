from django.core.management.base import BaseCommand
from django.conf import settings

import json

from player.models import Player

class Command(BaseCommand):
    def handle(self, **options):

        for player in Player.objects.all():
            player.update_info()
