"""Create a Flask application."""

from flask import Flask

from shift_scheduling.routes import register_routes


def create_app() -> Flask:
    """Create a Flask application."""
    app = Flask(__name__)

    register_routes(app)

    return app
