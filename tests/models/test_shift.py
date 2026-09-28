"""Tests for the Shift model."""

from datetime import UTC, datetime

import pytest

from shift_scheduling.models import Shift

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
        assert shift.required_qualifications == ["GUARD_LICENSE"]
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
