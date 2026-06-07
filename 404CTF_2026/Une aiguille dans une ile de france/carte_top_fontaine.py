import json
from math import radians, sin, cos, sqrt, atan2

# ---------- Charger ----------
with open("pois.json", encoding="utf-8") as f:
    pois = json.load(f)
with open("cache_fountains.json", encoding="utf-8") as f:
    fountains = json.load(f)   # [{lat, lon, tags}, ...]
with open("cache_cafes.json", encoding="utf-8") as f:
    cafes = json.load(f)

cafe_pts = [(c["lat"], c["lon"]) for c in cafes]
poi_pts  = [(p["lat"], p["lon"]) for p in pois]

def dist_m(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = radians(lat2-lat1); dlon = radians(lon2-lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return R*2*atan2(sqrt(a), sqrt(1-a))

# ---------- Pour chaque fontaine : café le plus proche + POI le plus proche ----------
MAX_POI = 400   # ⬅️ filtre : on ne garde que les fontaines avec un POI à moins de 400 m

scored = []
for fobj in fountains:
    flat, flon = fobj["lat"], fobj["lon"]
    d_poi = min(dist_m(flat, flon, pl, po) for pl, po in poi_pts)
    if d_poi > MAX_POI:          # ⬅️ FILTRE POI < 400 m
        continue
    d_cafe = min(dist_m(flat, flon, cl, co) for cl, co in cafe_pts)
    name = fobj["tags"].get("name", "")
    scored.append((flat, flon, d_cafe, d_poi, name))

# Tri par proximité café
scored.sort(key=lambda x: x[2])

TOP = scored[:50]   # ⬅️ les 50 meilleures (parmi celles filtrées POI<400m)

print(f"Fontaines avec POI < {MAX_POI}m : {len(scored)} | on affiche le TOP {len(TOP)}\n")