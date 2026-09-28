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

    def test_unknown_code_is_rejected(self):
        with pytest.raises(ValueError):
            Qualification.from_dict({"code": "UNKNOWN", "expiresOn": "2027-03-31"})
