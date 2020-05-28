import requests
import json

# url = "http://127.0.0.1:8000/bazaar/abroad/import/"
url = "https://yata.alwaysdata.net/bazaar/abroad/import/"
payload = {
    "country": "uae",
    "client": "my cool app",
    "version": "0.5",
    "uid": "2000607",
    "items": {
        "206": {
            "quantity": 1,
            "cost": 888,
        },
        272: {
            "quantity": 3,
            "cost": "654321",
        },
    },
    # "items": [
    #     {
    #         "id": "206",
    #         "quantity": 1,
    #         "cost": 888,
    #     },
    #     {
    #         "id": 272,
    #         "quantity": 3,
    #         "cost": "654321",
    #     },
    # ]
}

payload = {
  "country": "mex",
  "client": "TEST Kivou",
  "version": "0.0",
  "author_name": "Pyrit",
  "author_id": 2111649,
  "items": {
    "11": {
      "quantity": 134,
      "cost": 75000
    },
    "26": {
      "quantity": 13,
      "cost": 15000
    },
    "31": {
      "quantity": 24,
      "cost": 950000
    },
    "107": {
      "quantity": 85,
      "cost": 500000
    },
    "111": {
      "quantity": 6,
      "cost": 8000
    },
    "159": {
      "quantity": 645,
      "cost": 25
    },
    "177": {
      "quantity": 12,
      "cost": 70000
    },
    "178": {
      "quantity": 24,
      "cost": 7500
    },
    "229": {
      "quantity": 300,
      "cost": 15000
    },
    "231": {
      "quantity": 27,
      "cost": 45000
    },
    "232": {
      "quantity": 27,
      "cost": 65000
    },
    "258": {
      "quantity": 775,
      "cost": 10000
    },
    "260": {
      "quantity": 9718,
      "cost": 300
    },
    "399": {
      "quantity": 7,
      "cost": 20000000
    },
    "409": {
      "quantity": 74,
      "cost": 20000
    }
  }
}

x = requests.post(url, json=payload)
# print(x)
response = json.loads(x.text)
print(response["message"])
for k, v in sorted(response["stocks"].items(), key=lambda x: x[0]):
    print(k, v["quantity"])
