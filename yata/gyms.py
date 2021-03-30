import numpy
import re

gyms = {
    1: {
        "name": "Premier Fitness",
        "stage": 1,
        "cost": 10,
        "energy": 5,
        "strength": 20,
        "speed": 20,
        "defense": 20,
        "dexterity": 20,
        "unlock_e": 200,
        "note": ""
    },
    2: {
        "name": "Average Joes",
        "stage": 1,
        "cost": 100,
        "energy": 5,
        "strength": 24,
        "speed": 24,
        "defense": 27.999999999999996,
        "dexterity": 24,
        "unlock_e": 500,
        "note": ""
    },
    3: {
        "name": "Woody's Workout Club",
        "stage": 1,
        "cost": 250,
        "energy": 5,
        "strength": 27.999999999999996,
        "speed": 32,
        "defense": 30,
        "dexterity": 27.999999999999996,
        "unlock_e": 1000,
        "note": ""
    },
    4: {
        "name": "Beach Bods",
        "stage": 1,
        "cost": 500,
        "energy": 5,
        "strength": 32,
        "speed": 32,
        "defense": 32,
        "dexterity": 0,
        "unlock_e": 2000,
        "note": ""
    },
    5: {
        "name": "Silver Gym",
        "stage": 1,
        "cost": 1000,
        "energy": 5,
        "strength": 33.99999999999999,
        "speed": 36,
        "defense": 33.99999999999999,
        "dexterity": 32,
        "unlock_e": 2750,
        "note": ""
    },
    6: {
        "name": "Pour Femme",
        "stage": 1,
        "cost": 2500,
        "energy": 5,
        "strength": 33.99999999999999,
        "speed": 36,
        "defense": 36,
        "dexterity": 38,
        "unlock_e": 3000,
        "note": ""
    },
    7: {
        "name": "Davies Den",
        "stage": 1,
        "cost": 5000,
        "energy": 5,
        "strength": 37,
        "speed": 0,
        "defense": 37,
        "dexterity": 37,
        "unlock_e": 3500,
        "note": ""
    },
    8: {
        "name": "Global Gym",
        "stage": 1,
        "cost": 10000,
        "energy": 5,
        "strength": 40,
        "speed": 40,
        "defense": 40,
        "dexterity": 40,
        "unlock_e": 4000,
        "note": ""
    },
    9: {
        "name": "Knuckle Heads",
        "stage": 2,
        "cost": 50000,
        "energy": 10,
        "strength": 48,
        "speed": 44.00000000000001,
        "defense": 40,
        "dexterity": 42.00000000000001,
        "unlock_e": 6000,
        "note": ""
    },
    10: {
        "name": "Pioneer Fitness",
        "stage": 2,
        "cost": 100000,
        "energy": 10,
        "strength": 44.00000000000001,
        "speed": 46,
        "defense": 48,
        "dexterity": 44.00000000000001,
        "unlock_e": 7000,
        "note": ""
    },
    11: {
        "name": "Anabolic Anomalies",
        "stage": 2,
        "cost": 250000,
        "energy": 10,
        "strength": 50,
        "speed": 46,
        "defense": 52,
        "dexterity": 46,
        "unlock_e": 8000,
        "note": ""
    },
    12: {
        "name": "Core",
        "stage": 2,
        "cost": 500000,
        "energy": 10,
        "strength": 50,
        "speed": 52,
        "defense": 50,
        "dexterity": 50,
        "unlock_e": 11000,
        "note": ""
    },
    13: {
        "name": "Racing Fitness",
        "stage": 2,
        "cost": 1000000,
        "energy": 10,
        "strength": 50,
        "speed": 54,
        "defense": 48,
        "dexterity": 52,
        "unlock_e": 12420,
        "note": ""
    },
    14: {
        "name": "Complete Cardio",
        "stage": 2,
        "cost": 2000000,
        "energy": 10,
        "strength": 55.00000000000001,
        "speed": 57.999999999999986,
        "defense": 55.00000000000001,
        "dexterity": 52,
        "unlock_e": 18000,
        "note": ""
    },
    15: {
        "name": "Legs, Bums and Tums",
        "stage": 2,
        "cost": 3000000,
        "energy": 10,
        "strength": 0,
        "speed": 55.99999999999999,
        "defense": 55.99999999999999,
        "dexterity": 57.999999999999986,
        "unlock_e": 18100,
        "note": ""
    },
    16: {
        "name": "Deep Burn",
        "stage": 2,
        "cost": 5000000,
        "energy": 10,
        "strength": 60,
        "speed": 60,
        "defense": 60,
        "dexterity": 60,
        "unlock_e": 24140,
        "note": ""
    },
    17: {
        "name": "Apollo Gym",
        "stage": 3,
        "cost": 7500000,
        "energy": 10,
        "strength": 60,
        "speed": 62,
        "defense": 64,
        "dexterity": 62,
        "unlock_e": 31260,
        "note": ""
    },
    18: {
        "name": "Gun Shop",
        "stage": 3,
        "cost": 10000000,
        "energy": 10,
        "strength": 65.99999999999999,
        "speed": 64,
        "defense": 62,
        "dexterity": 62,
        "unlock_e": 36610,
        "note": ""
    },
    19: {
        "name": "Force Training",
        "stage": 3,
        "cost": 15000000,
        "energy": 10,
        "strength": 64,
        "speed": 65.99999999999999,
        "defense": 64,
        "dexterity": 67.99999999999999,
        "unlock_e": 46640,
        "note": ""
    },
    20: {
        "name": "Cha Cha's",
        "stage": 3,
        "cost": 20000000,
        "energy": 10,
        "strength": 64,
        "speed": 64,
        "defense": 67.99999999999999,
        "dexterity": 70,
        "unlock_e": 56520,
        "note": ""
    },
    21: {
        "name": "Atlas",
        "stage": 3,
        "cost": 30000000,
        "energy": 10,
        "strength": 70,
        "speed": 64,
        "defense": 64,
        "dexterity": 65.99999999999999,
        "unlock_e": 67775,
        "note": ""
    },
    22: {
        "name": "Last Round",
        "stage": 3,
        "cost": 50000000,
        "energy": 10,
        "strength": 67.99999999999999,
        "speed": 65.99999999999999,
        "defense": 70,
        "dexterity": 65.99999999999999,
        "unlock_e": 84525,
        "note": ""
    },
    23: {
        "name": "The Edge",
        "stage": 3,
        "cost": 75000000,
        "energy": 10,
        "strength": 67.99999999999999,
        "speed": 70,
        "defense": 70,
        "dexterity": 67.99999999999999,
        "unlock_e": 106305,
        "note": ""
    },
    24: {
        "name": "George's",
        "stage": 3,
        "cost": 100000000,
        "energy": 10,
        "strength": 73,
        "speed": 73,
        "defense": 73,
        "dexterity": 73,
        "unlock_e": 0,
        "note": ""
    },
    25: {
        "name": "Balboas Gym",
        "stage": 4,
        "cost": 50000000,
        "energy": 25,
        "strength": 0,
        "speed": 0,
        "defense": 75,
        "dexterity": 75,
        "unlock_e": 0,
        "note": "Requirements must be maintained to preserve access to this gym"
    },
    26: {
        "name": "Frontline Fitness",
        "stage": 4,
        "cost": 50000000,
        "energy": 25,
        "strength": 75,
        "speed": 75,
        "defense": 0,
        "dexterity": 0,
        "unlock_e": 0,
        "note": "Requirements must be maintained to preserve access to this gym"
    },
    27: {
        "name": "Gym 3000",
        "stage": 4,
        "cost": 100000000,
        "energy": 50,
        "strength": 80,
        "speed": 0,
        "defense": 0,
        "dexterity": 0,
        "unlock_e": 0,
        "note": "Requirements must be maintained to preserve access to this gym"
    },
    28: {
        "name": "Mr. Isoyamas",
        "stage": 4,
        "cost": 100000000,
        "energy": 50,
        "strength": 0,
        "speed": 0,
        "defense": 80,
        "dexterity": 0,
        "unlock_e": 0,
        "note": "Requirements must be maintained to preserve access to this gym"
    },
    29: {
        "name": "Total Rebound",
        "stage": 4,
        "cost": 100000000,
        "energy": 50,
        "strength": 0,
        "speed": 80,
        "defense": 0,
        "dexterity": 0,
        "unlock_e": 0,
        "note": "Requirements must be maintained to preserve access to this gym"
    },
    30: {
        "name": "Elites",
        "stage": 4,
        "cost": 100000000,
        "energy": 50,
        "strength": 0,
        "speed": 0,
        "defense": 0,
        "dexterity": 80,
        "unlock_e": 0,
        "note": "Requirements must be maintained to preserve access to this gym"
    },
    31: {
        "name": "The Sports Science Lab",
        "stage": 4,
        "cost": 500000000,
        "energy": 25,
        "strength": 90,
        "speed": 90,
        "defense": 90,
        "dexterity": 90,
        "unlock_e": 0,
        "note": "The use of drugs may result in the loss of membership without refunds"
    },
    32: {
        "name": "Unknown",
        "stage": 4,
        "cost": 2147483647,
        "energy": 10,
        "strength": 100,
        "speed": 100,
        "defense": 100,
        "dexterity": 100,
        "unlock_e": 0,
        "note": "Membership by invite only"
    },
    33: {
        "name": "The Jail Gym",
        "stage": 0,
        "cost": 2147483647,
        "energy": 5,
        "strength": 33.99999999999999,
        "speed": 33.99999999999999,
        "defense": 46,
        "dexterity": 0,
        "unlock_e": 0,
        "note": ""
    }
}


