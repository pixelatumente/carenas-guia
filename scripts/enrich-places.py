import json, time, urllib.request, os

# Read API key from file
with open('/home/hermes/.google_places_key') as f:
    API_KEY=f.read().strip()

# Load current data
with open('/home/hermes/projects/carenas-astro/src/data/carenas.json', encoding='utf-8') as f:
    data = json.load(f)

FIELD_MASK = (
    "places.id,places.displayName,places.formattedAddress,"
    "places.nationalPhoneNumber,places.websiteUri,places.rating,"
    "places.userRatingCount,places.regularOpeningHours,"
    "places.businessStatus,places.googleMapsUri"
)

def search_places(query, api_key):
    url = "https://places.googleapis.com/v1/places:searchText"
    payload = json.dumps({
        "textQuery": query,
        "maxResultCount": 1,
        "languageCode": "es"
    }).encode()
    
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Goog-Api-Key", api_key)
    req.add_header("X-Goog-FieldMask", FIELD_MASK)
    
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

def extract_place(place):
    if not place:
        return None
    return {
        "google_rating": place.get("rating"),
        "google_reviews": place.get("userRatingCount"),
        "google_address": place.get("formattedAddress"),
        "google_phone": place.get("nationalPhoneNumber"),
        "google_website": place.get("websiteUri"),
        "google_maps_url": place.get("googleMapsUri"),
        "google_business_status": place.get("businessStatus"),
        "google_hours_raw": place.get("regularOpeningHours", {}).get("weekdayDescriptions", []) if place.get("regularOpeningHours") else None,
        "google_place_id": place.get("id"),
    }

# Build query for each place
queries = []

# 1. Carenas (pueblo)
queries.append(("carenas-pueblo", "Carenas Zaragoza pueblo"))

# 2. Ermita de Santa Ana
queries.append(("ermita-santa-ana", "Ermita de Santa Ana Carenas Zaragoza"))

# 3. Iglesia de Nuestra Señora de la Asunción
queries.append(("iglesia-asuncion", "Iglesia de Nuestra Señora de la Asunción Carenas Zaragoza"))

# 4. Castillo de Somet
queries.append(("castillo-de-somet", "Castillo de Somet Carenas Zaragoza"))

# 5. Embalse de La Tranquera
queries.append(("embalse-tranquera", "Embalse de La Tranquera Zaragoza"))

# 6. Monasterio de Piedra
queries.append(("monasterio-piedra", "Monasterio de Piedra Nuévalos Zaragoza"))

# 7. Jaraba
queries.append(("jaraba", "Jaraba Zaragoza pueblo"))

# 8. Nuévalos
queries.append(("nuevalos", "Nuévalos Zaragoza pueblo"))

# 9. Ayuntamiento de Carenas
queries.append(("ayuntamiento-carenas", "Ayuntamiento de Carenas Zaragoza"))

# 10. Ruta Carenas - Embalse
queries.append(("ruta-carenas-tranquera", "Ruta senderismo Carenas Embalse de La Tranquera"))

# 11. Ruta Castillo Somet - Embalse
queries.append(("ruta-castillo-somet-tranquera", "Ruta senderismo Castillo de Somet Embalse de La Tranquera"))

# Map place IDs
place_map = {}
for p in data["places"]:
    place_map[p["id"]] = p

results = {}

for place_id, query in queries:
    print(f"\n--- {place_id} ---")
    print(f"Query: {query}")
    
    result = search_places(query, API_KEY)
    
    if "error" in result:
        print(f"  ERROR: {result['error']}")
        results[place_id] = {"error": result["error"]}
        continue
    
    places_raw = result.get("places", [])
    if not places_raw:
        # Try simpler query
        simple_query = query.split("Zaragoza")[0].strip() if "Zaragoza" in query else query
        print(f"  No results, retrying: {simple_query}")
        time.sleep(0.3)
        result = search_places(simple_query, API_KEY)
        places_raw = result.get("places", [])
    
    if not places_raw:
        print(f"  ✗ No Google Places match found")
        results[place_id] = {"error": "no_match"}
        time.sleep(0.3)
        continue
    
    place = places_raw[0]
    display = place.get("displayName", {}).get("text", "?")
    addr = place.get("formattedAddress", "?")
    rating = place.get("rating", "?")
    status = place.get("businessStatus", "?")
    print(f"  ✓ {display} | {addr} | rating: {rating} | status: {status}")
    
    enriched = extract_place(place)
    results[place_id] = enriched
    
    # Update the place in the JSON
    p = place_map.get(place_id)
    if p:
        if enriched["google_address"]:
            p["address"] = enriched["google_address"]
        if enriched["google_phone"]:
            p["phone"] = enriched["google_phone"]
        if enriched["google_website"] and not p.get("website"):
            p["website"] = enriched["google_website"]
        if enriched["google_rating"] is not None:
            p["rating"] = enriched["google_rating"]
        if enriched["google_reviews"] is not None:
            p["reviews"] = enriched["google_reviews"]
        if enriched["google_maps_url"]:
            p["mapsUrl"] = enriched["google_maps_url"]
        if enriched["google_hours_raw"]:
            p["hours"] = enriched["google_hours_raw"]
        p["verified"] = True
    
    time.sleep(0.3)

print("\n\n=== SUMMARY ===")
success = 0
fail = 0
for place_id in results:
    r = results[place_id]
    if "error" in r:
        print(f"  ✗ {place_id}: {r['error']}")
        fail += 1
    else:
        print(f"  ✓ {place_id}: rating={r.get('google_rating')}, reviews={r.get('google_reviews')}, phone={'✓' if r.get('google_phone') else '✗'}, web={'✓' if r.get('google_website') else '✗'}")
        success += 1

print(f"\nSuccess: {success}, Failed: {fail}")

# Save updated JSON
with open('/home/hermes/projects/carenas-astro/src/data/carenas.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n✅ JSON saved!")
