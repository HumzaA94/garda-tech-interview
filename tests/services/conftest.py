"""Fixtures shared by the service tests."""

from collections.abc import Callable, Sequence
from pathlib import Path

import pytest

from shift_scheduling.models import Agent, Assignment, Shift
from shift_scheduling.storage import DataStorage


@pytest.fixture
def sample_storage(sample_data_path: Path) -> DataStorage:
    """Storage loaded from a throwaway copy of the repo's sample data.json."""
    storage = DataStorage(sample_data_path)
    storage.load()
    return storage


@pytest.fixture
def make_storage(data_path: Path) -> Callable[..., DataStorage]:
    """Build storage from model instances; saves go to a temporary data file."""

    def _make_storage(
        agents: Sequence[Agent] = (),
        shifts: Sequence[Shift] = (),
        assignments: Sequence[Assignment] = (),
    ) -> DataStorage:
        storage = DataStorage(data_path)
        storage.agents = list(agents)
        storage.shifts = list(shifts)
        storage.assignments = list(assignments)
        return storage

    return _make_storage
