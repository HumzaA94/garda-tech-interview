"""Tests for AgentFactory."""

from shift_scheduling.factories import AgentFactory, QualificationFactory
from shift_scheduling.models import Agent, Qualification, QualificationCode


class TestAgentFactory:
    def test_builds_an_agent(self):
        assert isinstance(AgentFactory(), Agent)

    def test_each_agent_gets_a_unique_id(self):
        assert AgentFactory().id != AgentFactory().id

    def test_generates_a_name(self):
        name = AgentFactory().name
        assert isinstance(name, str)
        assert name

    def test_has_no_qualifications_by_default(self):
        assert AgentFactory().qualifications == []

    def test_codes_become_one_qualification_each_in_order(self):
        agent = AgentFactory(
            codes=[QualificationCode.GUARD_LICENSE, QualificationCode.CROWD_CONTROL]
        )
        assert all(isinstance(q, Qualification) for q in agent.qualifications)
        assert [q.code for q in agent.qualifications] == [
            QualificationCode.GUARD_LICENSE,
            QualificationCode.CROWD_CONTROL,
        ]

    def test_qualifications_can_be_passed_directly(self):
        qualification = QualificationFactory(code=QualificationCode.FIRST_AID)
        agent = AgentFactory(qualifications=[qualification])
        assert agent.qualifications == [qualification]

    def test_codes_is_not_a_field_on_the_model(self):
        assert not hasattr(
            AgentFactory(codes=[QualificationCode.GUARD_LICENSE]), "codes"
        )

    def test_round_trips_through_dict(self):
        agent = AgentFactory(codes=[QualificationCode.GUARD_LICENSE])
        assert Agent.from_dict(agent.to_dict()) == agent
