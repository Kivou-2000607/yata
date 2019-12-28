import os
from django.contrib.auth.models import User
from player.models import News
from player.models import Player
from chain.models import Faction
from chain.models import Crontab
from setup.models import APIKey
from awards.models import AwardsData
from chain.models import FactionData
from bazaar.models import BazaarData
from loot.models import NPC

key = False
install_req = False
reset_db = False
fill_db = False

# STEP 0: remove database and install modules

# install requirements
if install_req:
    print('Install requirements')
    cmd = 'pip install -r requirements.txt'
    r = os.system(cmd)


# STEP 1: setup database

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
if not len(News.objects.all()):
    print('Create News')
    News.objects.create(text="Hello World!")
if not len(Player.objects.filter(tId=-1)):
    print('Create Player')
    Player.objects.create(tId=-1, name="Anonymous", validKey=False)
if not len(Faction.objects.filter(tId=-1)):
    print('Create Faction')
    Faction.objects.create(tId=-1, name="Faction Anonymous")
if not len(Crontab.objects.all()):
    print('Create Crontab')
    Crontab.objects.create()
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

# STEP 2: fill database

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
    cmd = 'python manage.py updateUpgradeTree'
    r = os.system(cmd)