stat_types = ["strength", "speed", "dexterity", "defense"]


def get_happy(req):
    return req.get("happy", {"maximum": 250})["maximum"]


def get_gym(req):
    active_gym = req.get("active_gym", 1)
    return {k: gyms.get(active_gym).get(k, 20) / 10.0 for k in stat_types}, gyms.get(active_gym).get("name")


def get_bonus(req):
    perks = {k: 0.0 for k in stat_types}

    for stat in stat_types:
        perks_list = []
        # faction perk
        for p in req.get("faction_perks", []):
            reg = '\+ increases {} gym gains by \d{{1,3}}\%'.format(stat)
            if re.match(reg, p.lower()) is not None:
                bonus = p.replace("%", "").replace("+", "").strip().split(" ")[-1]
                bonus = int(bonus) if bonus.isdigit() else -1
                perks_list.append(bonus)
                continue

        # education perks
        for p in req.get("education_perks", []):
            # specific gym
            reg = '\+ \d{{1,3}}\% {} gym gains'.format(stat)
            if re.match(reg, p.lower()) is not None:
                bonus = p.replace("%", "").replace("+", "").strip().split(" ")[0]
                bonus = int(bonus) if bonus.isdigit() else -1
                perks_list.append(bonus)
                continue

            # all gyms
            # reg = '\+ \d{1,3}\% gym gains'
            # if re.match(reg, p.lower()) is not None:
            if p == "+ 1% Gym gains":
                bonus = p.replace("%", "").replace("+", "").strip().split(" ")[0]
                bonus = int(bonus) if bonus.isdigit() else -1
                perks_list.append(bonus)
                continue

        # property perks
        for p in req.get("property_perks", []):
            # specific gym
            reg = '\+ \d{{1,3}}\% gym gains'.format(stat)
            if re.match(reg, p.lower()) is not None:
                bonus = p.replace("%", "").replace("+", "").strip().split(" ")[0]
                bonus = int(bonus) if bonus.isdigit() else -1
                perks_list.append(bonus)
                continue

        # book perks
        for p in req.get("book_perks", []):
            # "book_perks": ["+ Increases Speed gym gains by 30% for 31 days"]
            # specific gym
            reg = '\+ increases {} gym gains by \d{{1,3}}\% for 31 days'.format(stat)
            if re.match(reg, p.lower()) is not None:
                bonus = p.replace("%", "").replace("+", "").strip().split(" ")[5]
                bonus = int(bonus) if bonus.isdigit() else -1
                perks_list.append(bonus)
                continue

        # company perks
        for p in req.get("company_perks", []):
            # all gym
            reg = '\+ \d{{1,3}}\% gym gains'.format(stat)
            if re.match(reg, p.lower()) is not None:
                bonus = p.replace("%", "").replace("+", "").strip().split(" ")[0]
                bonus = int(bonus) if bonus.isdigit() else -1
                perks_list.append(bonus)
                continue

            # specific gym
            reg = '\+ \d{{1,3}}\% {} gym gains'.format(stat)
            if re.match(reg, p.lower()) is not None:
                bonus = p.replace("%", "").replace("+", "").strip().split(" ")[0]
                bonus = int(bonus) if bonus.isdigit() else -1
                perks_list.append(bonus)
                continue

        b_perks = [1 + p / 100. for p in perks_list]
        perks[stat] = numpy.prod(b_perks) - 1.
    return perks


