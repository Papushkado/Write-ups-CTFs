import json, requests, urllib3, time
from math import radians, sin, cos, sqrt, atan2
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

with open("pois.json", encoding="utf-8") as f:
    pois = json.load(f)
with open("cache_cafes.json", encoding="utf-8") as f:
    cafes = json.load(f)

def dist_m(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = radians(lat2-lat1); dlon = radians(lon2-lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return R*2*atan2(sqrt(a), sqrt(1-a))

# Classer par proximité café
ranked = []
for p in pois:
    d = min(dist_m(p["lat"], p["lon"], cl, co) for cl, co in cafes)
    ranked.append((p["id"], p["lat"], p["lon"], d))
ranked.sort(key=lambda x: x[3])

# Géocodage des meilleurs, hors Paris
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.openstreetmap.org/",
}
def info(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&zoom=16"
    r = requests.get(url, headers=HEADERS, verify=False, timeout=30)
    a = r.json().get("address", {})
    ville = (a.get("city") or a.get("town") or a.get("village") or a.get("municipality") or "?")
    rue = a.get("road", "?")
    return ville, rue

print("\n=== TOP POI les plus proches d'un CAFÉ (hors Paris) ===\n")
count = 0
for pid, lat, lon, d in ranked[:80]:
    ville, rue = info(lat, lon)
    time.sleep(1.1)
    if ville.lower() == "paris":
        continue
    print(f"{pid} | café {d:5.1f}m | {ville:22s} | {rue}")
    count += 1
    if count >= 30:
        break