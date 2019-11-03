from django.db import models
from django.utils import timezone

from player.models import Player

from yata.handy import apiCall
from yata.handy import cleanhtml


class Preference(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    yataServer = models.BooleanField(default=False)
    yataServerName = models.CharField(default="", blank=True, max_length=32)

    notificationsEvents = models.BooleanField(default=False)

    def __str__(self):
        return "Bot preference of {}".format(self.player)

    def hasNotifications(self):
        return self.notificationsEvents

    def sendNotifications(self):
        """Returns a array of messages or False"""

        # get torn api events list
        key = self.player.key
        r = apiCall('user', '', 'events', key, sub='events', verbose=False)

        # keep only unseen events
        events = {int(k): v for k, v in r.items() if v['seen'] == 0}

        # handle the api error case
        if 'apiError' in r:
            return [r['apiError']]

        # loop over the unseen events
        messages = []
        for eventId, v in events.items():
            # create id and message
            event = cleanhtml(v['event']).replace("[view]", "").strip()

            # check if unseen even has already been notified (ie if Event exist)
            # first notification -> create Event object and return message
            if self.event_set.filter(eventId=eventId).first() is None:
                self.event_set.create(eventId=eventId, timestamp=int(timezone.now().timestamp()))
                messages.append(event)

            # event unseen but already notified
            else:
                pass

        # loop over notifications sent and clean
        for e in self.event_set.all():
            # event is now seen
            if e.eventId not in events:
                print("delete event because seen")
                e.delete()

        return messages if len(messages) else False


class Event(models.Model):
    preference = models.ForeignKey(Preference, on_delete=models.CASCADE)
    eventId = models.IntegerField(default=0)
    timestamp = models.IntegerField(default=0)


class BotData(models.Model):
    token = models.CharField(default="BOT_TOKEN", max_length=512)
