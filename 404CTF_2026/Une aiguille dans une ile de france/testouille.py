import json
import requests
import urllib3
import time
import os
from math import radians, sin, cos, sqrt, atan2

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

with open("pois.json", encoding="utf-8") as f:
    pois = json.load(f)

def dist_m(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = radians(lat2 - lat1); dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://overpass-turbo.eu/",
    "Origin": "https://overpass-turbo.eu",
}

SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]

def overpass(amenity, cache_file):
    # Si déjà en cache, on recharge
    if os.path.exists(cache_file):
        print(f"  (cache) {cache_file}")
        with open(cache_file, encoding="utf-8") as f:
            return json.load(f)

    query = f"""
    [out:json][timeout:180];
    (
      node["amenity"="{amenity}"](48.6,1.9,49.15,2.75);
      way["amenity"="{amenity}"](48.6,1.9,49.15,2.75);
    );
    out center;
    """
    for attempt in range(5):
        for url in SERVERS:
            try:
                r = requests.get(url, params={"data": query},
                                 headers=HEADERS, verify=False, timeout=300)
                if r.status_code == 200:
                    coords = []
                    for el in r.json()["elements"]:
                        if "lat" in el: coords.append((el["lat"], el["lon"]))
                        elif "center" in el: coords.append((el["center"]["lat"], el["center"]["lon"]))
                    with open(cache_file, "w", encoding="utf-8") as f:
                        json.dump(coords, f)
                    return coords
                else:
                    print(f"    {url} -> {r.status_code}, on réessaie...")
            except Exception as e:
                print(f"    {url} -> erreur {e}, on réessaie...")
            time.sleep(3)
        print(f"  Tentative {attempt+1}/5 échouée, pause 10s...")
        time.sleep(10)
    raise RuntimeError("Impossible de récupérer les données après plusieurs essais")

print("Téléchargement des fontaines...")
fountains = overpass("fountain", "cache_fountains.json")
print(f"  {len(fountains)} fontaines")

print("Téléchargement des cafés...")
cafes = overpass("cafe", "cache_cafes.json")
print(f"  {len(cafes)} cafés")

# Calcul des distances
results = []
for p in pois:
    lat, lon = p["lat"], p["lon"]
    d_font = min(dist_m(lat, lon, fl, fo) for fl, fo in fountains)
    d_cafe = min(dist_m(lat, lon, cl, co) for cl, co in cafes)
    results.append((p["id"], lat, lon, d_font, d_cafe))

results.sort(key=lambda x: x[3] + x[4])

print("\n=== TOP 15 POI les plus proches (fontaine + café) ===\n")
for pid, lat, lon, df, dc in results[:15]:
    osm = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=19/{lat}/{lon}"
    sv  = f"https://www.google.com/maps?q=&layer=c&cbll={lat},{lon}"
    print(f"{pid} | fontaine {df:6.1f}m | café {dc:6.1f}m")
    print(f"   OSM: {osm}")
    print(f"   SV:  {sv}\n")