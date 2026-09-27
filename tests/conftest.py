"""Shared pytest fixtures."""

import pytest
from flask import Flask
from flask.testing import FlaskClient

from shift_scheduling import create_app


@pytest.fixture
def app() -> Flask:
    """Create a Flask application configured for testing."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client for the Flask application."""
    return app.test_client()
