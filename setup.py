from loot.models import NPC
from bazaar.models import BazaarData
from faction.models import FactionData
from awards.models import AwardsData
from setup.models import APIKey
from faction.models import Faction
from player.models import Player
from django.contrib.auth.models import User
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yata.settings")
django.setup()


def yes_or_no(question):
    reply = str(input(question+' (y/n): ')).lower().strip()
    if reply[0] == 'y':
        return True
    if reply[0] == 'n':
        return False
    else:
        return yes_or_no("Uhhhh... please enter ")


key = 'jiqOS12ECly3tLbO'
#key = 'Your API Key'
reset_db = False
fill_db = False

if (key == False):
    key = input(
        "Enter your TORN API Key. Or save time and set this in setup.py: ")

reset_db = yes_or_no("Do you want to reset the database?")
fill_db = yes_or_no("Do you want to fill the database?")


if reset_db:
    # remove local database
    print('Remove local database')
    cmd = 'rm -vf db.sqlite3'
    r = os.system(cmd)

    # migrate
    cmd = 'python manage.py migrate'
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
