"""Factory for Shift model instances."""

from datetime import UTC, datetime, timedelta

import factory

from shift_scheduling.models import Shift


class ShiftFactory(factory.Factory):
    class Meta:
        model = Shift

    id = factory.Sequence(lambda n: f"shf_{n + 1}")
    site = factory.Faker("street_address")
    start = datetime(2026, 9, 15, 22, tzinfo=UTC)
    end = factory.LazyAttribute(lambda o: o.start + timedelta(hours=8))
    headcount = 1
    required_qualifications = factory.LazyFunction(list)
