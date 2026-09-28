"""Tests for the Assignment model."""

from shift_scheduling.models import Assignment

ASSIGNMENT_DATA = {"id": "asg_1", "shiftId": "shf_1", "agentId": "agt_1"}


class TestAssignment:
    def test_from_dict_maps_camel_case_keys(self):
        assignment = Assignment.from_dict(ASSIGNMENT_DATA)
        assert assignment.id == "asg_1"
        assert assignment.shift_id == "shf_1"
        assert assignment.agent_id == "agt_1"

    def test_round_trips_through_dict(self):
        assert Assignment.from_dict(ASSIGNMENT_DATA).to_dict() == ASSIGNMENT_DATA
