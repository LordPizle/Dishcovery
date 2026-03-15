import re
import time
import requests
from urllib.parse import urlencode
from flask import Blueprint, render_template, request, jsonify, session
from .location import search_nearby_restaurants, geocode_address
from .chat import get_ai_response
from .recommender import rerank_restaurants_by_query

main_bp = Blueprint("main", __name__)

# In-memory rate limit for /api/chat: 30 requests per 60 seconds per IP
_chat_rate_limit = {}
_RATE_LIMIT_WINDOW = 60
_RATE_LIMIT_MAX = 30


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
    min_rating = None
    open_now_only = False
    address = ""
    use_current = False
    sort = "distance"

    lat = None
    lng = None

    def _parse_filters(source):
        nonlocal distance, count, min_rating, open_now_only, sort
        try:
            distance = max(1, min(20, int(source.get("distance", distance) or distance)))
        except (ValueError, TypeError):
            pass
        try:
            count = max(1, min(20, int(source.get("count", count) or count)))
        except (ValueError, TypeError):
            pass
        mr = source.get("min_rating")
        if mr not in (None, "", "any"):
            try:
                min_rating = float(mr)
            except (ValueError, TypeError):
                min_rating = None
        ono = source.get("open_now_only")
        open_now_only = bool(str(ono) == "1" or ono is True)
        s = source.get("sort")
        if s in ("distance", "rating", "best_match"):
            sort = s

    if request.method == "POST":
        form = request.form
        keyword = (form.get("keyword") or "").strip()
        use_current = form.get("use_current") == "1"
        address = (form.get("address") or "").strip()
        lat = form.get("lat")
        lng = form.get("lng")
        _parse_filters(form)

        if not keyword:
            error = "Please enter what you're craving."
        elif use_current and lat and lng:
            results = search_nearby_restaurants(lat, lng, keyword, radius_km=distance, limit=count, min_rating=min_rating, open_now_only=open_now_only)
        elif lat and lng:
            results = search_nearby_restaurants(lat, lng, keyword, radius_km=distance, limit=count, min_rating=min_rating, open_now_only=open_now_only)
        elif address:
            coords = geocode_address(address)
            if coords:
                lat, lng = coords
                results = search_nearby_restaurants(lat, lng, keyword, radius_km=distance, limit=count, min_rating=min_rating, open_now_only=open_now_only)
            else:
                error = "Could not find that address. Please check and try again."
        else:
            error = "Please enter an address or use your current location."

        if isinstance(results, dict) and results is not None and "error" in results:
            error = results["error"]
            results = None

    else:
        args = request.args
        keyword = (args.get("keyword") or "").strip()
        address = (args.get("address") or "").strip()
        lat = args.get("lat")
        lng = args.get("lng")
        _parse_filters(args)

        if keyword and lat and lng:
            results = search_nearby_restaurants(lat, lng, keyword, radius_km=distance, limit=count, min_rating=min_rating, open_now_only=open_now_only)
            use_current = True
            if isinstance(results, dict) and "error" in results:
                error = results["error"]
                results = None

    # Apply sort when we have a list of results
    if results and not isinstance(results, dict):
        if sort == "rating":
            results = sorted(
                results,
                key=lambda r: (r.get("rating") is None, -(r.get("rating") or 0)),
            )
        elif sort == "distance":
            results = sorted(
                results,
                key=lambda r: (r.get("distance_km") is None, (r.get("distance_km") or 999)),
            )
        elif sort == "best_match":
            results = rerank_restaurants_by_query(results, keyword)

    filters_used = bool(min_rating is not None or open_now_only)
    no_results_from_filters = (
        not error
        and results is not None
        and len(results) == 0
        and filters_used
    )
    result_lat = float(lat) if lat is not None and results and not isinstance(results, dict) else None
    result_lng = float(lng) if lng is not None and results and not isinstance(results, dict) else None

    # Stores the last search in the session
    if results and not isinstance(results, dict) and lat is not None and lng is not None:
        try:
            session["last_search"] = {
                "lat": float(lat),
                "lng": float(lng),
                "keyword": keyword,
                "distance": distance,
            }
        except (TypeError, ValueError):
            session.pop("last_search", None)

    return render_template(
        "find_food.html",
        keyword=keyword,
        results=results,
        error=error,
        distance=distance,
        count=count,
        min_rating=min_rating,
        open_now_only=open_now_only,
        address=address,
        use_current=use_current,
        sort=sort,
        result_lat=result_lat,
        result_lng=result_lng,
        no_results_from_filters=no_results_from_filters,
        filters_used=filters_used,
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


def _chat_rate_limit_check():
    ip = request.remote_addr or "unknown"
    now = time.time()
    if ip not in _chat_rate_limit:
        _chat_rate_limit[ip] = []
    _chat_rate_limit[ip] = [t for t in _chat_rate_limit[ip] if now - t < _RATE_LIMIT_WINDOW]
    if len(_chat_rate_limit[ip]) >= _RATE_LIMIT_MAX:
        return False
    _chat_rate_limit[ip].append(now)
    return True


@main_bp.route("/api/chat", methods=["POST"])
def api_chat():
    if not _chat_rate_limit_check():
        return jsonify({"reply": "Too many messages. Please wait a minute and try again."}), 429
    data = request.get_json() or {}
    message = (data.get("message", "") or "").strip()
    if not message:
        return jsonify({"reply": "Please type a message!"})

    text = message.lower()
    lat = data.get("lat")
    lng = data.get("lng")

    def format_restaurant_reply(results, header_line, keyword, lat_val, lng_val):
        if not results:
            return (
                "I could not find any restaurants for that query. "
                "Try a broader craving or different cuisine in the Find Food page."
            )

        lines = [header_line]
        for idx, r in enumerate(results[:3], start=1):
            name = r.get("name") or "Unnamed place"
            rating = r.get("rating")
            total = r.get("user_ratings_total")
            dist = r.get("distance_km")
            addr = r.get("address")

            parts = [f"{idx}. {name}"]

            rating_bits = []
            if rating is not None:
                rating_bits.append(f"{rating}★")
            if total:
                rating_bits.append(f"{total} reviews")
            if rating_bits:
                parts.append(", ".join(rating_bits))

            if dist is not None:
                parts.append(f"{dist} km away")

            if addr:
                parts.append(addr)

            # One short paragraph per restaurant, followed by a blank line
            lines.append(" ".join(parts))
            lines.append("")

        qs = urlencode(
            {
                "keyword": keyword,
                "lat": lat_val,
                "lng": lng_val,
                "distance": 5,
            }
        )
        lines.append(
            f'View these on a map: <a href="/find-food?{qs}" target="_blank" rel="noopener">Open in Find Food</a>'
        )
        lines.append(
            "For more variety, you can also try a slightly broader search term on the Find Food page."
        )
        return "\n".join(lines)

    def search_and_reply(lat_val, lng_val, search_keyword, header_line):
        results = search_nearby_restaurants(lat_val, lng_val, search_keyword, radius_km=5, limit=5)
        if isinstance(results, dict) and "error" in results:
            return (
                results["error"]
                + " You can also try the Find Food page with your craving and location."
            )
        results = rerank_restaurants_by_query(results, search_keyword)
        return format_restaurant_reply(results, header_line, search_keyword, lat_val, lng_val)

    # If the user is searching for a city, search for restaurants in that city
    city_match = re.search(r"(.+?)\s+in\s+([a-zA-Z\s,]+)$", text)
    if city_match:
        food_part = city_match.group(1).strip()
        place_part = city_match.group(2).strip().strip(".")
        coords = geocode_address(place_part)
        if coords:
            lat_city, lng_city = coords
            keyword = food_part or message
            header = f"Here are a few places in {place_part}:"
            reply = search_and_reply(lat_city, lng_city, keyword, header)
            return jsonify({"reply": reply})

    if lat is None or lng is None:
        last = session.get("last_search") or {}
        lat = last.get("lat")
        lng = last.get("lng")

    if lat is not None and lng is not None:
        try:
            lat_f = float(lat)
            lng_f = float(lng)
        except (TypeError, ValueError):
            lat_f = None
            lng_f = None

        if lat_f is not None and lng_f is not None:
            wants_nearby = bool(
                ("near me" in text)
                or ("around me" in text)
                or ("nearby" in text)
                or ("close by" in text)
                or ("food near me" in text)
                or ("restaurants near me" in text)
                or ("where to eat" in text)
            )

            if wants_nearby:
                # Use the whole message as the keyword so queries like
                # "cheap sushi near me" still work reasonably well.
                reply = search_and_reply(lat_f, lng_f, message, "Here are a few places near you:")
                return jsonify({"reply": reply})

    # Fallback to the keyword-based AI helper
    reply = get_ai_response(message)
    return jsonify({"reply": reply})


