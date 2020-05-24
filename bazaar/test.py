import requests

url = "http://127.0.0.1:8000/bazaar/abroad/import/"
payload = {
    "country": "uae",
    "client": "my cool app",
    "uid": "2000607",
    # "items": {
    #     "206": {
    #         "quantity": 1,
    #         "cost": 888,
    #     },
    #     "272": {
    #         "quantity": 3,
    #         "cost": "654321",
    #     },
    # },
        "items": [
            {
                "id": 206,
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
print(x.text)
