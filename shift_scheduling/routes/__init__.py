"""Routes for the application."""

from __future__ import annotations

from flask import Flask

from shift_scheduling.routes.health import bp as health_bp
from shift_scheduling.routes.shifts import bp as shifts_bp


def register_routes(app: Flask) -> None:
    """Register routes with the application."""
    app.register_blueprint(health_bp)
    app.register_blueprint(shifts_bp)
