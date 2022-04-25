import os
import subprocess
import platform

from sre_constants import SRE_FLAG_DEBUG
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
    reset_db_question = "Do you want to reset the database?"
    fill_db_question = "Do you want to fill the database?"
    key = config('SECRET_KEY')

    def question(self, question):
        reply = str(input(question + ' (y/n): ')).lower().strip() 

        confirmation = [ "yes", "ye", "y" ]

        if (reply in confirmation or reply in [ 'no', 'n']):
            return reply in confirmation
        else:
            return self.question("Invalid input. Please enter")

    @staticmethod
    def executeCommand(command):
        try:
            if command[:2] == "rm" and platform.system() == "Windows":
                subprocess.run(["C:\Program Files\Git\git-bash.exe", "c", command], check = True, shell = True)
            else:
                os.system(command)
        except subprocess.CalledProcessError:
            print(command + ' does not exist')

    def resetDb(self):
        if (self.question(self.reset_db_question) is False):
            return

        if (config("DATABASE") == "postgresql"):
            print('Remove local database')
            self.executeCommand('py -3.8 manage.py reset_db')
        else:
            # remove local database
            print('Remove local database')
            self.executeCommand('rm -fr db.sqlite3')

        # migrate
        self.executeCommand('py -3.8 manage.py migrate')

        # create cache table
        self.executeCommand('py -3.8 manage.py createcachetable')

        # create db super user
        if not len(User.objects.all()):
            print('create superuser')
            User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')

        # create required objects
        if not len(PlayerData.objects.all()):
            print('Create Players stats')
            self.executeCommand('py -3.8 manage.py players_stats')

        if not len(Player.objects.filter(tId=-1)):
            print('Create Player')
            Player.objects.create(tId=-1, name="Anonymous", validKey=False)

        if not len(Faction.objects.filter(tId=-1)):
            print('Create Faction')
            Faction.objects.create(tId=-1, name="Faction Anonymous")

        if not len(APIKey.objects.all()) and self.key:
            print('Create API Key')
            APIKey.objects.create(key=self.key)

        if not len(AwardsData.objects.all()):
            print('Create Awards data')
            AwardsData.objects.create()

        if not len(BazaarData.objects.all()):
            print('Create Bazaar data')
            BazaarData.objects.create()

        if not len(FactionData.objects.all()):
            print('Create Faction data')
            FactionData.objects.create()
            self.executeCommand('py -3.8 manage.py init_faction_tree')

        if not len(NPC.objects.all()):
            print('Create NPC')
            NPC.objects.create(tId=4, show=True)
            NPC.objects.create(tId=15, show=True)
            NPC.objects.create(tId=19, show=True)

        if not len(CompanyDescription.objects.all()):
            print('Create Companies')
            self.executeCommand('py -3.8 manage.py init_companies')

        if not len(Bot.objects.all()) >= 3:
            print('Create Bots')
            for i in range(3):
                Bot.objects.create(token=f"Token {i + 1}", name=f"Bot {i + 1}")
    
    def fillDb(self):
        if (self.question(self.fill_db_question) is False):
            return

        cmds = [
            'py -3.8 manage.py check_keys',
            'py -3.8 manage.py awards',
            'py -3.8 manage.py territories',
            'py -3.8 manage.py items',
            'py -3.8 manage.py players',
            'py -3.8 manage.py loot',
            'py -3.8 manage.py factions',
            'py -3.8 manage.py companies'
        ]

        for cmd in cmds:
            self.executeCommand(cmd)

    def staticFiles(self):
        # Has its own yes/no
        cmd = 'py -3.8 manage.py collectstatic'
        r = os.system(cmd)