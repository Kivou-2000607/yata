from django.db import models

from datetime import datetime
from yata.BulkManager2 import BulkManager

class Stock(models.Model):
    torn_id = models.IntegerField(default=0, db_index=True)
    acronym = models.CharField(default="-", max_length=8, db_index=True)
    name = models.CharField(default="-", max_length=64)

    # prices tendencies
    tendency_l_a = models.FloatField(default=0.0)
    # tendency_l_b = models.FloatField(default=0.0)
    tendency_h_a = models.FloatField(default=0.0)
    tendency_h_b = models.FloatField(default=0.0)
    tendency_d_a = models.FloatField(default=0.0)
    tendency_d_b = models.FloatField(default=0.0)
    tendency_w_a = models.FloatField(default=0.0)
    tendency_w_b = models.FloatField(default=0.0)
    tendency_m_a = models.FloatField(default=0.0)
    tendency_m_b = models.FloatField(default=0.0)
    tendency_y_a = models.FloatField(default=0.0)
    tendency_y_b = models.FloatField(default=0.0)

    # market cap tendencies
    tendency_l_c = models.FloatField(default=0.0)
    # tendency_l_d = models.FloatField(default=0.0)
    tendency_h_c = models.FloatField(default=0.0)
    tendency_h_d = models.FloatField(default=0.0)
    tendency_d_c = models.FloatField(default=0.0)
    tendency_d_d = models.FloatField(default=0.0)
    tendency_w_c = models.FloatField(default=0.0)
    tendency_w_d = models.FloatField(default=0.0)
    tendency_m_c = models.FloatField(default=0.0)
    tendency_m_d = models.FloatField(default=0.0)
    tendency_y_c = models.FloatField(default=0.0)
    tendency_y_d = models.FloatField(default=0.0)

    timestamp = models.IntegerField(default=0)

    # current_price
    current_price = models.FloatField(default=0.0)
    previous_price = models.FloatField(default=0.0)

    # global
    market_cap = models.BigIntegerField(default=0)
    total_shares = models.BigIntegerField(default=0)
    previous_market_cap = models.BigIntegerField(default=0)
    previous_total_shares = models.BigIntegerField(default=0)

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


