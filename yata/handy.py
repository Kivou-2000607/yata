
# global bonus hits
BONUS_HITS = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000]


def getBonusHits(hitNumber, ts):
    # new report timestamp based on ched annoncement date
    # https://www.torn.com/forums.php#!p=threads&t=16067103
    import datetime
    import time
    if int(ts) < int(time.mktime(datetime.datetime(2018, 10, 30, 15, 00).timetuple())):
        # bonus respect values are 4.2*2**n
        return 4.2 * 2**(1 + float([i for i, x in enumerate(BONUS_HITS) if x == int(hitNumber)][0]))
    else:
        # bonus respect values are 10*2**(n-1)
        return 10 * 2**(int([i for i, x in enumerate(BONUS_HITS) if x == int(hitNumber)][0]))


def timestampToDate(timestamp):
    import datetime
    import pytz
    return datetime.datetime.fromtimestamp(timestamp, tz=pytz.UTC)


def apiCall(section, id, selections, key, sub=None):
    import requests
    # DEBUG live chain
    # if selections == "chain" and section == "faction":
    #     from django.utils import timezone
    #     print("[FUNCTION apiCall] DEBUG chain/faction")
    #     chain = dict({"chain": {"current": 3,
    #                             "timeout": 65,
    #                             "modifier": 0.75,
    #                             "cooldown": 0,
    #                             "start": timezone.now().timestamp()-36000
    #                             }})
    #     return chain[sub] if sub is not None else chain

    # DEBUG API error
    # return dict({"apiError": "API error code 42: debug error."})

    try:
        url = "https://api.torn.com/{}/{}?selections={}&key={}".format(section, id, selections, key)
        print("[FUNCTION apiCall] {}".format(url.replace("&key=" + key, "")))
        r = requests.get(url)
        r.raise_for_status()

        rjson = r.json()

        if "error" in rjson:  # standard api error
            err = rjson
        else:
            if sub is not None:
                if sub in rjson:
                    return rjson[sub]
                else:  # key not found
                    err = dict({"error": {"code": "", "error": "key not found... something went wrong..."}})
            else:
                return rjson

    except requests.exceptions.HTTPError as e:
        print("[FUNCTION apiCall] API HTTPError {}".format(e))
        err = dict({"error": {"code": r.status_code, "error": "{} #blameched".format(r.reason)}})

    return dict({"apiError": "API error code {}: {}.".format(err["error"]["code"], err["error"]["error"])})


def apiCallAttacks(factionId, beginTS, endTS, key):
    import requests
    # WARNING no fallback for this method if api crashed. Will yeld server error.

    # WINS = ["Arrested", "Attacked", "Looted", "None", "Special", "Hospitalized", "Mugged"]

    chain = dict({})

    feedAttacks = True
    i = 1
    while feedAttacks:
        url = "https://api.torn.com/faction/{}?selections=attacks&key={}&from={}&to={}".format(factionId, key, beginTS, endTS)
        print("[FUNCTION apiCallAttacks] call number {}: {}".format(i, url.replace("&key=" + key, "")))
        attacks = requests.get(url).json()["attacks"]
        if len(attacks):
            for j, (k, v)in enumerate(attacks.items()):
                chain[k] = v
                beginTS = max(v["timestamp_ended"] + 1, beginTS)

            if(len(attacks) < 100):
                feedAttacks = False

            print("[FUNCTION apiCallAttacks] Number of attacks: {}".format(len(attacks)))
            i += 1
        else:
            print("[FUNCTION apiCallAttacks] Number of attacks: {}".format(len(attacks)))
            feedAttacks = False

    return chain


