from django.core.management.base import BaseCommand
from django.utils import timezone

from bazaar.models import ItemUpdate


class Command(BaseCommand):
    def handle(self, **options):
        print("[COMMAND cleandb] start")

        for update in ItemUpdate.objects.filter(date__lt=timezone.now() - timezone.timedelta(days=1)):
            print("[COMMAND cleandb] deleting {}".format(update))
            update.delete()

        print("[COMMAND cleandb] end")
