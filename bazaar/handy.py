def apiCall(section, id, selections, key, sub=None):
    import requests

    try:
        r = requests.get("https://api.torn.com/{}/{}?selections={}&key={}".format(section, id, selections, key))
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
        print("[apiCall] API HTTPError {}".format(e))
        err = dict({"error": {"code": r.status_code, "error": "{} #blameched".format(r.reason)}})

    return dict({"apiError": "API error code {}: {}.".format(err["error"]["code"], err["error"]["error"])})


def getTopThreeUpdates(itemUpdates):
    # print(itemUpdates.discinct())
    # listItems = [a.item.tName for a in itemUpdates.all()]
    # distItems = list(set(listItems))
    # distOccur = [0]*len(distItems)
    # for i, item in enumerate(distItems):
    #     distOccur[i] = listItems.count(item)
    # return sorted(zip(distOccur, distItems), reverse=True)[:3]
    return False
