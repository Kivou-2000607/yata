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

    # abv
    abv = models.CharField(default="-", max_length=4)

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
    daily_profit = models.IntegerField(default=0)
    weekly_income = models.BigIntegerField(default=0)
    weekly_customers = models.IntegerField(default=0)
    weekly_profit = models.IntegerField(default=0)
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
    effectiveness_ws_act = models.IntegerField(default=0)  # to be removed
    effectiveness_ws_max = models.IntegerField(default=0)
    total_wage = models.IntegerField(default=0)

    # company wise effectiveness
    effectiveness_working_stats = models.IntegerField(default=0)
    effectiveness_settled_in = models.IntegerField(default=0)
    effectiveness_director_education = models.IntegerField(default=0)
    effectiveness_addiction = models.IntegerField(default=0)
    effectiveness_inactivity = models.IntegerField(default=0)
    effectiveness_management = models.IntegerField(default=0)
    effectiveness_book_bonus = models.IntegerField(default=0)
    effectiveness_total = models.IntegerField(default=0)

    def __str__(self):
        return f"{mark_safe(self.name)} [{self.tId}]"

    def html_link(self):
        return mark_safe(f'<a href="https://www.torn.com/joblist.php#?p=corpinfo&ID={self.tId}" target="_blank">{self}</a>')

    def update_info(self, rebuildPast=False):
        # try to get director's key
        director = Player.objects.filter(tId=self.director).first()
        if director is None:
            return

        print(f"Company {self} -> update with director key")

        # api call
        req = apiCall("company", "", "detailed,employees,profile,stock,timestamp", director.getKey(), verbose=False)
        if "apiError" in req:
            if req["apiErrorCode"] in [7]:
                self.director = 0
                self.save()
            return True, req

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

        # update all employees and compute company effectiveness
        defaults["total_wage"] = 0
        for k, v in employees.items():
            # convert last action to only timestamp
            v["last_action"] = v["last_action"]["timestamp"]
            # remove status
            del v["status"]
            # flatten effectiveness and compute company effectiveness
            for eff in ["working_stats", "settled_in", "director_education", "addiction", "inactivity", "management", "book_bonus", "total"]:
                effectiveness_key = f'effectiveness_{eff}'
                effectiveness_val = v.get("effectiveness", {}).get(eff, 0)
                v[effectiveness_key] = effectiveness_val
                defaults[effectiveness_key] = defaults[effectiveness_key] + effectiveness_val if effectiveness_key in defaults else effectiveness_val
            del v["effectiveness"]
            # compute total wage
            defaults["total_wage"] += int(v.get("wage", 0))

        # create total wage and employees
        for tId, emp in employees.items():
            try:
                self.employee_set.update_or_create(tId=tId, defaults=emp)
            except BaseException:
                self.employee_set.filter(tId=tId).delete()
                self.employee_set.update_or_create(tId=tId, defaults=emp)

        # set company updates
        for attr, value in defaults.items():
            setattr(self, attr, value)

        # create historical data
        timestamp = defaults["timestamp"]
        id_ts = (timestamp + 3600 * 6) - (timestamp + 3600 * 6) % (3600 * 24)
        # remove some data from defaults
        for k in ['company_bank', 'days_old', 'director', 'employees_capacity', 'name', 'rating', 'trains_available', 'upgrades_company_size', 'upgrades_staffroom_size', 'upgrades_storage_size', 'upgrades_storage_space', 'director_name']:
            del defaults[k]

        # remove some data from employees
        for emp in employees.values():
            for k in ["days_in_company", "wage"]:
                del emp[k]
        # add employees
        defaults["employees"] = json.dumps(employees)
        company_data, create = self.companydata_set.update_or_create(id_ts=id_ts, defaults=defaults)

        # create weekly_profit
        last_week = id_ts - (6 * 24 * 3600 + 1)
        company_datas = self.companydata_set.filter(id_ts__gt=last_week)
        n_data = company_datas.count()
        money_spent = 0
        for cd in company_datas:
            money_spent += (cd.advertising_budget + cd.total_wage) * 7 / float(company_datas.count())  # in case less than 7 data

        company_data.daily_profit = company_data.daily_income - company_data.advertising_budget - company_data.total_wage
        company_data.weekly_profit = company_data.weekly_income - money_spent
        company_data.save()

        # update
        self.daily_profit = company_data.daily_profit
        self.weekly_profit = company_data.weekly_profit
        self.save()

        if rebuildPast:
            print("Rebuild past")
            for company_data in self.companydata_set.all():
                # create weekly_profit
                last_week = company_data.id_ts - (6 * 24 * 3600 + 1)
                company_datas = self.companydata_set.filter(id_ts__gt=last_week)
                n_data = company_datas.count()
                money_spent = 0
                for cd in company_datas:
                    money_spent += (cd.advertising_budget + cd.total_wage) * 7 / float(company_datas.count())  # in case less than 7 data

                company_data.daily_profit = company_data.daily_income - company_data.advertising_budget - company_data.total_wage
                company_data.weekly_profit = company_data.weekly_income - money_spent

                # create effectiveness
                defaults = {}
                for emp_id, values in json.loads(company_data.employees).items():
                    for k, v in values.items():
                        if k[:13] == "effectiveness":
                            defaults[k] = defaults[k] + v if k in defaults else v

                # set company updates
                for attr, value in defaults.items():
                    setattr(company_data, attr, value)
                company_data.save()


        # get stocks
        defaults = {"timestamp": timestamp}
        stocks = req.get("company_stock", {})

        # create company posisions
        p_abv = {position.name: position.abv for position in self.company_description.position_set.all()}
        positions = {v: 0 for k, v in p_abv.items()}
        total = 0
        for e in self.employee_set.all():
            if e.position in p_abv:
                total += 1
                positions[p_abv[e.position]] += 1
        positions["TOT"] = total
        previous_stock = self.companystock_set.exclude(id_ts=id_ts).order_by("-timestamp").first()
        if previous_stock is not None:
            pp = json.loads(previous_stock.positions)
            delta_positions = {k: v-pp.get(k, 0) for k, v in positions.items()}
        else:
            delta_positions = {}

        # loop over stocks
        for stock_name, stock in stocks.items():
            for k, v in stock.items():
                defaults[k] = v

            # get previous stock
            previous_stock = self.companystock_set.exclude(id_ts=id_ts).filter(name=stock_name).order_by("-timestamp").first()
            if previous_stock is None:
                defaults["delta_in_stock"] = defaults["in_stock"]
                defaults["created"] = defaults["delta_in_stock"] + defaults["sold_amount"]
                defaults["delta_created"] = defaults["created"]
                defaults["delta_sold_worth"] = defaults["sold_worth"]
            else:
                defaults["delta_in_stock"] = defaults["in_stock"] - previous_stock.in_stock
                defaults["created"] = defaults["delta_in_stock"] + defaults["sold_amount"]
                defaults["delta_created"] = defaults["created"] - previous_stock.created
                defaults["delta_sold_worth"] = defaults["sold_worth"] - previous_stock.sold_worth

            defaults["positions"] = json.dumps(positions)
            defaults["delta_positions"] = json.dumps(delta_positions)

            company_stock, create = self.companystock_set.update_or_create(id_ts=id_ts, name=stock_name, defaults=defaults)
            # print(company_stock, create)
            # for k, v in defaults.items():
            #     print(k, v)

        return False, "updated"

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
    daily_income = models.BigIntegerField(default=0)
    daily_customers = models.IntegerField(default=0)
    daily_profit = models.IntegerField(default=0)
    weekly_income = models.BigIntegerField(default=0)
    weekly_customers = models.IntegerField(default=0)
    weekly_profit = models.IntegerField(default=0)
    advertising_budget = models.IntegerField(default=0)
    total_wage = models.IntegerField(default=0)

    # company wise effectiveness
    effectiveness_working_stats = models.IntegerField(default=0)
    effectiveness_settled_in = models.IntegerField(default=0)
    effectiveness_director_education = models.IntegerField(default=0)
    effectiveness_addiction = models.IntegerField(default=0)
    effectiveness_inactivity = models.IntegerField(default=0)
    effectiveness_management = models.IntegerField(default=0)
    effectiveness_book_bonus = models.IntegerField(default=0)
    effectiveness_total = models.IntegerField(default=0)

    employees = models.TextField(default="{}")

    def __str__(self):
        return f"Company data {self.company.name} [{self.company.tId}]"

