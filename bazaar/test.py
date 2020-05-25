import requests
import json

url = "http://127.0.0.1:8000/bazaar/abroad/import/"
# url = "https://yata.alwaysdata.net/bazaar/abroad/import/"
payload = {
    "country": "uae",
    "client": "my cool app",
    "version": "0.5",
    "uid": "2000607",
    # "items": {
    #     "206": {
    #         "quantity": 1,
    #         "cost": 888,
    #     },
    #     272: {
    #         "quantity": 3,
    #         "cost": "654321",
    #     },
    # },
        "items": [
            {
                "id": "206",
                "quantity": 1,
                "cost": 888,
            },
            {
                "id": 272,
                "quantity": 3,
                "cost": "654321",
            },
        ]
}

x = requests.post(url, json=payload)
print(x)
response = json.loads(x.text)
print(response["message"])
for k, v in response["stocks"].items():
    print(k, v)
