from django.db import models
from django.utils import timezone


class Player(models.Model):
    # user information: basic
    tId = models.IntegerField(default=4, unique=True)
    name = models.CharField(default="Duke", max_length=200)
    key = models.CharField(default="AAAA", max_length=16)

    # user information: faction
    factionId = models.IntegerField(default=0)
    factionAA = models.BooleanField(default=False)
    factionNa = models.CharField(default="My Faction", max_length=32)

    # user last update
    lastUpdateTS = models.IntegerField(default=0)

    # info for chain APP
    chainInfo = models.CharField(default="N/A", max_length=255)
    chainJson = models.TextField(default="{}")
    chainUpda = models.IntegerField(default=0)

    # info for target APP
    targetInfo = models.CharField(default="N/A", max_length=255)
    targetJson = models.TextField(default="{}")
    targetUpda = models.IntegerField(default=0)

    # info for target APP
    bazaarInfo = models.CharField(default="N/A", max_length=255)
    bazaarJson = models.TextField(default="{}")
    bazaarUpda = models.IntegerField(default=0)

    # info for awards APP
    awardsInfo = models.CharField(default="N/A", max_length=255)
    awardsJson = models.TextField(default="{}")
    awardsUpda = models.IntegerField(default=0)

    def __str__(self):
        return "{} [{}]".format(self.name, self.tId)

    def update_info(self):
        """ update player information

        """
        print("[player.models.update_info] {}".format(self))
        from yata.handy import apiCall
        from awards.functions import updatePlayerAwards
        import json

        # API Calls
        user = apiCall('user', '', 'personalstats,crimes,education,battlestats,workstats,perks,networth,merits,profile,medals,honors,icons', self.key)

        # update basic info (and chain)
        self.name = user.get("name", "?")
        self.factionId = user.get("faction", dict({})).get("faction_id", 0)
        self.factionNa = user.get("faction", dict({})).get("faction_name", "N/A")

        # update chain info
        self.factionId = 0
        if self.factionId:
            chains = apiCall("faction", "", "chains", self.key)
            self.factionAA = True if chains.get("chains") is not None else False
            self.chainInfo = "{} [AA]".format(self.factionNa) if self.factionAA else self.factionNa
        else:
            self.factionAA = False
            self.chainInfo = "N/A"
        self.chainUpda = int(timezone.now().timestamp())

        # update awards info
        tornAwards = apiCall('torn', '', 'honors,medals', self.key)
        if 'apiError' in tornAwards:
            self.awardsJson = json.dumps(awardsJson)
            self.awardsInfo = "0"
        else:
            updatePlayerAwards(self, tornAwards, user)
        self.awardsUpda = int(timezone.now().timestamp())


        self.lastUpdateTS = int(timezone.now().timestamp())
        self.save()
