from debug import player_key
import requests

player_id = input("Enter player id: ")
key = player_key(player_id)
if not key:
    exit()

r = requests.get(f"https://api.torn.com/user/?selection=&key={key}").json()
r["key"] = key
for k, v in r.items():
    if isinstance(v, dict):
        for k2, v2 in v.items():
            print(f'              {k2:<12}: {v2}')
    else:
        print(f'{k:<12}: {v}')
