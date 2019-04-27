from django.db import models
from django.utils import timezone


class Player(models.Model):
    tId = models.IntegerField(default=4, unique=True)
    name = models.CharField(default="Duke", max_length=200)
    key = models.CharField(default="AAAA", max_length=16)

    lastUpdateTS = models.IntegerField(default=0)

    factionInfo = models.CharField(default="N/A", max_length=255)
    factionJson = models.TextField(default="{}")

    bazaarInfo = models.CharField(default="N/A", max_length=255)
    bazaarJson = models.TextField(default="{}")

    awardsInfo = models.CharField(default="N/A", max_length=255)
    awardsJson = models.TextField(default="{}")

    def __str__(self):
        return "{} [{}]".format(self.name, self.tId)
