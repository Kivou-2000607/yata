import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yata.settings")
django.setup()

from django.contrib.auth.models import User
from player.models import Player
from faction.models import Faction
from setup.models import APIKey
from awards.models import AwardsData
from faction.models import FactionData
from bazaar.models import BazaarData
from loot.models import NPC
from decouple import config


def yes_or_no(question):
    reply = str(input(question + ' (y/n): ')).lower().strip()
    if reply[0] == 'y':
        return True
    if reply[0] == 'n':
        return False
    else:
        return yes_or_no("Uhhhh... please enter ")


key = config('APIKEY')
reset_db = False
fill_db = False
static_files = False


reset_db = yes_or_no("Do you want to reset the database?")
fill_db = yes_or_no("Do you want to fill the database?")
static_file = yes_or_no("Do you want to generate static files?")

if reset_db:
    if (config("DATABASE") == "postgresql"):
        print('Remove local database')
        cmd = 'python manage.py reset_db'
        r = os.system(cmd)
    else:
        # remove local database
        print('Remove local database')
        cmd = 'rm -vf db.sqlite3'
        r = os.system(cmd)

    # migrate
    cmd = 'python manage.py migrate'
    r = os.system(cmd)

    # create cache table
    cmd = 'python manage.py createcachetable'
    r = os.system(cmd)

# create db super user
if not len(User.objects.all()):
    print('create superuser')
    User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')

# create required objects
if not len(Player.objects.filter(tId=-1)):
    print('Create Player')
    Player.objects.create(tId=-1, name="Anonymous", validKey=False)
if not len(Faction.objects.filter(tId=-1)):
    print('Create Faction')
    Faction.objects.create(tId=-1, name="Faction Anonymous")
if not len(APIKey.objects.all()) and key:
    print('Create API Key')
    APIKey.objects.create(key=key)
if not len(AwardsData.objects.all()):
    print('Create Awards data')
    AwardsData.objects.create()
if not len(BazaarData.objects.all()):
    print('Create Bazaar data')
    BazaarData.objects.create()
if not len(FactionData.objects.all()):
    print('Create Faction data')
    FactionData.objects.create()
if not len(NPC.objects.all()):
    print('Create NPC')
    NPC.objects.create(tId=4, show=True)
    NPC.objects.create(tId=15, show=True)


if fill_db:
    cmd = 'python manage.py checkKeys'
    r = os.system(cmd)
    cmd = 'python manage.py updateStocks'
    r = os.system(cmd)
    cmd = 'python manage.py updateAwards'
    r = os.system(cmd)
    cmd = 'python manage.py updateTerritories'
    r = os.system(cmd)
    cmd = 'python manage.py updateItems'
    r = os.system(cmd)
    cmd = 'python manage.py updatePlayers'
    r = os.system(cmd)
    cmd = 'python manage.py updateLoot'
    r = os.system(cmd)
    cmd = 'python manage.py updateFactionTree'
    r = os.system(cmd)

if static_file:
    cmd = 'python manage.py collectstatic'
    r = os.system(cmd)
