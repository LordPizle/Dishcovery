from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    # Later we will plug real recommendations here
    return render_template("index.html")