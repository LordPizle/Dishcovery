from flask import Blueprint, render_template, request
from .location import search_nearby_restaurants

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    # Later we will plug real recommendations here
    return render_template("index.html")


@main_bp.route("/find-food", methods=["GET", "POST"])
def find_food():
    keyword = ""
    results = None
    error = None

    if request.method == "POST":
        keyword = request.form.get("keyword")
        lat = request.form.get("lat")
        lng = request.form.get("lng")

        if not (keyword and lat and lng):
            error = "Missing keyword or location."
        else:
            results = search_nearby_restaurants(lat, lng, keyword)

    return render_template("find_food.html", keyword=keyword, results=results, error=error)
