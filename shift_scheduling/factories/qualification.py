"""Factory for Qualification model instances."""

from datetime import date

import factory

from shift_scheduling.models import Qualification, QualificationCode


class QualificationFactory(factory.Factory):
    class Meta:
        model = Qualification

    code = QualificationCode.GUARD_LICENSE
    expires_on = date(2030, 1, 1)
