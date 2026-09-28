"""Tests for ShiftFactory."""

from datetime import UTC, datetime, timedelta

from shift_scheduling.factories import ShiftFactory
from shift_scheduling.models import QualificationCode, Shift


class TestShiftFactory:
    def test_builds_a_shift(self):
        assert isinstance(ShiftFactory(), Shift)

    def test_each_shift_gets_a_unique_id(self):
        assert ShiftFactory().id != ShiftFactory().id

    def test_has_no_required_qualifications_by_default(self):
        assert ShiftFactory().required_qualifications == []

    def test_required_qualifications_are_not_shared_between_shifts(self):
        first = ShiftFactory()
        first.required_qualifications.append(QualificationCode.GUARD_LICENSE)
        assert ShiftFactory().required_qualifications == []

    def test_defaults_to_an_eight_hour_overnight_shift_in_utc(self):
        shift = ShiftFactory()
        assert shift.start.tzinfo == UTC
        assert shift.end - shift.start == timedelta(hours=8)
        assert shift.end.date() > shift.start.date()

    def test_end_follows_an_overridden_start(self):
        start = datetime(2026, 10, 1, 9, tzinfo=UTC)
        assert ShiftFactory(start=start).end == start + timedelta(hours=8)

    def test_round_trips_through_dict(self):
        shift = ShiftFactory(required_qualifications=[QualificationCode.GUARD_LICENSE])
        assert Shift.from_dict(shift.to_dict()) == shift
