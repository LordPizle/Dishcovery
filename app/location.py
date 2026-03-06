import os
import requests
import math

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

def haversine_distance(lat1, lon1, lat2, lon2):
    
    R = 6371

    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(R * c, 1)

def get_photo_url(photo_reference, max_width=400):

    if not photo_reference:
        return None

    return (
        "https://maps.googleapis.com/maps/api/place/photo"
        f"?maxwidth={max_width}"
        f"&photoreference={photo_reference}"
        f"&key={GOOGLE_PLACES_API_KEY}"
    )

def get_place_photos(place_id, max_photos=5):

    if not GOOGLE_PLACES_API_KEY:
        return []

    details_url = "https://maps.googleapis.com/maps/api/place/details/json"

    params = {
        "place_id": place_id,
        "fields": "photos",
        "key": GOOGLE_PLACES_API_KEY,
    }

    resp = requests.get(details_url, params=params)
    data = resp.json()

    photos = data.get("result", {}).get("photos", [])
    photo_urls = []

    for photo in photos[:max_photos]:
        ref = photo.get("photo_reference")
        if ref:
            photo_urls.append(get_photo_url(ref))

    return photo_urls


def geocode_address_photon(address):
    """Geocode using Photon (OSM) - more reliable for worldwide addresses."""
    if not (address or "").strip():
        return None
    try:
        resp = requests.get(
            "https://photon.komoot.io/api/",
            params={"q": address.strip(), "limit": 1},
            timeout=10,
            headers={"User-Agent": "Dishcovery/1.0"},
        )
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return None
    features = data.get("features", [])
    if not features:
        return None
    coords = features[0].get("geometry", {}).get("coordinates", [])
    if len(coords) >= 2:
        return (float(coords[1]), float(coords[0]))  # lat, lng
    return None


def geocode_address(address):
    """Geocode address - uses Photon first for accurate worldwide results."""
    coords = geocode_address_photon(address)
    if coords:
        return coords
    if not GOOGLE_PLACES_API_KEY:
        return None
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address.strip(),
        "key": GOOGLE_PLACES_API_KEY,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
    except (requests.RequestException, ValueError):
        return None
    results = data.get("results", [])
    if not results:
        return None
    loc = results[0].get("geometry", {}).get("location", {})
    lat, lng = loc.get("lat"), loc.get("lng")
    if lat is not None and lng is not None:
        return (float(lat), float(lng))
    return None

def search_nearby_restaurants(lat, lng, keyword, radius_km=5, limit=10):

    if not GOOGLE_PLACES_API_KEY:
        return {"error": "Google Places API key not found. Set the environment variable."}

    radius_m = int(radius_km * 1000)
    limit = max(1, min(20, int(limit)))

    nearby_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    params = {
        "location": f"{lat},{lng}",
        "radius": radius_m,
        "type": "restaurant",
        "keyword": keyword,
        "key": GOOGLE_PLACES_API_KEY
    }

    try:
        response = requests.get(nearby_url, params=params, timeout=10)
        data = response.json()
    except (requests.RequestException, ValueError):
        return {"error": "Unable to fetch results. Please try again later."}

    status = data.get("status", "")
    if status != "OK" and status != "ZERO_RESULTS":
        return {"error": data.get("error_message", "Search failed. Please try again.")}

    restaurants = []

    for place in data.get("results", [])[:limit]:
        place_id = place.get("place_id")
        geo = place.get("geometry", {}).get("location", {})
        pl = geo.get("lat"), geo.get("lng")
        distance_km = haversine_distance(lat, lng, pl[0], pl[1]) if all(p is not None for p in pl) else None

        photo_urls = get_place_photos(place_id, max_photos=3)
        while len(photo_urls) < 1:
            photo_urls.append(None)
        photo_urls = photo_urls[:3]

        restaurant = {
            "name": place.get("name"),
            "address": place.get("vicinity") or place.get("formatted_address"),
            "place_id": place_id,
            "rating": place.get("rating"),
            "user_ratings_total": place.get("user_ratings_total"),
            "types": place.get("types"),
            "open_now": place.get("opening_hours", {}).get("open_now"),
            "distance_km": distance_km,
            "photo_urls": photo_urls,
        }
        restaurants.append(restaurant)

    return restaurants
