import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yata.settings")
django.setup()

from setup import configuration

config = configuration.Configuration()
config.resetDb()
config.fillDb()
config.staticFiles()