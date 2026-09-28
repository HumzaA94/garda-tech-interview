"""Factory for Agent model instances."""

import factory

from shift_scheduling.factories.qualification import QualificationFactory
from shift_scheduling.models import Agent


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
