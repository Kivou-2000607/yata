from django.core.management.base import BaseCommand
from django.conf import settings

import json
import os
from awards.honors import d

class Command(BaseCommand):
    def handle(self, **options):
        file = os.path.join(settings.PROJECT_ROOT, 'static/honors/bannersId.json')
        with open(file, 'w') as fp:
            json.dump(d, fp)
