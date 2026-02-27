import os
import subprocess
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yata.settings")
django.setup()

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
    if not reply:
        return yes_or_no(question)
    if reply[0] == "y":
        return True
    if reply[0] == "n":
        return False
    return yes_or_no("Uhhhh... please enter ")


def run(cmd):
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Command failed (exit {result.returncode}): {cmd}")
        sys.exit(result.returncode)


key = config("SECRET_KEY")

reset_db = yes_or_no("Do you want to reset the database?")
fill_db = yes_or_no("Do you want to fill the database?")
static_file = yes_or_no("Do you want to generate static files?")

if reset_db:
    if config("DATABASE") == "postgresql":
        print("Remove local database")
        run("python manage.py reset_db")
    else:
        print("Remove local database")
        run("rm -vf db.sqlite3")

    run("python manage.py migrate")
    run("python manage.py createcachetable")

# create db super user
if not User.objects.exists():
    print("create superuser")
    User.objects.create_superuser("admin", "admin@example.com", "adminpass")

# create required objects
if not PlayerData.objects.exists():
    print("Create Players stats")
    run("python manage.py players_stats")

if not Player.objects.filter(tId=-1).exists():
    print("Create Player")
    Player.objects.create(tId=-1, name="Anonymous", validKey=False)

if not Faction.objects.filter(tId=-1).exists():
    print("Create Faction")
    Faction.objects.create(tId=-1, name="Faction Anonymous")

if not APIKey.objects.exists() and key:
    print("Create API Key")
    APIKey.objects.create(key=key)

if not AwardsData.objects.exists():
    print("Create Awards data")
    AwardsData.objects.create()

if not BazaarData.objects.exists():
    print("Create Bazaar data")
    BazaarData.objects.create()

if not FactionData.objects.exists():
    print("Create Faction data")
    FactionData.objects.create()
    run("python manage.py init_faction_tree")

if not NPC.objects.exists():
    print("Create NPC")
    NPC.objects.create(tId=4, show=True)
    NPC.objects.create(tId=15, show=True)
    NPC.objects.create(tId=19, show=True)

if not CompanyDescription.objects.exists():
    print("Create Company descriptions")
    run("python manage.py init_companies")

if fill_db:
    run("python manage.py check_keys")
    run("python manage.py awards")
    run("python manage.py items")
    run("python manage.py players")
    run("python manage.py loot")
    run("python manage.py factions")
    run("python manage.py companies")

if static_file:
    run("python manage.py collectstatic --noinput")
