from debug import player_key
import requests

payload = {
      "client": "My cool script",
      "version": "v0.1",
      "author_name": "Kivou",
      "author_id": 2000607,
      "country": "uni",
      "items": [
          {
              "id": 268,
              "quantity": 339,
              "cost": 1000
          },
          {
              "id": 266,
              "quantity": 1,
              "cost": 200
          },
      ]
}
