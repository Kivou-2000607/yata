from django.db import models


# Company description
class CompanyDescription(models.Model):
    tId = models.IntegerField(default=0, unique=True)
    name = models.CharField(default="Default company name", max_length=32)
    cost = models.BigIntegerField(default=0)
    default_employees = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} [{self.tId}]"

# Company position
class Position(models.Model):
    company = models.ForeignKey(CompanyDescription, on_delete=models.CASCADE)
    name = models.CharField(default="Default position name", max_length=32)
    man_required = models.IntegerField(default=0)
    int_required = models.IntegerField(default=0)
    end_required = models.IntegerField(default=0)
    man_gain = models.IntegerField(default=0)
    int_gain = models.IntegerField(default=0)
    end_gain = models.IntegerField(default=0)
    special_ability = models.CharField(default="Default sepcial ability", max_length=32)
    description = models.CharField(default="Default description", max_length=256)

    def __str__(self):
        return f"{self.company} position {self.name}"

# Company special
class Special(models.Model):
    company = models.ForeignKey(CompanyDescription, on_delete=models.CASCADE)
    name = models.CharField(default="Default position name", max_length=32)
    effect = models.CharField(default="Default position name", max_length=256)
    cost = models.IntegerField(default=0)
    rating_required = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.company} special {self.name}"

# Company stock
class Stock(models.Model):
    company = models.ForeignKey(CompanyDescription, on_delete=models.CASCADE)
    name = models.CharField(default="Default position name", max_length=32)
    cost = models.IntegerField(default=0)
    rrp = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.company} stock {self.name}"
