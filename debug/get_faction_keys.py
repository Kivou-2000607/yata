#!/usr/bin/env python

from debug import faction_keys
import json

faction_id = input("Enter faction id: ")
keys = faction_keys(faction_id)

json.dump(keys, open(f'faction-keys-{faction_id}.json', 'w'))
for k in keys:
    print(k)
