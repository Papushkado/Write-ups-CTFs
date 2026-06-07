import json, requests, urllib3, time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://overpass-turbo.eu/",
}

BBOX = "48.1,1.4,49.3,3.6"

def fetch(amenity_filter, cache_file, label):
    query = f"""
    [out:json][timeout:300];
    (
      node[{amenity_filter}]({BBOX});
      way[{amenity_filter}]({BBOX});
    );
    out center tags;
    """
    for attempt in range(5):
        try:
            r = requests.get("https://overpass-api.de/api/interpreter",
                             params={"data": query}, headers=HEADERS,
                             verify=False, timeout=400)
            if r.status_code == 200:
                items = []
                for el in r.json()["elements"]:
                    if "lat" in el:
                        lat, lon = el["lat"], el["lon"]
                    elif "center" in el:
                        lat, lon = el["center"]["lat"], el["center"]["lon"]
                    else:
                        continue
                    items.append({
                        "lat": lat, "lon": lon,
                        "tags": el.get("tags", {})   # ← on garde les tags !
                    })
                with open(cache_file, "w", encoding="utf-8") as fp:
                    json.dump(items, fp, ensure_ascii=False)
                print(f"  {label}: {len(items)} éléments")
                # Vérification : afficher 3 exemples avec leurs tags
                for ex in items[:3]:
                    print(f"     ex: amenity={ex['tags'].get('amenity')}, "
                          f"name={ex['tags'].get('name','?')}")
                return items
            print(f"  status {r.status_code}, retry...")
        except Exception as e:
            print(f"  erreur {e}, retry...")
        time.sleep(8)
    raise RuntimeError("échec")

print("Fontaines (amenity=fountain)...")
fetch('"amenity"="fountain"', "cache_fountains.json", "fontaines")

time.sleep(3)

print("Cafés (amenity=cafe)...")
fetch('"amenity"="cafe"', "cache_cafes.json", "cafés")

print("\n✅ Caches régénérés avec les tags pour vérification")