def fillReport(faction, members, chain, report, attacks):
    import time
    from django.utils import timezone
    import numpy

    tip = time.time()

    # initialisation of variables before loop
    nWRA = [0, 0.0, 0]  # number of wins, respect and attacks
    bonus = []  # chain bonus
    attacksForHisto = []  # record attacks timestamp histogram

    # create attackers array on the fly to avoid db connection in the loop
    attackers = dict({})
    attackersHisto = dict({})
    for m in members:
        # 0: attacks
        # 1: wins
        # 2: fairFight
        # 3: war
        # 4: retaliation
        # 5: groupAttack
        # 6: overseas
        # 7: chainBonus
        # 8:respect_gain
        # 9: daysInFaction
        # 10: tId
        attackers[m.name] = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, m.daysInFaction, m.tId]

    # loop over attacks
    for k, v in sorted(attacks.items(), key=lambda x: x[1]['timestamp_ended'], reverse=True):
        attackerID = int(v['attacker_id'])
        attackerName = v['attacker_name']
        # if attacker part of the faction at the time of the chain
        if(int(v['attacker_faction']) == faction.tId):
            # if attacker not part of the faction at the time of the call
            if attackerName not in attackers:
                print('[FUNCTION fillReport] hitter out of faction: {}'.format(attackerName))
                attackers[attackerName] = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1, attackerID]  # add out of faction attackers on the fly

            attackers[attackerName][0] += 1
            nWRA[2] += 1

            # if it's a hit
            respect = float(v['respect_gain'])
            if respect > 0.0:
                attacksForHisto.append(v['timestamp_ended'])
                if attackerName in attackersHisto:
                    attackersHisto[attackerName].append(v['timestamp_ended'])
                else:
                    attackersHisto[attackerName] = [v['timestamp_ended']]

                nWRA[0] += 1
                nWRA[1] += respect

                attackers[attackerName][1] += 1
                attackers[attackerName][2] += float(v['modifiers']['fairFight'])
                attackers[attackerName][3] += float(v['modifiers']['war'])
                attackers[attackerName][4] += float(v['modifiers']['retaliation'])
                attackers[attackerName][5] += float(v['modifiers']['groupAttack'])
                attackers[attackerName][6] += float(v['modifiers']['overseas'])
                attackers[attackerName][7] += float(v['modifiers']['chainBonus'])
                attackers[attackerName][8] += respect / float(v['modifiers']['chainBonus'])
                if v['chain'] in BONUS_HITS:
                    r = getBonusHits(v['chain'], v["timestamp_ended"])
                    print('[FUNCTION fillReport] bonus {}: {} respects'.format(v['chain'], r))
                    bonus.append((v['chain'], attackerName, respect, r))

    print('[FUNCTION fillReport] It took {} seconds to build the attacker array'.format(time.time() - tip))
    tip = time.time()

    # create histogram
    chain.start = int(attacksForHisto[-1])
    chain.startDate = timestampToDate(chain.start)
    diff = int(chain.end - chain.start)
    binsGapMinutes = 5
    while diff / (binsGapMinutes * 60) > 256:
        binsGapMinutes += 5

    bins = [chain.start]
    for i in range(256):
        add = bins[i] + (binsGapMinutes * 60)
        if add > chain.end:
            break
        bins.append(add)

    # bins = max(min(int(diff / (5 * 60)), 256), 1)  # min is to limite the number of bins for long chains and max is to insure minimum 1 bin
    print('[FUNCTION fillReport] chain delta time: {} second'.format(diff))
    print('[FUNCTION fillReport] histogram bins delta time: {} second'.format(binsGapMinutes * 60))
    print('[FUNCTION fillReport] histogram number of bins: {}'.format(len(bins) - 1))
    histo, bin_edges = numpy.histogram(attacksForHisto, bins=bins)
    binsCenter = [int(0.5 * (a + b)) for (a, b) in zip(bin_edges[0:-1], bin_edges[1:])]
    chain.nHits = nWRA[0]
    chain.respect = nWRA[1]
    chain.nAttacks = nWRA[2]
    chain.graph = ','.join(['{}:{}'.format(a, b) for (a, b) in zip(binsCenter, histo)])
    chain.save()

    print('[FUNCTION fillReport] It took {} seconds to build histogram'.format(time.time() - tip))
    tip = time.time()

    # fill the database with counts
    print('[FUNCTION fillReport] fill database with counts')
    for k, v in attackers.items():
        # time now - chain end - days old: determine if member was in the fac for the chain
        delta = int(timezone.now().timestamp()) - chain.end - v[9] * 24 * 3600
        beenThere = True if (delta < 0 or v[9] < 0) else False
        if k in attackersHisto:
            histoTmp, _ = numpy.histogram(attackersHisto[k], bins=bins)
            watcher = sum(histoTmp > 0) / float(len(histoTmp)) if len(histo) else 0
            graphTmp = ','.join(['{}:{}'.format(a, b) for (a, b) in zip(binsCenter, histoTmp)])
        else:
            graphTmp = ''
            watcher = 0
        # 0: attacks
        # 1: wins
        # 2: fairFight
        # 3: war
        # 4: retaliation
        # 5: groupAttack
        # 6: overseas
        # 7: chainBonus
        # 8:respect_gain
        # 9: daysInFaction
        # 10: tId
        report.count_set.create(attackerId=v[10],
                                name=k,
                                hits=v[0],
                                wins=v[1],
                                fairFight=v[2],
                                war=v[3],
                                retaliation=v[4],
                                groupAttack=v[5],
                                overseas=v[6],
                                respect=v[8],
                                daysInFaction=v[9],
                                beenThere=beenThere,
                                graph=graphTmp,
                                watcher=watcher)

    print('[FUNCTION fillReport] It took {} seconds to fill the count'.format(time.time() - tip))
    tip = time.time()

    # fill the database with bonus
    print('[FUNCTION fillReport] fill database with bonus')
    for b in bonus:
        report.bonus_set.create(hit=b[0], name=b[1], respect=b[2], respectMax=b[3])

    print('[FUNCTION fillReport] It took {} seconds to fill the bonus'.format(time.time() - tip))
    tip = time.time()

    return chain, report, (binsCenter, histo)


