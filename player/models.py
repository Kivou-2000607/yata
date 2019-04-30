from django.db import models
from django.utils import timezone


class Player(models.Model):
    tId = models.IntegerField(default=4, unique=True)
    name = models.CharField(default="Duke", max_length=200)
    key = models.CharField(default="AAAA", max_length=16)

    lastUpdateTS = models.IntegerField(default=0)

    chainInfo = models.CharField(default="N/A", max_length=255)
    chainJson = models.TextField(default="{}")
    chainUpda = models.IntegerField(default=0)

    targetsInfo = models.CharField(default="N/A", max_length=255)
    targetsJson = models.TextField(default="{}")
    targetsUpda = models.IntegerField(default=0)


    bazaarInfo = models.CharField(default="N/A", max_length=255)
    bazaarJson = models.TextField(default="{}")
    bazaarUpda = models.IntegerField(default=0)

    awardsInfo = models.CharField(default="N/A", max_length=255)
    awardsJson = models.TextField(default="{}")
    awardsUpda = models.IntegerField(default=0)

    def __str__(self):
        return "{} [{}]".format(self.name, self.tId)
