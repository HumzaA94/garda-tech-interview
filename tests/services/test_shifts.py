"""Tests for the shift service."""

from collections.abc import Callable

import pytest

from shift_scheduling.errors import NotFoundError
from shift_scheduling.factories import AgentFactory, AssignmentFactory, ShiftFactory
from shift_scheduling.models import QualificationCode
from shift_scheduling.services import shifts
from shift_scheduling.storage import DataStorage

MakeStorage = Callable[..., DataStorage]


class TestGetShift:
    def test_returns_existing_shift(self, sample_storage: DataStorage):
        assert shifts.get_shift(sample_storage, "shf_1").id == "shf_1"

    def test_unknown_shift_raises_not_found(self, sample_storage: DataStorage):
        with pytest.raises(NotFoundError):
            shifts.get_shift(sample_storage, "shf_missing")


class TestAvailableAgents:
    def test_sample_shf_1_returns_only_marc(self, sample_storage: DataStorage):
        result = shifts.available_agents(sample_storage, "shf_1")
        assert [a.id for a in result] == ["agt_3"]

    def test_sample_shf_2_returns_only_marc(self, sample_storage: DataStorage):
        result = shifts.available_agents(sample_storage, "shf_2")
        assert [a.id for a in result] == ["agt_3"]

    def test_excludes_unqualified_and_double_booked_agents(
        self, make_storage: MakeStorage
    ):
        shift = ShiftFactory(required_qualifications=[QualificationCode.GUARD_LICENSE])
        free = AgentFactory(codes=[QualificationCode.GUARD_LICENSE])
        booked = AgentFactory(codes=[QualificationCode.GUARD_LICENSE])
        unqualified = AgentFactory()
        storage = make_storage(
            agents=[free, booked, unqualified],
            shifts=[shift],
            assignments=[AssignmentFactory(agent_id=booked.id, shift_id=shift.id)],
        )
        assert shifts.available_agents(storage, shift.id) == [free]

    def test_unknown_shift_raises_not_found(self, sample_storage: DataStorage):
        with pytest.raises(NotFoundError):
            shifts.available_agents(sample_storage, "shf_missing")
