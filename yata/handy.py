def timestampToDate(timestamp):
    import datetime
    import pytz
    return datetime.datetime.fromtimestamp(timestamp, tz=pytz.UTC)


def apiCall(section, id, selections, key, sub=None):
    import requests
    # DEBUG live chain
    # if selections == "chain" and section == "faction":
    #     print("[FUNCTION apiCall] DEBUG chain/faction")
    #     chain = dict({"chain": {"current": 3,
    #                             "timeout": 158,
    #                             "modifier": 0.75,
    #                             "cooldown": 18
    #                             }})
    #     return chain[sub] if sub is not None else chain

    # DEBUG API error
    # return dict({"apiError": "API error code 42: debug error."})

    try:
        url = "https://api.torn.com/{}/{}?selections={}&key={}".format(section, id, selections, key)
        print("[FUNCTION apiCall] {}".format(url.replace(key, "*" * len(key))))
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


def apiCallAttacks(factionId, beginTS, endTS, key, stopAfterNAttacks=False):
    import requests
    # WARNING no fallback for this method if api crashed. Will yeld server error.

    WINS = ["Arrested", "Attacked", "Looted", "None", "Special", "Hospitalized", "Mugged"]

    chain = dict({})

    beginTS = beginTS
    currentEndTS = endTS + 1  # add one to get last hit
    feedAttacks = True
    i = 1
    nWins = 0
    while feedAttacks:
        url = "https://api.torn.com/faction/{}?selections=attacks&key={}&from={}&to={}".format(factionId, key, beginTS, currentEndTS)
        print("[FUNCTION apiCallAttacks] call number {}: {}".format(i, url.replace(key, "*" * len(key))), end='... ')
        attacks = requests.get(url).json()["attacks"]
        if len(attacks):
            for k, v in attacks.items():
                if v["result"] in WINS and float(v["respect_gain"]) > 0.0:
                    nWins += 1
                chain[k] = v
                currentEndTS = min(v["timestamp_ended"], currentEndTS)
            if(len(attacks) < 1000):
                feedAttacks = False
            print("\tNumber of attacks: {}".format(len(attacks)))
            i += 1
        else:
            print("\tNumber of attacks: {}".format(len(attacks)))
            feedAttacks = False

        if stopAfterNAttacks is not False and nWins >= stopAfterNAttacks:
            print("[FUNCTION apiCallAttacks] stopped after {} attacks".format(stopAfterNAttacks))
            feedAttacks = False

    return chain


def toggleMessage(request, context, key):
    if key in request.session:
        context[key] = request.session[key]
        request.session[key] = False
    return context
