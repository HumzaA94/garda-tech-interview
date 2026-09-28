"""Create a Flask application."""

from pathlib import Path

from flask import Flask

from shift_scheduling.config import Config
from shift_scheduling.errors import register_error_handlers
from shift_scheduling.routes import register_routes
from shift_scheduling.storage import DataStorage


def create_app(data_path: str | Path | None = None) -> Flask:
    """Create a Flask application."""
    config = Config(Path(data_path)) if data_path else Config.from_env()

    app = Flask(__name__)

    storage = DataStorage(config.data_path)
    storage.load()
    app.extensions["storage"] = storage

    register_routes(app)
    register_error_handlers(app)
    return app
