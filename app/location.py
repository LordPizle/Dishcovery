import os
import requests

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")


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
        return {"error": "Missing Google Places API key"}

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

        restaurants.append({
            "name": place.get("name"),
            "address": place.get("formatted_address"),
            "rating": place.get("rating"),
            "types": place.get("types"),
            "photo_url": photo_url,
        })

    return restaurants