def bs_e(si, sf, H=250, B=0.0, G=1.0, verbose=False):
    """Returns the energy needed given:
        si: the initial stat
        so: the final stat
        H: the happy
        B: the gym perks bonus
        G: the gym dot bonus

        note: it account automatically account for pre/post cap
    """

    sc = 50000000.

    # states coefficients
    a = 1. / 200000.
    alpha = a * (1. + 0.07 * numpy.log(1 + H / 250.)) * (1 + B) * G
    beta = a * 12.75 * H * (1 + B) * G

    # shortcuts
    minf = min(sc, sf)
    mini = min(sc, si)
    maxf = max(sc, sf)
    maxi = max(sc, si)
    ratio = numpy.divide(beta, alpha)
    slope = alpha * sc + beta

    # energy before cap
    dE_bc = numpy.divide(numpy.log(numpy.divide(minf + ratio, mini + ratio)), alpha)
    # print(dE_bc[0], numpy.log((minf + ratio) / (mini + ratio))[0], alpha[0])
    # energy after cap
    dE_ac = numpy.divide(maxf - maxi, slope)
    # energy total
    dE = dE_bc + dE_ac

    if verbose == 1:
        print(f"h = {H:.4g}, b = {B:.4g}, g = {G:.4g}")
    elif verbose == 2:
        print("=== Battle stats formula ===")
        print("")
        print("= States variables =")
        print(f"Happy: {H:.4g}")
        print(f"Bonus: {B:.4g}")
        print(f"Gym dot: {G:.4g}")
        print("")
        print("= States coefficients =")
        print(f"alpha: {alpha:.4g}")
        print(f"beta: {beta:.4g}")
        print("")
        print("= Energy =")
        print(f"Before CAP: {dE_bc:,.1f}")
        print(f"After CAP: {dE_ac:,.1f}")
        print(f"Total: {dE:,.1f}")

    return dE
