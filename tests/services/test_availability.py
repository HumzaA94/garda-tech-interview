"""Tests for the availability rules."""

from collections.abc import Callable
from datetime import UTC, date, datetime

from shift_scheduling.factories import (
    AgentFactory,
    AssignmentFactory,
    QualificationFactory,
    ShiftFactory,
)
from shift_scheduling.models import Agent, Assignment, QualificationCode, Shift
from shift_scheduling.services.availability import (
    RULES,
    is_available,
    is_double_booked,
    is_qualified,
    unavailability_reasons,
)
from shift_scheduling.storage import DataStorage

MakeStorage = Callable[..., DataStorage]


def at(day: int, hour: int) -> datetime:
    return datetime(2026, 9, day, hour, tzinfo=UTC)


def book(agent: Agent, shift: Shift) -> Assignment:
    return AssignmentFactory(agent_id=agent.id, shift_id=shift.id)


def guard_license(expires_on: date) -> list:
    return [
        QualificationFactory(code=QualificationCode.GUARD_LICENSE, expires_on=expires_on)
    ]


class TestIsQualified:
    def test_agent_with_every_required_code_qualifies(self):
        agent = AgentFactory(
            codes=[QualificationCode.GUARD_LICENSE, QualificationCode.CROWD_CONTROL]
        )
        shift = ShiftFactory(
            required_qualifications=[
                QualificationCode.GUARD_LICENSE,
                QualificationCode.CROWD_CONTROL,
            ]
        )
        assert is_qualified(agent, shift)

    def test_extra_qualifications_do_not_matter(self):
        agent = AgentFactory(
            codes=[QualificationCode.GUARD_LICENSE, QualificationCode.FIRST_AID]
        )
        shift = ShiftFactory(required_qualifications=[QualificationCode.GUARD_LICENSE])
        assert is_qualified(agent, shift)

    def test_agent_missing_one_required_code_does_not_qualify(self):
        agent = AgentFactory(codes=[QualificationCode.GUARD_LICENSE])
        shift = ShiftFactory(
            required_qualifications=[
                QualificationCode.GUARD_LICENSE,
                QualificationCode.CROWD_CONTROL,
            ]
        )
        assert not is_qualified(agent, shift)

    def test_shift_with_no_requirements_accepts_anyone(self):
        assert is_qualified(AgentFactory(), ShiftFactory())

    def test_required_qualification_expired_before_shift_does_not_count(self):
        agent = AgentFactory(qualifications=guard_license(date(2026, 8, 31)))
        shift = ShiftFactory(required_qualifications=[QualificationCode.GUARD_LICENSE])
        assert not is_qualified(agent, shift)

    def test_required_qualification_expiring_on_shift_start_day_counts(self):
        agent = AgentFactory(qualifications=guard_license(date(2026, 9, 15)))
        shift = ShiftFactory(
            start=at(15, 22),
            required_qualifications=[QualificationCode.GUARD_LICENSE],
        )
        assert is_qualified(agent, shift)

    def test_expired_qualification_that_is_not_required_does_not_matter(self):
        agent = AgentFactory(
            qualifications=[
                QualificationFactory(code=QualificationCode.GUARD_LICENSE),
                QualificationFactory(
                    code=QualificationCode.FIRST_AID, expires_on=date(2020, 1, 1)
                ),
            ]
        )
        shift = ShiftFactory(required_qualifications=[QualificationCode.GUARD_LICENSE])
        assert is_qualified(agent, shift)


