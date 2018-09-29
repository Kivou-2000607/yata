from django.db import models
from django.utils import timezone


class Faction(models.Model):
    tId = models.IntegerField(default=0, unique=True)
    name = models.CharField(default="MyFaction", max_length=200)
    hitsThreshold = models.IntegerField(default=100)
    apiKey = models.CharField(default="0", max_length=16)

    def __str__(self):
        return "{} [{}]".format(self.name, self.tId)

    def get_n_chains(self):
        return(len(self.chain_set.all()))


class Chain(models.Model):
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    tId = models.IntegerField(default=0)
    nHits = models.IntegerField(default=0)
    respect = models.FloatField(default=0)
    start = models.IntegerField(default=0)
    startDate = models.DateTimeField(default=timezone.now)
    end = models.IntegerField(default=0)
    endDate = models.DateTimeField(default=timezone.now)
    status = models.BooleanField(default=True)
    jointReport = models.BooleanField(default=False)

    def __str__(self):
        return "Chain [{}]: {} hits and {} respects".format(self.tId, self.nHits, self.respect)

    def have_report(self):
        return True if len(self.report_set.all()) else False

    def toggle_report(self):
        self.jointReport = not self.jointReport
        return self.jointReport


class Member(models.Model):
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    tId = models.IntegerField(default=0, unique=True)
    name = models.CharField(default="Duke", max_length=200)
    daysInFaction = models.IntegerField(default=0)
    lastAction = models.CharField(default="Duke", max_length=200)

    def __str__(self):
        return "{} [{}]".format(self.name, self.tId)


class Report(models.Model):
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return("Report of {}".format(self.chain))


class Bonus(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    name = models.CharField(default="Duke", max_length=200)
    hit = models.IntegerField(default=0)
    respect = models.FloatField(default=0)
    respectMax = models.FloatField(default=0)


class Count(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    attackerId = models.IntegerField(default=0)
    name = models.CharField(default="Duke", max_length=200)
    hits = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    respect = models.FloatField(default=0)
    respectTotal = models.FloatField(default=0)
    daysInFaction = models.IntegerField(default=0)
