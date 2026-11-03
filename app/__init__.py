import os

from flask import Flask, render_template

_DEBUG_ON = {"1", "true", "yes", "on"}


def debug_enabled() -> bool:
    """Debug stays off unless FLASK_DEBUG is an explicit on-value."""
    return os.environ.get("FLASK_DEBUG", "").strip().lower() in _DEBUG_ON


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["DEBUG"] = debug_enabled()

    @app.get("/")
    def home():
        return render_template("home.html")

    return app
