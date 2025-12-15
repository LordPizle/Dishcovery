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


def search_nearby_restaurants(lat, lng, keyword):

    if not GOOGLE_PLACES_API_KEY:
        return {"error": "Google Places API key not found. Set the environment variable."}

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    params = {
        "query": f"{keyword} restaurant",
        "location": f"{lat},{lng}",
        "radius": 5000, 
        "key": GOOGLE_PLACES_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    restaurants = []

    for place in data.get("results", []):

        photo_ref = None
        if "photos" in place:
            photo_ref = place["photos"][0].get("photo_reference")

        photo_url = get_photo_url(photo_ref)
        opening_hours = place.get("opening_hours", {})
        open_now = opening_hours.get("open_now")

        place_lat = place["geometry"]["location"]["lat"]
        place_lng = place["geometry"]["location"]["lng"]

        distance_km = haversine_distance(lat, lng, place_lat, place_lng)

        restaurants.append({
            "name": place.get("name"),
            "address": place.get("formatted_address"),
            "rating": place.get("rating"),
            "types": place.get("types"),
            "photo_url": photo_url,
            "open_now": open_now,
            "distance_km": distance_km   
        })

    return restaurants