def None2Zero(a):
    return 0 if a is None else a


def honorId2Img(i):
    d = {
		# 0
		617: 312084767,  # 10-Stack
		268: 517070365,  # Wholesaler
		9: 442995373,  # Luxury Real Estate
		395: 579593508,  # Energetic
		607: 210452243,  # Buffed
		21: 819611004,  # Driving Elite
		266: 400884239,  # Energize
		258: 780858042,  # The High Life
		244: 411243367,  # Web Of Perks
		229: 486362984,  # Seeker
		220: 384148528,  # The Affronted
		216: 539384064,  # Silicon Valley
		274: 739693375,  # Redline
		380: 462192588,  # Ecstatic
		167: 363324386,  # Velutinous
		312: 0,  # Time Traveller
		231: 0,  # Discovery
		164: 0,  # Keen
		572: 0,  # Motorhead
		566: 0,  # You've Got Some Nerve
		620: 0,  # OP
		5: 0,  # Journalist
		156: 0,  # RDD
		14: 0,  # Slow Bomb

        # 1
		171: 228001376,  # Afghanistan
		172: 200538715,  # Albania
		173: 722667458,  # Andorra
		66: 269681365,  # Argentina
		67: 276138609,  # Australia
		68: 758276345,  # Austria
		174: 546557225,  # Bahrain
		69: 174762120,  # Bangladesh
		175: 542589113,  # Barbados
		176: 775817841,  # Belarus
		70: 393997506,  # Belgium
		71: 871294991,  # Bosnia & Herzegovina
		72: 892867465,  # Brazil
		73: 763221810,  # Brunei
		74: 631743915,  # Bulgaria
		177: 348170911,  # Cambodia
		75: 848716087,  # Canada
		178: 181705077,  # Chile
		76: 160969203,  # China
		179: 754297818,  # Colombia
		180: 640447143,  # Confederate
		77: 664992125,  # Croatia
		725: 672421294,  # Cuba
		181: 731259760,  # Cyprus
		78: 854703963,  # Czech
		169: 825170128,  # Default
		79: 501801562,  # Denmark
		80: 477364639,  # Egypt
		81: 280564904,  # El Salvador
		170: 859700713,  # England
		82: 650929625,  # Estonia
		83: 321850047,  # Finland
		182: 843932392,  # Former USSR
		84: 516518611,  # France
		204: 608878422,  # Gay Pride
		85: 593392193,  # Germany
		183: 438905351,  # Ghana
		86: 574073677,  # Greece
		184: 215522989,  # Greenland
		87: 343460788,  # Guyana
		186: 314376694,  # Haiti
		88: 264835903,  # Hong Kong
		89: 802774118,  # Hungary
		188: 456078883,  # Iceland
		90: 172258804,  # India
		91: 596218430,  # Indonesia
		92: 304508581,  # Iran
		93: 518140224,  # Iraq
		94: 493325186,  # Ireland
		95: 389262024,  # Israel
		96: 818587564,  # Italy
		189: 692175864,  # Jamaica
		97: 307040980,  # Japan
		190: 187635480,  # Jolly Roger
		191: 926199478,  # Kazakhstan
		192: 144861681,  # Kuwait
		193: 936063304,  # Laos
		98: 313624782,  # Latvia
		99: 806052013,  # Lebanon
		100: 591665400,  # Lithuania
		101: 585376152,  # Malaysia
		102: 614021553,  # Malta
		103: 703539420,  # Mauritius
		104: 496737780,  # Mexico
		194: 167661408,  # Morocco
		105: 160764995,  # Myanmar
		196: 510804187,  # Nepal
		106: 104127319,  # Netherlands
		107: 430044831,  # New Zealand
		197: 690746829,  # Nigeria
		198: 666562225,  # Northern Ireland
		108: 265092870,  # Norway
		199: 771619349,  # Oman
		109: 524790883,  # Pakistan
		200: 471784088,  # Palestine
		201: 620934359,  # Peru
		110: 479877638,  # Philippines
		111: 460282606,  # Poland
		112: 464053606,  # Portugal
		202: 374145733,  # Puerto Rico
		203: 899502521,  # Qatar
		205: 161813438,  # Romania
		113: 940442548,  # Russia
		114: 596579699,  # Saudi Arabia
		206: 833101858,  # Scotland
		115: 354665868,  # Serbia
		116: 653079627,  # Singapore
		117: 541205309,  # Slovakia
		118: 170927545,  # Slovenia
		119: 128027014,  # South Africa
		120: 528148922,  # South Korea
		121: 694700670,  # Spain
		207: 781431703,  # Sri Lanka
		168: 435540163,  # Standard Bar
		122: 923018852,  # Sweden
		123: 472883748,  # Switzerland
		208: 726998058,  # Taiwan
		124: 631970519,  # Thailand
		209: 254533819,  # Tunisia
		125: 703605883,  # Turkey
		210: 566722083,  # Ukraine
		126: 711956775,  # United Arab Emirates
		127: 583611652,  # United Kingdom
		211: 923289734,  # United Nations
		65: 808447850,  # United States
		726: 206977670,  # Uruguay
		128: 535956474,  # Vietnam
		129: 415068830,  # Wales

        # 2
        149: 138334568,  # The Stabbist
        150: 526451239,  # Slasher
        146: 788312531,  # 2800 Ft/S
        142: 441555606,  # Axe Wound
        148: 363437922,  # Act Of Faith
        145: 984865664,  # Yours Says Replica...
        147: 367511662,  # Cartridge Packer
        141: 267309487,  # Stumped
        144: 444089484,  # Lend A Hand
        28: 835735982,  # Machinist
        143: 744664817,  # Pin Puller
        515: 245161575,  # Unarmed

		# 3
		39: 198010293,  # Woodland Camo
		40: 110459989,  # Desert Storm Camo
		41: 124793397,  # Urban Camo
		42: 281152456,  # Arctic Camo
		43: 144330126,  # Fall Camo
		44: 311866173,  # Yellow Camo
		45: 120184469,  # Digital Camo
		46: 915200783,  # Red Camo
		47: 981248146,  # Blue Camo
		48: 777643835,  # Orange Camo
		50: 0,  # Zebra Skin
		51: 0,  # Leopard Skin
		49: 0,  # Pink Camo
		52: 0,  # Tiger Skin

		# 4
		653: 872280837,  # Smart Alec
		55: 920148790,  # Combat Bachelor
		60: 145755443,  # History Bachelor
		56: 189007328,  # ICT Bachelor
		64: 478147325,  # Sports Bachelor
		63: 577782139,  # Psychology Bachelor
		54: 400541661,  # Business Bachelor
		57: 0,  # Defense Bachelor
		58: 0,  # General Bachelor
		53: 0,  # Biology Bachelor
		59: 0,  # Fitness Bachelor
		61: 0,  # Law Bachelor
		62: 0,  # Mathematics Bachelor
		530: 0,  # Talented
		525: 0,  # Tireless
		533: 0,  # Tough

		# 5
		25: 566282329,  # Candy Man
		157: 486487597,  # Smile, You're On Camera
		251: 940653341,  # Society's Worst
		161: 603343376,  # Bug
		24: 455713236,  # Fire Starter
		552: 409748477,  # Mastermind
		153: 193222093,  # Escobar
		2: 0,  # Smokin' Barrels
		158: 0,  # Breaking And Entering
		154: 0,  # Stroke Bringer
		6: 0,  # Find A Penny, Pick It Up
		155: 0,  # We Have A Breach
		160: 0,  # Joy Rider
		152: 0,  # Civil Offence
		159: 0,  # Professional

		# 6
		37: 602282262,  # Free Energy
		30: 196995484,  # Party Animal
		29: 750345257,  # Who's Frank?
		26: 499675289,  # Spaced Out
		38: 0,  # Painkiller
		32: 0,  # Acid Dream
		31: 0,  # Horse Tranquilizer
		34: 0,  # I Think I See Dead People
		33: 0,  # The Fields Of Opium
		36: 0,  # Angel Dust
		35: 0,  # Crank It Up

        # 7
        11: 241952085,  # Mile High Club
        549: 724568067,  # Tourist
        131: 647632452,  # Cascado
        136: 371218685,  # Cape Town
        137: 450089156,  # Like The Celebs
        139: 510088358,  # Toronto
        135: 887351771,  # British Pride
        272: 779401199,  # Shark Bait
        138: 956584838,  # Year Of The Dragon
        130: 697523940,  # Maradona
        132: 445049088,  # Land Of Promise
        567: 891235999,  # Frequent Flyer
        133: 545258345,  # Hula
        134: 759640199,  # The Rising Sun
        165: 317282935,  # There And Back

		# 8
		20: 778719620,  # Precision
		15: 303172651,  # Kill Streaker 1
		230: 623515559,  # Domino Effect
		140: 848136489,  # Spray And Pray
		254: 445969768,  # Flatline
		27: 751012417,  # Night Walker
		253: 928605417,  # Chainer 1
		247: 694423307,  # Blood Money
		481: 119550579,  # Semper     Fortis
		255: 854310530,  # Chainer 2
		256: 202622962,  # Carnage
		257: 597531894,  # Chainer 3
		151: 208481636,  # Two Halves Make A Hole
		16: 398400273,  # Kill Streaker 2
		517: 831091914,  # Pressure Point
		236: 115202393,  # Dead Or Alive
		227: 153489781,  # 50 Cal
		601: 660878966,  # Fury
		615: 120694345,  # Guardian Angel
		500: 764616509,  # Survivalist
		639: 711079121,  # Double Dragon
		475: 758263946,  # Chainer 4
		477: 352979366,  # Massacre
		478: 171416497,  # Genocide
		22: 0,  # Self Defense
		270: 0,  # Deadlock
		232: 0,  # Bounty Hunter
		228: 0,  # 007
		17: 0,  # Kill Streaker 3
		490: 0,  # Sidekick
		476: 0,  # Chainer 5

		# 9
		431: 733603085,  # Lame
		437: 703700900,  # Mediocre
		427: 893742097,  # Awesome
		338: 929197424,  # Twenty-One
		269: 739646998,  # Spinner
		327: 796833908,  # One in Six
		326: 156400756,  # Highs and Lows
		513: 814368109,  # Daddys New Shoes
		276: 494694037,  # Lucky Break
		237: 0,  # Poker King
		275: 0,  # Jackpot

        # 10
        687: 835636011,  # Lean
        233: 439667520,  # Bronze Belt
        720: 304884624,  # Fit
        686: 348857600,  # Healthy
        243: 863707160,  # Abaddon
        234: 511356030,  # Silver Belt
        723: 907581608,  # Toned
        240: 362146978,  # Behemoth
        242: 773994822,  # Phoenix
        694: 978318797,  # Athletic
        241: 611520665,  # Draco
        643: 867197599,  # Powerhouse
        505: 457583274,  # Turbocharged
        497: 168691956,  # Reinforced
        635: 162644761,  # Freerunner
        646: 164338289,  # Mighty Roar
        235: 877994898,  # Gold Belt
        506: 926799069,  # Lightspeed
        640: 795066538,  # Bulletproof

		# 11
		163: 431464057,  # Fascination
		309: 959806366,  # Christmas in Torn
		162: 636752583,  # Chasm
		459: 332983521,  # Torniversary
		443: 513488839,  # Trick or Treat
		223: 350797134,  # The Socialist
		217: 438803717,  # Two's Company
		245: 965199742,  # Couch Potato
		316: 240827340,  # Forgiven
		218: 294488415,  # Three's a Crowd
		219: 534607883,  # Social Butterfly
		246: 536984897,  # Pyramid Scheme
		166: 0,  # Stairway To Heaven

		# 12
		18: 978797305,  # Another Brick In The Wall
		259: 587092963,  # Half Way There
		13: 0,  # The Beautiful City
		264: 0,  # The Whole Nine Yards
		265: 0,  # To The Limit

		# 13
		283: 363100539,  # Globule
		226: 783491253,  # Purple Heart
		222: 566217580,  # Good Friday
		308: 192941769,  # Retro
		313: 215124214,  # Serenity
		298: 486913102,  # Acute
		318: 498954762,  # Futurity
		297: 733807792,  # Constellations
		221: 844457156,  # KIA
		281: 449722729,  # Parallel
		215: 431217843,  # Labyrinth
		280: 790762265,  # Supremacy
		213: 576433461,  # Allure
		284: 485677656,  # Electric Dream
		212: 0,  # Mission Accomplished
		214: 0,  # Jack Of All Trades
		224: 0,  # Proven Capacity
		225: 0,  # Master Of One
		278: 0,  # Globally Effective
		315: 0,  # Glimmer
		306: 0,  # Resistance
		279: 0,  # Domination
		321: 0,  # Supernova
		294: 0,  # Pepperoni
		263: 0,  # Survivor
		277: 0,  # Departure
		311: 0,  # Brainz
		330: 0,  # Champion

        # 14
        12: 533285823,  # Pocket Money
        10: 927018892,  # Green, Green Grass
        3: 234842928,  # Moneybags
        8: 602403620,  # Loan Shark
        546: 543547927,  # Dividend
        19: 890959235,  # Stock Analyst

		# 15
		367: 474813486,  # Clotted
		406: 534029106,  # Vampire
		418: 832724939,  # Transfusion
		7: 559177183,  # Magical Veins
		398: 670385087,  # Anaemic
		4: 0,  # I'm a Real Doctor
		248: 0,  # Bar Breaker
		252: 0,  # Freedom Isn't Free
		249: 0,  # Aiding And Abetting
		23: 0,  # Florence Nightingale
		267: 0,  # Second Chance
		250: 0,  # Don't Drop It

		# 16
		239: 275270401,  # Middleman
		1: 315115646,  # I'm Watching You
		271: 969012100,  # Eco Friendly
		273: 121155579,  # Bargain Hunter
		537: 614179864,  # Diabetic
		534: 124108189,  # Alcoholic
		238: 0,  # Optimist
		538: 0,  # Sodaholic
		527: 0,  # Worth it
		539: 0,  # Bibliophile

        # 17
        371: 668653618,  # Protege
        }

    return d.get(i) if d.get(i) > 0 else None
