import json

with open("cache_fountains.json", encoding="utf-8") as f:
    fountains = json.load(f)

print(f"Nombre d'éléments dans cache_fountains.json : {len(fountains)}")
print("Format des 3 premiers éléments :")
for x in fountains[:3]:
    print("  ", x)