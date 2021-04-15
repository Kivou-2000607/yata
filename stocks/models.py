from django.db import models

from datetime import datetime
from yata.BulkManager2 import BulkManager

class Stock(models.Model):
    acronym = models.CharField(default="-", max_length=8, db_index=True)
    name = models.CharField(default="-", max_length=64)

    tendancy_l_a = models.FloatField(default=0.0)
    # tendancy_l_b = models.FloatField(default=0.0)
    tendancy_h_a = models.FloatField(default=0.0)
    tendancy_h_b = models.FloatField(default=0.0)
    tendancy_d_a = models.FloatField(default=0.0)
    tendancy_d_b = models.FloatField(default=0.0)
    tendancy_w_a = models.FloatField(default=0.0)
    tendancy_w_b = models.FloatField(default=0.0)
    tendancy_m_a = models.FloatField(default=0.0)
    tendancy_m_b = models.FloatField(default=0.0)
    tendancy_y_a = models.FloatField(default=0.0)
    tendancy_y_b = models.FloatField(default=0.0)

    timestamp = models.IntegerField(default=0)

    # current_price
    current_price = models.FloatField(default=0.0)
    previous_price = models.FloatField(default=0.0)

    # global
    market_cap = models.BigIntegerField(default=0)
    total_shares = models.BigIntegerField(default=0)

    # benefit
    requirement = models.IntegerField(default=0)
    description = models.CharField(default="-", max_length=256)

    # BulkManager
    objects = BulkManager()

    def __str__(self):
        return self.acronym

