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

from bot.models import Preference
from bot.models import BotData

from discord import Client


class Notifications(Client):

    async def on_ready(self):
        prefs = Preference.objects.all()
        for p in prefs:
            user = self.get_user(int(p.player.dId))

            if user is None:
                p.yataServer = False
            else:
                p.yataServer = True
                p.yataServerName = user.name

            p.save()
            print(p, p.yataServer, p.yataServerName)

            if p.hasNotifications() and p.yataServer:
                if user is None:
                    print("\tuser not found")
                else:
                    messages = p.sendNotifications()
                    if messages:
                        for message in messages:
                            print("\tnotification set: {}".format(message))
                            await user.send(message)
                    else:
                        print("\tno notification to send")

            else:
                print("\tno notifications on")

        await self.close()


class Command(BaseCommand):
    def handle(self, **options):
        print("Init notifications")
        client = Notifications()
        print("Run notifications")
        client.run(BotData.objects.first().token)