# Company stock
class CompanyStock(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    id_ts = models.IntegerField(default=0)  # timestamp rounded at the day (serves as ID)
    timestamp = models.IntegerField(default=0)  # real timestamp

    # dictionnary with number of employees / positions
    positions = models.TextField(default="{}")
    delta_positions = models.TextField(default="{}")

    # from API
    name = models.CharField(default="Stock", max_length=32)
    cost = models.IntegerField(default=0)
    rrp = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    in_stock = models.IntegerField(default=0)
    on_order = models.IntegerField(default=0)
    sold_amount = models.IntegerField(default=0)
    sold_worth = models.IntegerField(default=0)

    # computed
    created = models.IntegerField(default=0)  # sold_amount + delta_in_stock

    # delta
    delta_in_stock = models.IntegerField(default=0)
    delta_created = models.IntegerField(default=0)
    delta_sold_worth = models.IntegerField(default=0)

    def __str__(self):
        return f"Company stock {self.company.name} [{self.company.tId}]"

    def display_pos(self):
        emps = json.loads(self.positions)
        demps = json.loads(self.delta_positions)
        pos = ' '.join([f'{k}: {v}' for k, v in emps.items() if k not in ['TOT']])
        dpos = ' '.join([f'{k}: {v}' for k, v in demps.items() if v])
        tot = emps.get("TOT", 0)
        return pos, dpos, tot