class TestIsDoubleBooked:
    def test_agent_with_no_assignments_is_free(self, make_storage: MakeStorage):
        agent, shift = AgentFactory(), ShiftFactory()
        storage = make_storage(agents=[agent], shifts=[shift])
        assert not is_double_booked(storage, agent, shift)

    def test_agent_already_on_this_shift_is_booked(self, make_storage: MakeStorage):
        agent, shift = AgentFactory(), ShiftFactory()
        storage = make_storage(
            agents=[agent], shifts=[shift], assignments=[book(agent, shift)]
        )
        assert is_double_booked(storage, agent, shift)

    def test_agent_on_an_overlapping_shift_is_booked(self, make_storage: MakeStorage):
        agent = AgentFactory()
        overnight = ShiftFactory(start=at(15, 22), end=at(16, 6))
        late_evening = ShiftFactory(start=at(15, 23), end=at(16, 3))
        storage = make_storage(
            agents=[agent],
            shifts=[overnight, late_evening],
            assignments=[book(agent, overnight)],
        )
        assert is_double_booked(storage, agent, late_evening)

    def test_agent_on_a_back_to_back_shift_is_free(self, make_storage: MakeStorage):
        agent = AgentFactory()
        night = ShiftFactory(start=at(15, 22), end=at(16, 6))
        morning = ShiftFactory(start=at(16, 6), end=at(16, 14))
        storage = make_storage(
            agents=[agent], shifts=[night, morning], assignments=[book(agent, night)]
        )
        assert not is_double_booked(storage, agent, morning)

    def test_another_agents_booking_does_not_count(self, make_storage: MakeStorage):
        agent, colleague, shift = AgentFactory(), AgentFactory(), ShiftFactory()
        storage = make_storage(
            agents=[agent, colleague],
            shifts=[shift],
            assignments=[book(colleague, shift)],
        )
        assert not is_double_booked(storage, agent, shift)

    def test_assignment_to_an_unknown_shift_is_ignored(
        self, make_storage: MakeStorage
    ):
        agent, shift = AgentFactory(), ShiftFactory()
        storage = make_storage(
            agents=[agent],
            shifts=[shift],
            assignments=[AssignmentFactory(agent_id=agent.id, shift_id="shf_gone")],
        )
        assert not is_double_booked(storage, agent, shift)


class TestUnavailabilityReasons:
    def test_available_agent_has_no_reasons(self, make_storage: MakeStorage):
        agent = AgentFactory(codes=[QualificationCode.GUARD_LICENSE])
        shift = ShiftFactory(required_qualifications=[QualificationCode.GUARD_LICENSE])
        storage = make_storage(agents=[agent], shifts=[shift])
        assert unavailability_reasons(storage, agent, shift) == []

    def test_unqualified_agent(self, make_storage: MakeStorage):
        agent = AgentFactory()
        shift = ShiftFactory(required_qualifications=[QualificationCode.GUARD_LICENSE])
        storage = make_storage(agents=[agent], shifts=[shift])
        assert unavailability_reasons(storage, agent, shift) == [
            "missing or expired qualification"
        ]

    def test_double_booked_agent(self, make_storage: MakeStorage):
        agent, shift = AgentFactory(), ShiftFactory()
        storage = make_storage(
            agents=[agent], shifts=[shift], assignments=[book(agent, shift)]
        )
        assert unavailability_reasons(storage, agent, shift) == [
            "already booked on an overlapping shift"
        ]

    def test_lists_every_failed_rule_in_order(self, make_storage: MakeStorage):
        agent = AgentFactory(qualifications=guard_license(date(2026, 8, 31)))
        shift = ShiftFactory(required_qualifications=[QualificationCode.GUARD_LICENSE])
        storage = make_storage(
            agents=[agent], shifts=[shift], assignments=[book(agent, shift)]
        )
        assert unavailability_reasons(storage, agent, shift) == [
            rule.reason for rule in RULES
        ]


class TestIsAvailable:
    def test_agent_passing_every_rule_is_available(self, make_storage: MakeStorage):
        agent = AgentFactory(codes=[QualificationCode.GUARD_LICENSE])
        shift = ShiftFactory(required_qualifications=[QualificationCode.GUARD_LICENSE])
        storage = make_storage(agents=[agent], shifts=[shift])
        assert is_available(storage, agent, shift)

    def test_agent_failing_any_rule_is_not_available(self, make_storage: MakeStorage):
        agent, shift = AgentFactory(), ShiftFactory()
        storage = make_storage(
            agents=[agent], shifts=[shift], assignments=[book(agent, shift)]
        )
        assert not is_available(storage, agent, shift)
