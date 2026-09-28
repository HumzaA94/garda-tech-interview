"""Factory for Assignment model instances."""

import factory

from shift_scheduling.models import Assignment


class AssignmentFactory(factory.Factory):
    class Meta:
        model = Assignment

    id = factory.Sequence(lambda n: f"asg_{n + 1}")
    shift_id = factory.Sequence(lambda n: f"shf_{n + 1}")
    agent_id = factory.Sequence(lambda n: f"agt_{n + 1}")
