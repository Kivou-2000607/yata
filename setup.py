import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yata.settings")
django.setup()

from _config import Configuration

config = Configuration.Configuration()
config.reset_db()
config.fill_db()
config.static_files()