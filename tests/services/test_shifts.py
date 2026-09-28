"""Tests for the shift service."""

import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import pytest

from shift_scheduling.errors import ConflictError, NotFoundError, UnprocessableError
from shift_scheduling.factories import AgentFactory, AssignmentFactory, ShiftFactory
from shift_scheduling.models import QualificationCode
from shift_scheduling.services import shifts
from shift_scheduling.storage import DataStorage

MakeStorage = Callable[..., DataStorage]


def at(day: int, hour: int) -> datetime:
    return datetime(2026, 9, day, hour, tzinfo=UTC)


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


class TestIsFull:
    @pytest.mark.parametrize(
        ("headcount", "booked", "expected"),
        [(1, 0, False), (2, 1, False), (1, 1, True), (1, 2, True)],
        ids=["empty", "one-spot-left", "at-headcount", "over-headcount"],
    )
    def test_compares_bookings_to_headcount(
        self, make_storage: MakeStorage, headcount: int, booked: int, expected: bool
    ):
        shift = ShiftFactory(headcount=headcount)
        storage = make_storage(
            shifts=[shift],
            assignments=[AssignmentFactory(shift_id=shift.id) for _ in range(booked)],
        )
        assert shifts.is_full(storage, shift) is expected

    def test_only_counts_bookings_on_this_shift(self, make_storage: MakeStorage):
        shift, other = ShiftFactory(headcount=1), ShiftFactory()
        storage = make_storage(
            shifts=[shift, other], assignments=[AssignmentFactory(shift_id=other.id)]
        )
        assert not shifts.is_full(storage, shift)


class TestBookAgent:
    def test_sample_booking_marc_onto_shf_2(
        self, sample_storage: DataStorage, sample_data_path: Path
    ):
        assignment = shifts.book_agent(sample_storage, "shf_2", "agt_3")

        assert assignment.to_dict() == {
            "id": "asg_2",
            "shiftId": "shf_2",
            "agentId": "agt_3",
        }
        saved = json.loads(sample_data_path.read_text(encoding="utf-8"))
        assert saved["assignments"][-1] == assignment.to_dict()

    def test_booking_updates_availability_straight_away(
        self, sample_storage: DataStorage
    ):
        shifts.book_agent(sample_storage, "shf_2", "agt_3")

        assert shifts.available_agents(sample_storage, "shf_2") == []
        assert shifts.available_agents(sample_storage, "shf_1") == []

    @pytest.mark.parametrize(
        ("shift_id", "agent_id", "message"),
        [
            ("shf_missing", "agt_3", "shift not found"),
            ("shf_2", "agt_x", "agent not found"),
        ],
        ids=["unknown-shift", "unknown-agent"],
    )
    def test_unknown_shift_or_agent_raises_not_found(
        self, sample_storage: DataStorage, shift_id: str, agent_id: str, message: str
    ):
        with pytest.raises(NotFoundError, match=message):
            shifts.book_agent(sample_storage, shift_id, agent_id)

    def test_full_shift_raises_conflict(self, make_storage: MakeStorage):
        shift = ShiftFactory(headcount=1)
        booked, agent = AgentFactory(), AgentFactory()
        storage = make_storage(
            agents=[booked, agent],
            shifts=[shift],
            assignments=[AssignmentFactory(agent_id=booked.id, shift_id=shift.id)],
        )

        with pytest.raises(ConflictError):
            shifts.book_agent(storage, shift.id, agent.id)

    def test_unqualified_agent_raises_unprocessable(self, make_storage: MakeStorage):
        shift = ShiftFactory(required_qualifications=[QualificationCode.GUARD_LICENSE])
        agent = AgentFactory()
        storage = make_storage(agents=[agent], shifts=[shift])

        with pytest.raises(
            UnprocessableError, match="missing or expired qualification"
        ):
            shifts.book_agent(storage, shift.id, agent.id)

    def test_double_booked_agent_raises_unprocessable(self, make_storage: MakeStorage):
        overnight = ShiftFactory(start=at(15, 22), end=at(16, 6))
        late_evening = ShiftFactory(start=at(15, 23), end=at(16, 3), headcount=2)
        agent = AgentFactory()
        storage = make_storage(
            agents=[agent],
            shifts=[overnight, late_evening],
            assignments=[AssignmentFactory(agent_id=agent.id, shift_id=overnight.id)],
        )

        with pytest.raises(
            UnprocessableError, match="already booked on an overlapping shift"
        ):
            shifts.book_agent(storage, late_evening.id, agent.id)

    def test_full_is_reported_before_unavailable(self, make_storage: MakeStorage):
        shift = ShiftFactory(headcount=1)
        agent = AgentFactory()
        storage = make_storage(
            agents=[agent],
            shifts=[shift],
            assignments=[AssignmentFactory(agent_id=agent.id, shift_id=shift.id)],
        )

        with pytest.raises(ConflictError):
            shifts.book_agent(storage, shift.id, agent.id)

    def test_rejected_booking_changes_nothing(
        self, make_storage: MakeStorage, data_path: Path
    ):
        shift = ShiftFactory(required_qualifications=[QualificationCode.GUARD_LICENSE])
        agent = AgentFactory()
        storage = make_storage(agents=[agent], shifts=[shift])

        with pytest.raises(UnprocessableError):
            shifts.book_agent(storage, shift.id, agent.id)

        assert storage.assignments == []
        assert not data_path.exists()
