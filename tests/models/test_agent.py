"""Tests for the Agent model."""

from shift_scheduling.models import Agent, Qualification, QualificationCode

AGENT_DATA = {
    "id": "agt_1",
    "name": "Jordan Reyes",
    "qualifications": [
        {"code": "GUARD_LICENSE", "expiresOn": "2027-03-31"},
        {"code": "FIRST_AID", "expiresOn": "2026-11-30"},
    ],
}


class TestAgent:
    def test_from_dict(self):
        agent = Agent.from_dict(AGENT_DATA)
        assert agent.id == "agt_1"
        assert agent.name == "Jordan Reyes"
        assert [q.code for q in agent.qualifications] == [
            QualificationCode.GUARD_LICENSE,
            QualificationCode.FIRST_AID,
        ]
        assert all(isinstance(q, Qualification) for q in agent.qualifications)

    def test_missing_qualifications_defaults_to_empty(self):
        agent = Agent.from_dict({"id": "agt_9", "name": "No Quals"})
        assert agent.qualifications == []

    def test_round_trips_through_dict(self):
        assert Agent.from_dict(AGENT_DATA).to_dict() == AGENT_DATA

    def test_summary_only_exposes_id_and_name(self):
        assert Agent.from_dict(AGENT_DATA).to_summary() == {
            "id": "agt_1",
            "name": "Jordan Reyes",
        }
