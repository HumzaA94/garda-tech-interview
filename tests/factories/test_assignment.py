"""Tests for AssignmentFactory."""

from shift_scheduling.factories import AgentFactory, AssignmentFactory, ShiftFactory
from shift_scheduling.models import Assignment


class TestAssignmentFactory:
    def test_builds_an_assignment(self):
        assert isinstance(AssignmentFactory(), Assignment)

    def test_each_assignment_gets_a_unique_id(self):
        assert AssignmentFactory().id != AssignmentFactory().id

    def test_can_link_a_real_shift_and_agent(self):
        shift, agent = ShiftFactory(), AgentFactory()
        assignment = AssignmentFactory(shift_id=shift.id, agent_id=agent.id)
        assert assignment.shift_id == shift.id
        assert assignment.agent_id == agent.id

    def test_round_trips_through_dict(self):
        assignment = AssignmentFactory()
        assert Assignment.from_dict(assignment.to_dict()) == assignment
