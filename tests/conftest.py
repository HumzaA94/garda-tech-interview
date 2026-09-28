"""Shared pytest fixtures."""

import json
import shutil
from collections.abc import Callable, Sequence
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient

from shift_scheduling import create_app
from shift_scheduling.config import DEFAULT_DATA_PATH
from shift_scheduling.models import Agent, Assignment, Shift


@pytest.fixture
def sample_data_path(tmp_path: Path) -> Path:
    """A throwaway copy of the repo's data.json, so tests never modify the real one."""
    path = tmp_path / "sample-data.json"
    shutil.copy(DEFAULT_DATA_PATH, path)
    return path


@pytest.fixture
def app(sample_data_path: Path) -> Flask:
    """Create a Flask application configured for testing, on the sample data."""
    app = create_app(data_path=sample_data_path)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def data_path(tmp_path: Path) -> Path:
    """Where `make_client` and `make_storage` write their custom data file."""
    return tmp_path / "data.json"


def write_data(
    path: Path,
    agents: Sequence[Agent] = (),
    shifts: Sequence[Shift] = (),
    assignments: Sequence[Assignment] = (),
) -> None:
    data = {
        "agents": [agent.to_dict() for agent in agents],
        "shifts": [shift.to_dict() for shift in shifts],
        "assignments": [assignment.to_dict() for assignment in assignments],
    }
    path.write_text(json.dumps(data), encoding="utf-8")


@pytest.fixture
def make_client(data_path: Path) -> Callable[..., FlaskClient]:
    """Create a test client backed by a custom data file instead of data.json."""

    def _make_client(
        agents: Sequence[Agent] = (),
        shifts: Sequence[Shift] = (),
        assignments: Sequence[Assignment] = (),
    ) -> FlaskClient:
        write_data(data_path, agents, shifts, assignments)
        app = create_app(data_path=data_path)
        app.config["TESTING"] = True
        return app.test_client()

    return _make_client