class History(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    timestamp = models.IntegerField(default=0, db_index=True)
    current_price = models.FloatField(default=0.0)
    market_cap = models.BigIntegerField(default=0)
    total_shares = models.BigIntegerField(default=0)

    # BulkManager
    objects = BulkManager()

    def __str__(self):
        return f'{self.stock} data'



ALL_STOCKS = [
		{
			"name": "Torn & Shanghai Banking",
			"acronym": "TSB",
			"current_price": 811.07,
			"benefit": {
				"requirement": 3000000,
				"description": "$50,000,000 every month"
			}
		},
		{
			"name": "Torn City Investments",
			"acronym": "TCB",
			"current_price": 849.13,
			"benefit": {
				"requirement": 1500000,
				"description": "a 10% Bank Interest Bonus"
			}
		},
		{
			"name": "Syscore MFG",
			"acronym": "SYS",
			"current_price": 474.96,
			"benefit": {
				"requirement": 3000000,
				"description": "an Advanced Firewall"
			}
		},
		{
			"name": "Legal Authorities Group",
			"acronym": "LAG",
			"current_price": 293.29,
			"benefit": {
				"requirement": 750000,
				"description": "1x Lawyer Business Card every week"
			}
		},
		{
			"name": "Insured On Us",
			"acronym": "IOU",
			"current_price": 147.95,
			"benefit": {
				"requirement": 3000000,
				"description": "$12,000,000 every month"
			}
		},
		{
			"name": "Grain",
			"acronym": "GRN",
			"current_price": 211.37,
			"benefit": {
				"requirement": 500000,
				"description": "$4,000,000 every month"
			}
		},
		{
			"name": "Torn City Health Service",
			"acronym": "THS",
			"current_price": 330.27,
			"benefit": {
				"requirement": 150000,
				"description": "1x Box of Medical Supplies every week"
			}
		},
		{
			"name": "Yazoo",
			"acronym": "YAZ",
			"current_price": 37.12,
			"benefit": {
				"requirement": 1000000,
				"description": "Free Banner Advertising"
			}
		},
		{
			"name": "The Torn City Times",
			"acronym": "TCT",
			"current_price": 223.48,
			"benefit": {
				"requirement": 100000,
				"description": "$1,000,000 every month"
			}
		},
		{
			"name": "Crude & Co",
			"acronym": "CNC",
			"current_price": 674.44,
			"benefit": {
				"requirement": 7500000,
				"description": "$80,000,000 every month"
			}
		},
		{
			"name": "Messaging Inc.",
			"acronym": "MSG",
			"current_price": 155.9,
			"benefit": {
				"requirement": 300000,
				"description": "Free Classified Advertising"
			}
		},
		{
			"name": "TC Music Industries",
			"acronym": "TMI",
			"current_price": 150.08,
			"benefit": {
				"requirement": 6000000,
				"description": "$25,000,000 every month"
			}
		},
		{
			"name": "TC Media Productions",
			"acronym": "TCP",
			"current_price": 275.06,
			"benefit": {
				"requirement": 1000000,
				"description": "a Company Sales Boost"
			}
		},
		{
			"name": "I Industries Ltd.",
			"acronym": "IIL",
			"current_price": 86.08,
			"benefit": {
				"requirement": 1000000,
				"description": "50% Coding Time Reduction"
			}
		},
		{
			"name": "Feathery Hotels Group",
			"acronym": "FHG",
			"current_price": 567,
			"benefit": {
				"requirement": 2000000,
				"description": "1x Feathery Hotel Coupon every week"
			}
		},
		{
			"name": "Symbiotic Ltd.",
			"acronym": "SYM",
			"current_price": 770.48,
			"benefit": {
				"requirement": 500000,
				"description": "1x Drug Pack every week"
			}
		},
		{
			"name": "Lucky Shots Casino",
			"acronym": "LSC",
			"current_price": 364.81,
			"benefit": {
				"requirement": 500000,
				"description": "1x Lottery Voucher every week"
			}
		},
		{
			"name": "Performance Ribaldry",
			"acronym": "PRN",
			"current_price": 487.97,
			"benefit": {
				"requirement": 1000000,
				"description": "1x Erotic DVD every week"
			}
		},
		{
			"name": "Eaglewood Mercenary",
			"acronym": "EWM",
			"current_price": 267.16,
			"benefit": {
				"requirement": 1000000,
				"description": "1x Box of Grenades every week"
			}
		},
		{
			"name": "Torn City Motors",
			"acronym": "TCM",
			"current_price": 298.69,
			"benefit": {
				"requirement": 1000000,
				"description": "10% Racing Skill Boost"
			}
		},
		{
			"name": "Empty Lunchbox Traders",
			"acronym": "ELT",
			"current_price": 182.95,
			"benefit": {
				"requirement": 5000000,
				"description": "10% Home Upgrade Discount"
			}
		},
		{
			"name": "Home Retail Group",
			"acronym": "HRG",
			"current_price": 212.65,
			"benefit": {
				"requirement": 10000000,
				"description": "1x Random Property"
			}
		},
		{
			"name": "Tell Group Plc.",
			"acronym": "TGP",
			"current_price": 90.33,
			"benefit": {
				"requirement": 2500000,
				"description": "a Company Advertising Boost"
			}
		},
		{
			"name": "West Side University",
			"acronym": "WSU",
			"current_price": 64.75,
			"benefit": {
				"requirement": 1000000,
				"description": "a 10% Education Course Duration Reduction"
			}
		},
		{
			"name": "International School TC",
			"acronym": "IST",
			"current_price": 314.09,
			"benefit": {
				"requirement": 100000,
				"description": "Free Education Courses"
			}
		},
		{
			"name": "Big Al's Gun Shop",
			"acronym": "BAG",
			"current_price": 419.68,
			"benefit": {
				"requirement": 3000000,
				"description": "1x Ammunition Pack"
			}
		},
		{
			"name": "Evil Ducks Candy Corp",
			"acronym": "EVL",
			"current_price": 377.9,
			"benefit": {
				"requirement": 100000,
				"description": "1000 Happiness every week"
			}
		},
		{
			"name": "Mc Smoogle Corp",
			"acronym": "MCS",
			"current_price": 576.52,
			"benefit": {
				"requirement": 350000,
				"description": "100 Energy every week"
			}
		},
		{
			"name": "Wind Lines Travel",
			"acronym": "WLT",
			"current_price": 459.53,
			"benefit": {
				"requirement": 9000000,
				"description": "Private Jet Access"
			}
		},
		{
			"name": "Torn City Clothing",
			"acronym": "TCC",
			"current_price": 308.35,
			"benefit": {
				"requirement": 7500000,
				"description": "1x Clothing Cache"
			}
		}
	]
