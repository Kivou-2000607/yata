from django.db import models

from player.models import Player
from yata.handy import apiCall

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


# Company
class Company(models.Model):
    company_description = models.ForeignKey(CompanyDescription, on_delete=models.CASCADE)

    # profile
    tId = models.IntegerField(default=0, unique=True)
    rating = models.IntegerField(default=0)
    name = models.CharField(default="Default company name", max_length=32)
    director = models.IntegerField(default=0)
    employees_hired = models.IntegerField(default=0)
    employees_capacity = models.IntegerField(default=0)
    employees_capacity = models.IntegerField(default=0)
    daily_income = models.BigIntegerField(default=0)
    daily_customers = models.IntegerField(default=0)
    weekly_income = models.BigIntegerField(default=0)
    weekly_customers = models.IntegerField(default=0)
    days_old = models.IntegerField(default=0)

    # detailed
    company_bank = models.BigIntegerField(default=0)
    popularity = models.IntegerField(default=0)
    efficiency = models.IntegerField(default=0)
    environment = models.IntegerField(default=0)
    trains_available = models.IntegerField(default=0)
    advertising_budget = models.IntegerField(default=0)
    upgrades_company_size = models.IntegerField(default=0)
    upgrades_staffroom_size = models.CharField(default="Default company staffroom", max_length=32)
    upgrades_storage_size = models.CharField(default="Default company storage", max_length=32)
    upgrades_storage_space = models.IntegerField(default=0)

    # misc
    timestamp = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} [{self.tId}]"

    def update_info(self):

        # try to get director's key
        director = Player.objects.filter(tId=self.director).first()
        if director is None:
            return

        # api call
        req = apiCall("company", "", "detailed,employees,profile,timestamp", director.getKey(), verbose=True)
        if "apiError" in req:
            print(req)
            if req["apiErrorCode"] in [7]:
                self.director = 0
                self.save()
            return

        # create update dict
        defaults = {"timestamp": req.get("timestamp", 0)}

        # update profile
        for k in ["rating", "name", "director", "employees_hired", "employees_capacity", "employees_capacity", "daily_income", "daily_customers", "weekly_income", "weekly_customers", "days_old"]:
            defaults[k] = req.get("company", {}).get(k, 0)

        # update detailed
        for k in ["company_bank", "popularity", "efficiency", "environment", "trains_available", "advertising_budget"]:
            defaults[k] = req.get("company_detailed", {}).get(k, 0)

        # update detailed upgrades
        for k in ["company_size", "staffroom_size", "storage_size", "storage_space"]:
            defaults[f'upgrades_{k}'] = req.get("company_detailed", {}).get("upgrades", {}).get(k, 0)

        # updates
        for attr, value in defaults.items():
            setattr(self, attr, value)
        self.save()

        employees = req.get("company_employees", {})
        # remove old employees
        for employee in self.employee_set.all():
            if str(employee.tId) not in employees:
                print(f"company update remove emplyee {employee}")
                employee.delete()

        # update all employees
        for k, v in employees.items():
            # convert last action to only timestamp
            v["last_action"] = v["last_action"]["timestamp"]
            # remove status
            del v["status"]
            # flatten effectiveness
            for eff in v["effectiveness"]:
                if eff not in ["working_stats", "settled_in", "director_education", "addiction", "total"]:
                    print("missing effeciveness key", eff)
            for eff in ["working_stats", "settled_in", "director_education", "addiction"]:
                v[f'effectiveness_{eff}'] = v.get("effectiveness", {}).get(eff, 0)
            del v["effectiveness"]

        for tId, defaults in employees.items():
            self.employee_set.update_or_create(company=self, tId=tId, defaults=defaults)

# Emplaye stock
class Employee(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    tId = models.IntegerField(default=0)
    name = models.CharField(default="Default employee name", max_length=32)
    position = models.CharField(default="Default employee position", max_length=32)
    days_in_company = models.IntegerField(default=0)
    last_action = models.IntegerField(default=0)
    wage = models.IntegerField(default=0)
    manual_labor = models.IntegerField(default=0)
    intelligence = models.IntegerField(default=0)
    endurance = models.IntegerField(default=0)
    effectiveness_working_stats = models.IntegerField(default=0)
    effectiveness_settled_in = models.IntegerField(default=0)
    effectiveness_director_education = models.IntegerField(default=0)
    effectiveness_addiction = models.IntegerField(default=0)


    def __str__(self):
        return f"{self.company} employee {self.name} [{self.tId}]"
