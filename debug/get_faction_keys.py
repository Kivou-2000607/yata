from debug import faction_keys

faction_id = input("Enter faction id: ")
keys = faction_keys(faction_id)

for k in keys:
    print(k)
