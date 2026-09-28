"""Shared pytest fixtures."""

import json
from collections.abc import Callable, Sequence
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient

from shift_scheduling import create_app
from shift_scheduling.models import Agent, Assignment, Shift


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


@pytest.fixture
def make_client(tmp_path: Path) -> Callable[..., FlaskClient]:
    """Create a test client backed by a custom data file instead of data.json."""

    def _make_client(
        agents: Sequence[Agent] = (),
        shifts: Sequence[Shift] = (),
        assignments: Sequence[Assignment] = (),
    ) -> FlaskClient:
        data = {
            "agents": [agent.to_dict() for agent in agents],
            "shifts": [shift.to_dict() for shift in shifts],
            "assignments": [assignment.to_dict() for assignment in assignments],
        }
        data_file = tmp_path / "data.json"
        data_file.write_text(json.dumps(data), encoding="utf-8")
        app = create_app(data_path=data_file)
        app.config["TESTING"] = True
        return app.test_client()

    return _make_client
