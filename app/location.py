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


def search_nearby_restaurants(lat, lng, keyword):

    if not GOOGLE_PLACES_API_KEY:
        return {"error": "Google Places API key not found. Set the environment variable."}

    textsearch_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    params = {
        "query": f"{keyword} restaurant",
        "location": f"{lat},{lng}",
        "radius": 5000, 
        "key": GOOGLE_PLACES_API_KEY
    }

    response = requests.get(textsearch_url, params=params)
    data = response.json()

    restaurants = []

    for place in data.get("results", [])[:10]:

        place_id = place.get("place_id")

        photo_urls = get_place_photos(place_id, max_photos=5)
        while len(photo_urls) < 2:
            if photo_urls:
                photo_urls.append(photo_urls[-1])
            else:
                photo_urls.append(None)

        restaurant = {
            "name": place.get("name"),
            "address": place.get("formatted_address"),
            "rating": place.get("rating"),
            "types": place.get("types"),
            "open_now": place.get("opening_hours", {}).get("open_now"),
            "distance_km": None,
            "photo_urls": photo_urls,
        }

        restaurants.append(restaurant)

    return restaurants
