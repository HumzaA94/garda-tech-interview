"""Fixtures shared by the service tests."""

from collections.abc import Callable, Sequence
from pathlib import Path

import pytest

from shift_scheduling.config import DEFAULT_DATA_PATH
from shift_scheduling.models import Agent, Assignment, Shift
from shift_scheduling.storage import DataStorage


@pytest.fixture
def sample_storage() -> DataStorage:
    """Storage loaded from the repo's sample data.json."""
    storage = DataStorage(Path(DEFAULT_DATA_PATH))
    storage.load()
    return storage


@pytest.fixture
def make_storage() -> Callable[..., DataStorage]:
    """Build in-memory storage from model instances, without touching disk."""

    def _make_storage(
        agents: Sequence[Agent] = (),
        shifts: Sequence[Shift] = (),
        assignments: Sequence[Assignment] = (),
    ) -> DataStorage:
        storage = DataStorage(Path("unused.json"))
        storage.agents = list(agents)
        storage.shifts = list(shifts)
        storage.assignments = list(assignments)
        return storage

    return _make_storage
