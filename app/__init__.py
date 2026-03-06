import os
from flask import Flask

def create_app():
    static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    app = Flask(__name__, static_folder=static_path)

    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app
