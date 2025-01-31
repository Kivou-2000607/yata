import os
from pathlib import Path

import django
import django_json_widget as _

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yata.settings")
django.setup()
from yata.logger import logger
from decouple import config  # noqa: E402
from django.contrib.auth.models import User  # noqa: E402

from awards.models import AwardsData  # noqa: E402
from bazaar.models import BazaarData  # noqa: E402
from company.models import CompanyDescription  # noqa: E402
from faction.models import Faction, FactionData  # noqa: E402
from loot.models import NPC  # noqa: E402
from player.models import Player, PlayerData  # noqa: E402
from setup.models import APIKey  # noqa: E402


def yes_or_no(question):
    reply = str(input(question + " (y/n): ")).lower().strip()
    if reply[0] == "y":
        return True
    if reply[0] == "n":
        return False
    else:
        return yes_or_no("Uhhhh... please enter ")


key = config("SECRET_KEY")
reset_db = False
fill_db = False
static_files = False


reset_db = yes_or_no("Do you want to reset the database?")
fill_db = yes_or_no("Do you want to fill the database?")
static_file = yes_or_no("Do you want to generate static files?")

if reset_db:
    if config("DATABASE") == "postgresql":
        logger.info("Remove local database")
        cmd = "python manage.py reset_db"
        r = os.system(cmd)
    else:
        # remove local database
        logger.info("Remove local database")
        cmd = "rm -vf db.sqlite3"
        r = os.system(cmd)

    # migrate
    cmd = "python manage.py migrate"
    r = os.system(cmd)

    # create cache table
    cmd = "python manage.py createcachetable"
    r = os.system(cmd)

# create db super user
if not len(User.objects.all()):
    logger.info("create superuser")
    User.objects.create_superuser("admin", "admin@example.com", "adminpass")

# create required objects
if not len(PlayerData.objects.all()):
    logger.info("Create Players stats")
    cmd = "python manage.py players_stats"
    r = os.system(cmd)

if not len(Player.objects.filter(tId=-1)):
    logger.info("Create Player")
    Player.objects.create(tId=-1, name="Anonymous", validKey=False)

if not len(Faction.objects.filter(tId=-1)):
    logger.info("Create Faction")
    Faction.objects.create(tId=-1, name="Faction Anonymous")

if not len(APIKey.objects.all()) and key:
    logger.info("Create API Key")
    APIKey.objects.create(key=key)

if not len(AwardsData.objects.all()):
    logger.info("Create Awards data")
    AwardsData.objects.create()

if not len(BazaarData.objects.all()):
    logger.info("Create Bazaar data")
    BazaarData.objects.create()

if not len(FactionData.objects.all()):
    logger.info("Create Faction data")
    FactionData.objects.create()
    cmd = "python manage.py init_faction_tree"
    r = os.system(cmd)

if not len(NPC.objects.all()):
    logger.info("Create NPC")
    NPC.objects.create(tId=4, show=True)
    NPC.objects.create(tId=15, show=True)
    NPC.objects.create(tId=19, show=True)

if not len(CompanyDescription.objects.all()):
    logger.info("Create NPC")
    cmd = "python manage.py init_companies"
    r = os.system(cmd)

if fill_db:
    cmd = "python manage.py check_keys"
    r = os.system(cmd)
    cmd = "python manage.py awards"
    r = os.system(cmd)
    cmd = "python manage.py items"
    r = os.system(cmd)
    cmd = "python manage.py players"
    r = os.system(cmd)
    cmd = "python manage.py loot"
    r = os.system(cmd)
    cmd = "python manage.py factions"
    r = os.system(cmd)
    cmd = "python manage.py companies"
    r = os.system(cmd)

if static_file:

    p = Path(_.__path__[0]) / "static" / "dist" / "jsoneditor.map"
    p.touch()

    cmd = "python manage.py collectstatic --noinput"
    r = os.system(cmd)
