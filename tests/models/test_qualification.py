"""Tests for the Qualification model."""

from datetime import date

import pytest

from shift_scheduling.models import Qualification, QualificationCode


class TestQualification:
    def test_from_dict(self):
        qualification = Qualification.from_dict(
            {"code": "GUARD_LICENSE", "expiresOn": "2027-03-31"}
        )
        assert qualification.code == QualificationCode.GUARD_LICENSE
        assert qualification.expires_on == date(2027, 3, 31)

    def test_round_trips_through_dict(self):
        data = {"code": "FIRST_AID", "expiresOn": "2026-11-30"}
        assert Qualification.from_dict(data).to_dict() == data

    @pytest.mark.parametrize(
        ("day", "expected"),
        [
            (date(2026, 9, 14), True),
            (date(2026, 9, 15), True),
            (date(2026, 9, 16), False),
        ],
        ids=["before-expiry", "on-expiry-day", "after-expiry"],
    )
    def test_is_valid_on(self, day: date, expected: bool):
        qualification = Qualification(
            code=QualificationCode.GUARD_LICENSE, expires_on=date(2026, 9, 15)
        )
        assert qualification.is_valid_on(day) is expected

    def test_unknown_code_is_rejected(self):
        with pytest.raises(ValueError):
            Qualification.from_dict({"code": "UNKNOWN", "expiresOn": "2027-03-31"})
