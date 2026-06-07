import json
from math import radians, sin, cos, sqrt, atan2

# ---------- Charger les données ----------
with open("pois.json", encoding="utf-8") as f:
    pois = json.load(f)
with open("cache_fountains.json", encoding="utf-8") as f:
    fountains = json.load(f)   # nouveau format : [{lat, lon, tags}, ...]
with open("cache_cafes.json", encoding="utf-8") as f:
    cafes = json.load(f)

# ---------- Helpers d'accès (nouveau format dict) ----------
def coords(items):
    """Renvoie une liste de (lat, lon) depuis le format {lat,lon,tags}."""
    return [(it["lat"], it["lon"]) for it in items]

fountain_pts = coords(fountains)
cafe_pts = coords(cafes)

def dist_m(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = radians(lat2-lat1); dlon = radians(lon2-lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return R*2*atan2(sqrt(a), sqrt(1-a))

# ---------- Calculer le compromis fontaine + café ----------
scored = []
for p in pois:
    lat, lon = p["lat"], p["lon"]
    d_font = min(dist_m(lat, lon, fl, fo) for fl, fo in fountain_pts)
    d_cafe = min(dist_m(lat, lon, cl, co) for cl, co in cafe_pts)
    score = d_font + d_cafe
    scored.append((p["id"], lat, lon, d_font, d_cafe, score))

scored.sort(key=lambda x: x[5])

TOP = scored[:25]
top_ids = {t[0] for t in TOP}

# ---------- Génération JS ----------
def js_pois_normaux():
    out = []
    for pid, lat, lon, df, dc, sc in scored:
        if pid in top_ids:
            continue
        sv = f"https://www.google.com/maps?q=&layer=c&cbll={lat},{lon}"
        popup = f"<b>{pid}</b><br>fontaine {df:.0f}m | café {dc:.0f}m<br><a href=\\'{sv}\\' target=_blank>StreetView</a>"
        out.append(
            f"L.circleMarker([{lat},{lon}],{{radius:6,color:'white',weight:1,"
            f"fillColor:'#e60000',fillOpacity:0.85}})"
            f".addTo(poiLayer).bindPopup('{popup}').bindTooltip('{pid}');"
        )
    return "\n".join(out)

def js_pois_top():
    out = []
    for rank, (pid, lat, lon, df, dc, sc) in enumerate(TOP, 1):
        sv = f"https://www.google.com/maps?q=&layer=c&cbll={lat},{lon}"
        popup = (f"<b>#{rank} - {pid}</b><br>"
                 f"🔵 fontaine {df:.0f}m<br>🟢 café {dc:.0f}m<br>"
                 f"compromis {sc:.0f}m<br>"
                 f"<a href=\\'{sv}\\' target=_blank>📍 StreetView</a>")
        out.append(
            f"L.circleMarker([{lat},{lon}],{{radius:11,color:'black',weight:2,"
            f"fillColor:'#ff9900',fillOpacity:1}})"
            f".addTo(topLayer).bindPopup('{popup}')"
            f".bindTooltip('#{rank} {pid}',{{permanent:true,direction:'top',className:'toplabel'}});"
        )
    return "\n".join(out)

def js_amenity(items, color, layer, radius):
    """Affiche fontaines/cafés avec leur nom en tooltip (depuis tags)."""
    out = []
    for it in items:
        lat, lon = it["lat"], it["lon"]
        name = it["tags"].get("name", "")
        amenity = it["tags"].get("amenity", "")
        tip = (name or amenity).replace("'", "")
        out.append(
            f"L.circleMarker([{lat},{lon}],{{radius:{radius},color:'{color}',"
            f"fillColor:'{color}',fillOpacity:0.6,weight:1}})"
            f".addTo({layer}).bindTooltip('{tip}');"
        )
    return "\n".join(out)

html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8"><title>Carte 404CTF</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  #map {{ height:100vh; }}
  body {{ margin:0; font-family:Arial, sans-serif; }}
  .legend {{ background:white; padding:12px 15px; line-height:1.8em;
     border-radius:8px; box-shadow:0 0 15px rgba(0,0,0,0.3); font-size:14px; }}
  .legend i {{ width:16px; height:16px; display:inline-block; margin-right:8px;
     border-radius:50%; vertical-align:middle; border:1px solid #555; }}
  .toplabel {{ background:#ff9900; border:1px solid black; font-weight:bold; font-size:11px; }}
</style>
</head><body>
<div id="map"></div>
<script>
var map = L.map('map').setView([48.85, 2.35], 11);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
  {{maxZoom:19, attribution:'© OpenStreetMap'}}).addTo(map);

var poiLayer     = L.layerGroup();
var topLayer     = L.layerGroup().addTo(map);
var fountainLayer= L.layerGroup().addTo(map);
var cafeLayer    = L.layerGroup();

{js_pois_normaux()}

{js_pois_top()}

{js_amenity(fountains, '#0066ff', 'fountainLayer', 5)}

{js_amenity(cafes, '#00aa00', 'cafeLayer', 4)}

L.control.layers(null, {{
  "⭐ TOP compromis ({len(TOP)})": topLayer,
  "🔴 Tous les POI": poiLayer,
  "🔵 Fontaines ({len(fountains)})": fountainLayer,
  "🟢 Cafés ({len(cafes)})": cafeLayer
}}, {{collapsed:false}}).addTo(map);

var legend = L.control({{position:'bottomright'}});
legend.onAdd = function(map) {{
  var div = L.DomUtil.create('div', 'legend');
  div.innerHTML =
    '<b>Légende</b><br>' +
    '<i style="background:#ff9900; width:18px; height:18px; border:2px solid black;"></i> <b>TOP compromis</b><br>' +
    '<i style="background:#e60000"></i> Autres POI<br>' +
    '<i style="background:#0066ff"></i> Fontaines<br>' +
    '<i style="background:#00aa00"></i> Cafés<br>' +
    '<hr style="margin:6px 0"><small>Survolez fontaines/cafés<br>pour voir leur nom</small>';
  return div;
}};
legend.addTo(map);
</script>
</body></html>"""

with open("carte.html", "w", encoding="utf-8") as f:
    f.write(html)

# ---------- Console : classement + vérif des tags ----------
print("✅ carte.html généré !\n")

print("=== Vérification : 5 premières 'fontaines' et leurs tags ===")
for it in fountains[:5]:
    print(f"  amenity={it['tags'].get('amenity')}, name={it['tags'].get('name','?')}")

print("\n=== TOP 25 compromis fontaine+café ===")
for rank, (pid, lat, lon, df, dc, sc) in enumerate(TOP, 1):
    print(f"#{rank:2d} {pid} | fontaine {df:6.1f}m | café {dc:6.1f}m | total {sc:6.1f}m")