ALL_STOCKS = {
	"1": {
		"name": "Torn & Shanghai Banking",
		"acronym": "TSB",
		"current_price": 813.98,
		"market_cap": 9205047820746,
		"total_shares": 11308690411,
		"benefit": {
			"requirement": 3000000,
			"description": "$50,000,000 every month"
		}
	},
	"2": {
		"name": "Torn City Investments",
		"acronym": "TCB",
		"current_price": 891.29,
		"market_cap": 9424810902546,
		"total_shares": 10574348307,
		"benefit": {
			"requirement": 1500000,
			"description": "a 10% Bank Interest Bonus"
		}
	},
	"3": {
		"name": "Syscore MFG",
		"acronym": "SYS",
		"current_price": 478.07,
		"market_cap": 2735136974889,
		"total_shares": 5721206047,
		"benefit": {
			"requirement": 3000000,
			"description": "an Advanced Firewall"
		}
	},
	"4": {
		"name": "Legal Authorities Group",
		"acronym": "LAG",
		"current_price": 298.82,
		"market_cap": 1818458553586,
		"total_shares": 6085464673,
		"benefit": {
			"requirement": 750000,
			"description": "1x Lawyer Business Card every week"
		}
	},
	"5": {
		"name": "Insured On Us",
		"acronym": "IOU",
		"current_price": 142.57,
		"market_cap": 3704477553800,
		"total_shares": 25983569852,
		"benefit": {
			"requirement": 3000000,
			"description": "$12,000,000 every month"
		}
	},
	"6": {
		"name": "Grain",
		"acronym": "GRN",
		"current_price": 217.78,
		"market_cap": 1699457430208,
		"total_shares": 7803551429,
		"benefit": {
			"requirement": 500000,
			"description": "$4,000,000 every month"
		}
	},
	"7": {
		"name": "Torn City Health Service",
		"acronym": "THS",
		"current_price": 329.06,
		"market_cap": 3125383193865,
		"total_shares": 9497912824,
		"benefit": {
			"requirement": 150000,
			"description": "1x Box of Medical Supplies every week"
		}
	},
	"8": {
		"name": "Yazoo",
		"acronym": "YAZ",
		"current_price": 36.24,
		"market_cap": 1992688582606,
		"total_shares": 54985888041,
		"benefit": {
			"requirement": 1000000,
			"description": "Free Banner Advertising"
		}
	},
	"9": {
		"name": "The Torn City Times",
		"acronym": "TCT",
		"current_price": 227,
		"market_cap": 417699711318,
		"total_shares": 1840086834,
		"benefit": {
			"requirement": 100000,
			"description": "$1,000,000 every month"
		}
	},
	"10": {
		"name": "Crude & Co",
		"acronym": "CNC",
		"current_price": 671.13,
		"market_cap": 3002595811924,
		"total_shares": 4473940685,
		"benefit": {
			"requirement": 7500000,
			"description": "$80,000,000 every month"
		}
	},
	"11": {
		"name": "Messaging Inc.",
		"acronym": "MSG",
		"current_price": 151.36,
		"market_cap": 2687750520601,
		"total_shares": 17757336949,
		"benefit": {
			"requirement": 300000,
			"description": "Free Classified Advertising"
		}
	},
	"12": {
		"name": "TC Music Industries",
		"acronym": "TMI",
		"current_price": 153.13,
		"market_cap": 5349197926119,
		"total_shares": 34932396827,
		"benefit": {
			"requirement": 6000000,
			"description": "$25,000,000 every month"
		}
	},
	"13": {
		"name": "TC Media Productions",
		"acronym": "TCP",
		"current_price": 275.68,
		"market_cap": 1224967852924,
		"total_shares": 4443441138,
		"benefit": {
			"requirement": 1000000,
			"description": "a Company Sales Boost"
		}
	},
	"14": {
		"name": "I Industries Ltd.",
		"acronym": "IIL",
		"current_price": 86.53,
		"market_cap": 1515553315910,
		"total_shares": 17514773095,
		"benefit": {
			"requirement": 1000000,
			"description": "50% Coding Time Reduction"
		}
	},
	"15": {
		"name": "Feathery Hotels Group",
		"acronym": "FHG",
		"current_price": 566.79,
		"market_cap": 21891636695487,
		"total_shares": 38623893674,
		"benefit": {
			"requirement": 2000000,
			"description": "1x Feathery Hotel Coupon every week"
		}
	},
	"16": {
		"name": "Symbiotic Ltd.",
		"acronym": "SYM",
		"current_price": 731.55,
		"market_cap": 8705735396820,
		"total_shares": 11900396961,
		"benefit": {
			"requirement": 500000,
			"description": "1x Drug Pack every week"
		}
	},
	"17": {
		"name": "Lucky Shots Casino",
		"acronym": "LSC",
		"current_price": 375.95,
		"market_cap": 3054414681256,
		"total_shares": 8124523690,
		"benefit": {
			"requirement": 500000,
			"description": "1x Lottery Voucher every week"
		}
	},
	"18": {
		"name": "Performance Ribaldry",
		"acronym": "PRN",
		"current_price": 492.32,
		"market_cap": 7696943424314,
		"total_shares": 15634025480,
		"benefit": {
			"requirement": 1000000,
			"description": "1x Erotic DVD every week"
		}
	},
	"19": {
		"name": "Eaglewood Mercenary",
		"acronym": "EWM",
		"current_price": 270.26,
		"market_cap": 1674149717461,
		"total_shares": 6194589349,
		"benefit": {
			"requirement": 1000000,
			"description": "1x Box of Grenades every week"
		}
	},
	"20": {
		"name": "Torn City Motors",
		"acronym": "TCM",
		"current_price": 307.62,
		"market_cap": 548728570475,
		"total_shares": 1783787044,
		"benefit": {
			"requirement": 1000000,
			"description": "10% Racing Skill Boost"
		}
	},
	"21": {
		"name": "Empty Lunchbox Traders",
		"acronym": "ELT",
		"current_price": 181.29,
		"market_cap": 1126779057671,
		"total_shares": 6215340381,
		"benefit": {
			"requirement": 5000000,
			"description": "10% Home Upgrade Discount"
		}
	},
	"22": {
		"name": "Home Retail Group",
		"acronym": "HRG",
		"current_price": 208.17,
		"market_cap": 8829266222187,
		"total_shares": 42413730231,
		"benefit": {
			"requirement": 10000000,
			"description": "1x Random Property"
		}
	},
	"23": {
		"name": "Tell Group Plc.",
		"acronym": "TGP",
		"current_price": 89.47,
		"market_cap": 1464515359470,
		"total_shares": 16368786850,
		"benefit": {
			"requirement": 2500000,
			"description": "a Company Advertising Boost"
		}
	},
	"25": {
		"name": "West Side University",
		"acronym": "WSU",
		"current_price": 65.04,
		"market_cap": 2809147102329,
		"total_shares": 43191068609,
		"benefit": {
			"requirement": 1000000,
			"description": "a 10% Education Course Duration Reduction"
		}
	},
	"26": {
		"name": "International School TC",
		"acronym": "IST",
		"current_price": 317.84,
		"market_cap": 268278917341,
		"total_shares": 844069083,
		"benefit": {
			"requirement": 100000,
			"description": "Free Education Courses"
		}
	},
	"27": {
		"name": "Big Al's Gun Shop",
		"acronym": "BAG",
		"current_price": 417.64,
		"market_cap": 2857121787649,
		"total_shares": 6841111454,
		"benefit": {
			"requirement": 3000000,
			"description": "1x Ammunition Pack"
		}
	},
	"28": {
		"name": "Evil Ducks Candy Corp",
		"acronym": "EVL",
		"current_price": 373.1,
		"market_cap": 2352404495068,
		"total_shares": 6305024109,
		"benefit": {
			"requirement": 100000,
			"description": "1000 Happiness every week"
		}
	},
	"29": {
		"name": "Mc Smoogle Corp",
		"acronym": "MCS",
		"current_price": 587.22,
		"market_cap": 10975550397072,
		"total_shares": 18690695816,
		"benefit": {
			"requirement": 350000,
			"description": "100 Energy every week"
		}
	},
	"30": {
		"name": "Wind Lines Travel",
		"acronym": "WLT",
		"current_price": 449.92,
		"market_cap": 12799927500021,
		"total_shares": 28449340994,
		"benefit": {
			"requirement": 9000000,
			"description": "Private Jet Access"
		}
	},
	"31": {
		"name": "Torn City Clothing",
		"acronym": "TCC",
		"current_price": 303.99,
		"market_cap": 1549280680647,
		"total_shares": 5096485676,
		"benefit": {
			"requirement": 7500000,
			"description": "1x Clothing Cache"
		}
	}
}
