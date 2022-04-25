import os
import subprocess

from django.contrib.auth.models import User
from player.models import Player
from player.models import PlayerData
from faction.models import Faction
from setup.models import APIKey
from awards.models import AwardsData
from faction.models import FactionData
from bazaar.models import BazaarData
from company.models import CompanyDescription
from loot.models import NPC
from bot.models import Bot
from decouple import config


class Configuration:
    def getInput(question):
        user_input = input(question)
        return user_input is None if "" else user_input

    def executeCommand(command):
        r = os.system(command)

    def question(self, question):
        reply = self.getInput(question + ' (y/n): ').lower().strip()

        confirmation = ["yes", "ye", "y"]

        if reply in confirmation or reply in ['no', 'n']:
            return reply in confirmation
        else:
            return self.question("Invalid input. Please enter")

    @classmethod
    def resetDb(cls):
        if cls.question("Do you want to reset the database?") is False:
            return
            
        key = config('SECRET_KEY')

        if config("DATABASE") == "postgresql":
            print('Remove local database')
            cls.executeCommand('python manage.py reset_db')
        else:
            # remove local database
            print('Remove local database')
            command = 'rm -fr db.sqlite3'
            try:
                subprocess.run(["C:\Program Files\Git\git-bash.exe", "c", command], check=True, shell=True)
            except subprocess.CalledProcessError:
                print(command + ' does not exist')

        # migrate
        cls.executeCommand('python manage.py migrate')

        # create cache table
        cls.executeCommand('python manage.py createcachetable')

        # create db super user
        if not len(User.objects.all()):
            print('create superuser')
            User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')

        # create required objects
        if not len(PlayerData.objects.all()):
            print('Create Players stats')
            cls.executeCommand('python manage.py players_stats')

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
            cls.executeCommand('python manage.py init_faction_tree')

        if not len(NPC.objects.all()):
            print('Create NPC')
            NPC.objects.create(tId=4, show=True)
            NPC.objects.create(tId=15, show=True)
            NPC.objects.create(tId=19, show=True)

        if not len(CompanyDescription.objects.all()):
            print('Create Companies')
            cls.executeCommand('python manage.py init_companies')

        if not len(Bot.objects.all()) >= 3:
            print('Create Bots')
            for i in range(3):
                Bot.objects.create(token=f"Token {i + 1}", name=f"Bot {i + 1}")
    
    @classmethod
    def fillDb(cls):
        if (cls.question("Do you want to fill the database?") is False):
            return

        cmds = [
            'python manage.py check_keys',
            'python manage.py awards',
            'python manage.py territories',
            'python manage.py items',
            'python manage.py players',
            'python manage.py loot',
            'python manage.py factions',
            'python manage.py companies'
        ]

        for cmd in cmds:
            cls.executeCommand(cmd)

    @classmethod
    def staticFiles(cls):
        # Has its own yes/no
        cls.executeCommand('python manage.py collectstatic')