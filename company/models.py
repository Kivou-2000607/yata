from django.db import models
from django.utils.safestring import mark_safe

import json

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
    name = models.CharField(default="Default company name", max_length=128)
    director = models.IntegerField(default=0)
    director_name = models.CharField(default="Player", max_length=16)
    director_hrm = models.BooleanField(default=False)  # education Human Resource Management (boost in employee effectiveness)
    employees_hired = models.IntegerField(default=0)
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
    effectiveness_total = models.IntegerField(default=0)
    effectiveness_neg = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} [{self.tId}]"

    def html_link(self):
        return mark_safe(f'<a href="https://www.torn.com/joblist.php#?p=corpinfo&ID={self.tId}" target="_blank">{self}</a>')

    def update_info(self):
        # try to get director's key
        director = Player.objects.filter(tId=self.director).first()
        if director is None:
            return

        print(f"Company {self} -> update with director key")

        # api call
        req = apiCall("company", "", "detailed,employees,profile,timestamp", director.getKey(), verbose=False)
        if "apiError" in req:
            print(req)
            if req["apiErrorCode"] in [7]:
                self.director = 0
                self.save()
            return

        # create update dict
        defaults = {"timestamp": req.get("timestamp", 0), "director_name": director.name}

        # update profile
        for k in ["rating", "name", "director", "employees_hired", "employees_capacity", "employees_capacity", "daily_income", "daily_customers", "weekly_income", "weekly_customers", "days_old"]:
            defaults[k] = req.get("company", {}).get(k, 0)

        # update detailed
        for k in ["company_bank", "popularity", "efficiency", "environment", "trains_available", "advertising_budget"]:
            defaults[k] = req.get("company_detailed", {}).get(k, 0)

        # update detailed upgrades
        for k in ["company_size", "staffroom_size", "storage_size", "storage_space"]:
            defaults[f'upgrades_{k}'] = req.get("company_detailed", {}).get("upgrades", {}).get(k, 0)

        # get director edication
        if not self.director_hrm:
            self.director_hrm = 11 in apiCall("user", "", "education", director.getKey(), verbose=False).get("education_completed", [])

        # update employees
        employees = req.get("company_employees", {})
        employees = {} if employees is None else employees

        # remove old employees
        for employee in self.employee_set.all():
            if str(employee.tId) not in employees:
                print(f"company update remove employee {employee}")
                employee.delete()

        # update all employees
        effectiveness_total = 0
        effectiveness_neg = 0
        for k, v in employees.items():
            # convert last action to only timestamp
            v["last_action"] = v["last_action"]["timestamp"]
            # remove status
            del v["status"]
            # flatten effectiveness and compute total effectiveness
            for eff, effv in v["effectiveness"].items():
                if effv < 0:
                    effectiveness_neg += effv
                elif eff == "total":
                    effectiveness_total += effv
                if eff not in ["working_stats", "settled_in", "director_education", "addiction", "inactivity", "management", "book_bonus", "total"]:
                    print("missing effeciveness key", eff)
            for eff in ["working_stats", "settled_in", "director_education", "addiction", "inactivity", "management", "book_bonus", "total"]:
                v[f'effectiveness_{eff}'] = v.get("effectiveness", {}).get(eff, 0)
            del v["effectiveness"]

        defaults["effectiveness_total"] = effectiveness_total
        defaults["effectiveness_neg"] = effectiveness_neg

        for tId, emp in employees.items():
            self.employee_set.update_or_create(company=self, tId=tId, defaults=emp)

        # push company updates
        for attr, value in defaults.items():
            setattr(self, attr, value)
        self.save()

        # create historical data
        timestamp = defaults["timestamp"]
        id_ts = timestamp - timestamp % (3600 * 24)
        # remove some data from defaults
        for k in ['company_bank', 'days_old', 'director', 'employees_capacity', 'name', 'rating', 'trains_available', 'upgrades_company_size', 'upgrades_staffroom_size', 'upgrades_storage_size', 'upgrades_storage_space', 'director_name', 'director_hrm']:
            del defaults[k]

        # remove some data from employees
        for emp in employees.values():
            for k in ["days_in_company", "wage"]:
                del emp[k]
        # add employees
        defaults["employees"] = json.dumps(employees)
        data, create = self.companydata_set.update_or_create(id_ts=id_ts, defaults=defaults)

# Employee
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
    effectiveness_inactivity = models.IntegerField(default=0)
    effectiveness_management = models.IntegerField(default=0)
    effectiveness_book_bonus = models.IntegerField(default=0)
    effectiveness_total = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.company} employee {self.name} [{self.tId}]"

# Company data
class CompanyData(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    id_ts = models.IntegerField(default=0)  # timestamp rounded at the day (serves as ID)
    timestamp = models.IntegerField(default=0)  # real timestamp

    employees_hired = models.IntegerField(default=0)
    popularity = models.IntegerField(default=0)
    efficiency = models.IntegerField(default=0)
    environment = models.IntegerField(default=0)
    effectiveness_total = models.IntegerField(default=0)
    effectiveness_neg = models.IntegerField(default=0)
    daily_income = models.BigIntegerField(default=0)
    daily_customers = models.IntegerField(default=0)
    weekly_income = models.BigIntegerField(default=0)
    weekly_customers = models.IntegerField(default=0)
    advertising_budget = models.IntegerField(default=0)

    employees = models.TextField(default="{}")

    def __str__(self):
        return f"Company data {self.company.name} [{self.company.tId}]"
