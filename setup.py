import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yata.settings")
django.setup()

from setup.configuration import Configuration as config

config.resetDb()
config.fillDb()
config.staticFiles()