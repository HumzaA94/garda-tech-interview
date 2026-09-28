"""Tests for the shift service."""

from pathlib import Path

import pytest

from shift_scheduling.config import DEFAULT_DATA_PATH
from shift_scheduling.errors import NotFoundError
from shift_scheduling.services import shifts
from shift_scheduling.storage import DataStorage
from tests.factories import AgentFactory, ShiftFactory


@pytest.fixture
def storage() -> DataStorage:
    storage = DataStorage(Path(DEFAULT_DATA_PATH))
    storage.load()
    return storage


class TestGetShift:
    def test_returns_existing_shift(self, storage: DataStorage):
        assert shifts.get_shift(storage, "shf_1").id == "shf_1"

    def test_unknown_shift_raises_not_found(self, storage: DataStorage):
        with pytest.raises(NotFoundError):
            shifts.get_shift(storage, "shf_missing")


class TestIsQualified:
    def test_agent_with_every_required_code_qualifies(self):
        agent = AgentFactory(codes=["GUARD_LICENSE", "CROWD_CONTROL"])
        shift = ShiftFactory(required_qualifications=["GUARD_LICENSE", "CROWD_CONTROL"])
        assert shifts.is_qualified(agent, shift)

    def test_extra_qualifications_do_not_matter(self):
        agent = AgentFactory(codes=["GUARD_LICENSE", "FIRST_AID"])
        shift = ShiftFactory(required_qualifications=["GUARD_LICENSE"])
        assert shifts.is_qualified(agent, shift)

    def test_agent_missing_one_required_code_does_not_qualify(self):
        agent = AgentFactory(codes=["GUARD_LICENSE"])
        shift = ShiftFactory(required_qualifications=["GUARD_LICENSE", "CROWD_CONTROL"])
        assert not shifts.is_qualified(agent, shift)

    def test_shift_with_no_requirements_accepts_anyone(self):
        assert shifts.is_qualified(AgentFactory(), ShiftFactory())


class TestAvailableAgents:
    def test_shift_requiring_one_code(self, storage: DataStorage):
        result = shifts.available_agents(storage, "shf_1")
        assert [a.id for a in result] == ["agt_1", "agt_2", "agt_3"]

    def test_shift_requiring_two_codes(self, storage: DataStorage):
        result = shifts.available_agents(storage, "shf_2")
        assert [a.id for a in result] == ["agt_3"]

    def test_unknown_shift_raises_not_found(self, storage: DataStorage):
        with pytest.raises(NotFoundError):
            shifts.available_agents(storage, "shf_missing")
