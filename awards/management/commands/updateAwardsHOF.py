from django.core.management.base import BaseCommand
from django.conf import settings

import json
import os
from player.models import Player
from yata.handy import apiCall
from awards.functions import updatePlayerAwards

class Command(BaseCommand):
    def handle(self, **options):
        for player in Player.objects.exclude(awardsInfo="N/A").all():
            print("[command.awards.updateAwardsHOF] update player {}".format(player))
            key = player.key
            # key = ""

            error = False
            tornAwards = apiCall('torn', '', 'honors,medals', key)
            if 'apiError' in tornAwards:
                error = tornAwards
                # return render(request, 'errorPage.html', tornAwards)

            userInfo = apiCall('user', '', 'personalstats,crimes,education,battlestats,workstats,perks,networth,merits,profile,medals,honors,icons', key)
            if 'apiError' in userInfo:
                error = userInfo
                # return render(request, 'errorPage.html', userInfo)

            if not error:
                updatePlayerAwards(player, tornAwards, userInfo)
                print("[command.awards.updateAwardsHOF] update done")
            else:
                print("[command.awards.updateAwardsHOF] error updating")
