"""Tests for the Shift model."""

from datetime import UTC, datetime

import pytest

from shift_scheduling.factories import ShiftFactory
from shift_scheduling.models import QualificationCode, Shift

SHIFT_DATA = {
    "id": "shf_1",
    "site": "Warehouse 3, Dorval",
    "start": "2026-09-15T22:00:00Z",
    "end": "2026-09-16T06:00:00Z",
    "requiredQualifications": ["GUARD_LICENSE"],
    "headcount": 2,
}


class TestShift:
    def test_from_dict(self):
        shift = Shift.from_dict(SHIFT_DATA)
        assert shift.id == "shf_1"
        assert shift.site == "Warehouse 3, Dorval"
        assert shift.start == datetime(2026, 9, 15, 22, tzinfo=UTC)
        assert shift.end == datetime(2026, 9, 16, 6, tzinfo=UTC)
        assert shift.required_qualifications == [QualificationCode.GUARD_LICENSE]
        assert shift.headcount == 2

    def test_overnight_shift_ends_after_it_starts(self):
        shift = Shift.from_dict(SHIFT_DATA)
        assert shift.end > shift.start

    @pytest.mark.parametrize("required", [None, []])
    def test_null_or_empty_required_qualifications_becomes_empty_list(self, required):
        shift = Shift.from_dict({**SHIFT_DATA, "requiredQualifications": required})
        assert shift.required_qualifications == []

    def test_missing_required_qualifications_becomes_empty_list(self):
        data = {k: v for k, v in SHIFT_DATA.items() if k != "requiredQualifications"}
        assert Shift.from_dict(data).required_qualifications == []

    def test_round_trips_through_dict(self):
        assert Shift.from_dict(SHIFT_DATA).to_dict() == SHIFT_DATA


def at(day: int, hour: int) -> datetime:
    return datetime(2026, 9, day, hour, tzinfo=UTC)


class TestShiftOverlaps:
    @pytest.mark.parametrize(
        ("other_start", "other_end", "expected"),
        [
            (at(15, 23), at(16, 3), True),
            (at(15, 20), at(15, 23), True),
            (at(16, 5), at(16, 9), True),
            (at(15, 20), at(16, 8), True),
            (at(15, 14), at(15, 22), False),
            (at(16, 6), at(16, 14), False),
            (at(15, 10), at(15, 18), False),
            (at(16, 8), at(16, 12), False),
        ],
        ids=[
            "contained",
            "overlaps-start",
            "overlaps-end-after-midnight",
            "contains",
            "touches-start",
            "touches-end",
            "entirely-before",
            "entirely-after",
        ],
    )
    def test_overnight_shift(self, other_start, other_end, expected):
        overnight = ShiftFactory(start=at(15, 22), end=at(16, 6))
        other = ShiftFactory(start=other_start, end=other_end)
        assert overnight.overlaps(other) is expected
        assert other.overlaps(overnight) is expected

    def test_shift_overlaps_itself(self):
        shift = ShiftFactory()
        assert shift.overlaps(shift)
