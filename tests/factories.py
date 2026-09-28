"""factory_boy factories for building model instances in tests."""

from datetime import UTC, date, datetime, timedelta

import factory

from shift_scheduling.models import Agent, Assignment, Qualification, Shift


class QualificationFactory(factory.Factory):
    class Meta:
        model = Qualification

    code = "GUARD_LICENSE"
    expires_on = date(2030, 1, 1)


class AgentFactory(factory.Factory):
    """Pass `codes=[...]` to give the agent one qualification per code."""

    class Meta:
        model = Agent

    class Params:
        codes = ()

    id = factory.Sequence(lambda n: f"agt_{n + 1}")
    name = factory.Faker("name")
    qualifications = factory.LazyAttribute(
        lambda o: [QualificationFactory(code=code) for code in o.codes]
    )


class ShiftFactory(factory.Factory):
    class Meta:
        model = Shift

    id = factory.Sequence(lambda n: f"shf_{n + 1}")
    site = factory.Faker("street_address")
    start = datetime(2026, 9, 15, 22, tzinfo=UTC)
    end = factory.LazyAttribute(lambda o: o.start + timedelta(hours=8))
    headcount = 1
    required_qualifications = factory.LazyFunction(list)


class AssignmentFactory(factory.Factory):
    class Meta:
        model = Assignment

    id = factory.Sequence(lambda n: f"asg_{n + 1}")
    shift_id = factory.Sequence(lambda n: f"shf_{n + 1}")
    agent_id = factory.Sequence(lambda n: f"agt_{n + 1}")
