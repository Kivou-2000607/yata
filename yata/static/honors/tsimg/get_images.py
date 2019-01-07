import os

ts = {
    # 0
    164: "8ZoTY",  # Keen
    620: "6LTvzXx",  # OP
    5: "hV0Xo",  # Journalist
    156: "IqBED",  # RDD
    14: "bDcya",  # Slow Bomb

    # 3
    50: "R9wDs",  # Zebra Skin
    51: "cjwMr",  # Leopard Skin
    52: "nR7S3",  # Tiger Skin

    # 4
    533: "hJeTEPU",  # Tough

    # 5
    154: "q4Ce9",  # Stroke Bringer
    6: "wcGkF",  # Find A Penny, Pick It Up
    160: "UjZrd",  # Joy Rider
    152: "rN2sM",  # Civil Offence
    159: "WxTd0",  # Professional

    # 6
    31: "8vnqj",  # Horse Tranquilizer
    32: "2Pr9J",  # Acid Dream
    33: "5Vmp8",  # The Fields Of Opium
    34: "HGcaP",  # I Think I See Dead People
    36: "MLgws",  # Angel Dust
    35: "R6JO7",  # Crank It Up

    # 8
    228: "MC3FW",  # 007
    17: "sDp0i",  # Kill Streaker 3
    490: "3Z5kBEa",  # Sidekick
    476: 0,  # Chainer 5

    # 9
    237: "NQ5Yy",  # Poker King
    275: "u4YzC",  # Jackpot

    # 12
    264: "ncl1H",  # The Whole Nine Yards
    265: "Hfzxg",  # To The Limit

    # 13
    224: "Os4BB",  # Proven Capacity
    225: "8Nrzi",  # Master Of One
    278: "Ls7pb",  # Globally Effective
    279: "Nw23Hzi",  # Domination
    294: "zZv0Sz7",  # Pepperoni
    263: "iKUPG",  # Survivor
    277: "EiVrjiy",  # Departure
    311: "COyyoPc",  # Brainz
    330: "fd9C6cz",  # Champion

    # 15
    249: "ySUG9",  # Aiding And Abetting
    23: "4FMUx",  # Florence Nightingale
    267: "AMoyz",  # Second Chance
    250: "CWjSK",  # Don't Drop It

    # 16
    538: "DAYdk2N",  # Sodaholic
    527: "S4845LN",  # Worth it
    539: "5xmayVr",  # Bibliophile

    }




for k, v in ts.items():
    print( "get image:", k, v )
    url = "https://i.imgur.com/{}.png".format(v)
    print( url )
    os.system( "wget --tries=1 {}".format( url ) )
#
#         os.system( "rm -fr {}".format( i+1 ) )
#         os.system( "mkdir {}".format( i+1 ) )
#         os.system( "mv large.png?{} {}/large.png".format( random, i+1 ) )
#         print( "" )
