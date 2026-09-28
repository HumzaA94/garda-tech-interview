"""Tests for QualificationFactory."""

from datetime import date

from shift_scheduling.factories import QualificationFactory
from shift_scheduling.models import Qualification, QualificationCode


class TestQualificationFactory:
    def test_builds_a_qualification(self):
        assert isinstance(QualificationFactory(), Qualification)

    def test_defaults_to_a_guard_license_that_has_not_expired(self):
        qualification = QualificationFactory()
        assert qualification.code == QualificationCode.GUARD_LICENSE
        assert qualification.expires_on > date(2026, 12, 31)

    def test_fields_can_be_overridden(self):
        qualification = QualificationFactory(
            code=QualificationCode.FIRST_AID, expires_on=date(2027, 1, 1)
        )
        assert qualification.code == QualificationCode.FIRST_AID
        assert qualification.expires_on == date(2027, 1, 1)

    def test_round_trips_through_dict(self):
        qualification = QualificationFactory()
        assert Qualification.from_dict(qualification.to_dict()) == qualification
