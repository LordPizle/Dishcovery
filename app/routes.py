import requests
from flask import Blueprint, render_template, request, jsonify
from .location import search_nearby_restaurants, geocode_address
from .chat import get_ai_response

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/find-food", methods=["GET", "POST"])
def find_food():
    keyword = ""
    results = None
    error = None
    distance = 5
    count = 10
    address = ""
    use_current = False

    if request.method == "POST":
        keyword = (request.form.get("keyword") or "").strip()
        use_current = request.form.get("use_current") == "1"
        address = (request.form.get("address") or "").strip()
        lat = request.form.get("lat")
        lng = request.form.get("lng")
        try:
            distance = max(1, min(20, int(request.form.get("distance", 5) or 5)))
        except (ValueError, TypeError):
            pass
        try:
            count = max(1, min(20, int(request.form.get("count", 10) or 10)))
        except (ValueError, TypeError):
            pass

        if not keyword:
            error = "Please enter what you're craving."
        elif use_current and lat and lng:
            results = search_nearby_restaurants(lat, lng, keyword, radius_km=distance, limit=count)
            if isinstance(results, dict) and "error" in results:
                error = results["error"]
                results = None
        elif lat and lng:
            results = search_nearby_restaurants(lat, lng, keyword, radius_km=distance, limit=count)
            if isinstance(results, dict) and "error" in results:
                error = results["error"]
                results = None
        elif address:
            coords = geocode_address(address)
            if coords:
                lat, lng = coords
                results = search_nearby_restaurants(lat, lng, keyword, radius_km=distance, limit=count)
                if isinstance(results, dict) and "error" in results:
                    error = results["error"]
                    results = None
            else:
                error = "Could not find that address. Please check and try again."
        else:
            error = "Please enter an address or use your current location."

    return render_template(
        "find_food.html",
        keyword=keyword,
        results=results,
        error=error,
        distance=distance,
        count=count,
        address=address,
        use_current=use_current,
    )


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/api/address-search")
def address_search():
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return jsonify([])
    params = {"q": q, "limit": 8}
    try:
        lat = request.args.get("lat", type=float)
        lon = request.args.get("lon", type=float)
        if lat is not None and lon is not None and -90 <= lat <= 90 and -180 <= lon <= 180:
            params["lat"] = lat
            params["lon"] = lon
    except (ValueError, TypeError):
        pass
    try:
        resp = requests.get(
            "https://photon.komoot.io/api/",
            params=params,
            timeout=10,
            headers={"User-Agent": "Dishcovery/1.0"},
        )
        resp.raise_for_status()
        data = resp.json()
        results = []
        for f in data.get("features", [])[:8]:
            props = f.get("properties", {})
            coords = f.get("geometry", {}).get("coordinates", [])
            if len(coords) < 2:
                continue
            osm_type = props.get("osm_value", "")
            name = props.get("name") or ""
            street = props.get("street") or ""
            housenumber = (props.get("housenumber") or props.get("streetnumber") or "").strip()
            postcode = props.get("postcode") or ""
            city = props.get("city") or props.get("locality") or ""
            state = props.get("state") or props.get("county") or ""
            country = props.get("country", "")
            if osm_type in ("city", "town", "village") or props.get("osm_key") == "place":
                display = ", ".join(p for p in [name, state, country] if p)
            else:
                street_part = (housenumber + " " + (street or name)).strip() if housenumber else (street or name)
                loc_part = ", ".join(p for p in [postcode, city, state] if p)
                display = ", ".join(p for p in [street_part, loc_part, country] if p)
            display = display.strip() or name or country or "Unknown"
            if display:
                results.append({"display": display, "lat": coords[1], "lng": coords[0]})
        return jsonify(results)
    except Exception:
        return jsonify([])


@main_bp.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()
    message = (data.get("message", "") or "").strip()
    if not message:
        return jsonify({"reply": "Please type a message!"})
    reply = get_ai_response(message)
    return jsonify({"reply": reply})


