import os
from flask import Flask

def create_app():
    # Resolve `static/` from project root so templates and assets work consistently.
    static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    app = Flask(__name__, static_folder=static_path)
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dishcovery-secret-key")

    # Register all HTTP routes via blueprint.
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app
