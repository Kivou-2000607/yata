from django.core.management.base import BaseCommand
from django.utils import timezone


from bazaar.models import Stat
from bazaar.models import Player
from bazaar.models import ItemUpdate


class Command(BaseCommand):
    def handle(self, **options):
        print("[COMMAND stats] start")

        s = Stat.objects.all()[0]

        itemUpdates = ItemUpdate.objects.filter(date__gte=timezone.now() - timezone.timedelta(days=1))
        players = Player.objects.filter(date__gte=timezone.now() - timezone.timedelta(days=1))
        
        listItems = [a.item.tName for a in itemUpdates.all()]
        distItems = list(set(listItems))
        distOccur = [0]*len(distItems)
        for i, item in enumerate(distItems):
            distOccur[i] = listItems.count(item)
            print("[COMMAND stats] {}: {}".format(item, distOccur[i]))
        firstT = sorted(zip(distOccur, distItems), reverse=True)[:3]
        
        s.numberUpdates = itemUpdates.count()
        s.numberPlayers = players.count()
        s.firstThree = ";".join(["{},{}".format(t[1], t[0]) for t in firstT])
        s.date = timezone.now()
        s.save()

        print("[COMMAND stats] end")
