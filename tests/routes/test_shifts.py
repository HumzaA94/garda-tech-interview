"""Tests for the shifts endpoints."""

from collections.abc import Callable
from http import HTTPStatus

from flask.testing import FlaskClient

from tests.factories import AgentFactory, ShiftFactory

MakeClient = Callable[..., FlaskClient]


class TestListAvailableAgents:
    def test_returns_every_agent_holding_the_required_code(
        self, make_client: MakeClient
    ):
        guard = AgentFactory(codes=["GUARD_LICENSE"])
        guard_with_first_aid = AgentFactory(codes=["GUARD_LICENSE", "FIRST_AID"])
        unqualified = AgentFactory(codes=["FIRST_AID"])
        shift = ShiftFactory(required_qualifications=["GUARD_LICENSE"])
        client = make_client(
            agents=[guard, guard_with_first_aid, unqualified], shifts=[shift]
        )

        response = client.get(f"/api/shifts/{shift.id}/available-agents")

        assert response.status_code == HTTPStatus.OK
        assert response.get_json() == [
            guard.to_summary(),
            guard_with_first_aid.to_summary(),
        ]

    def test_only_returns_agents_holding_every_required_code(
        self, make_client: MakeClient
    ):
        guard_only = AgentFactory(codes=["GUARD_LICENSE"])
        crowd_controller = AgentFactory(codes=["GUARD_LICENSE", "CROWD_CONTROL"])
        shift = ShiftFactory(required_qualifications=["GUARD_LICENSE", "CROWD_CONTROL"])
        client = make_client(agents=[guard_only, crowd_controller], shifts=[shift])

        response = client.get(f"/api/shifts/{shift.id}/available-agents")

        assert response.status_code == HTTPStatus.OK
        assert response.get_json() == [crowd_controller.to_summary()]

    def test_unknown_shift_returns_404(self, make_client: MakeClient):
        client = make_client(agents=[AgentFactory()], shifts=[ShiftFactory()])

        response = client.get("/api/shifts/shf_missing/available-agents")

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.get_json() == {"error": "shift not found"}

    def test_shift_with_no_requirements_returns_every_agent(
        self, make_client: MakeClient
    ):
        agents = [AgentFactory(codes=["GUARD_LICENSE"]), AgentFactory()]
        shift = ShiftFactory()
        client = make_client(agents=agents, shifts=[shift])

        response = client.get(f"/api/shifts/{shift.id}/available-agents")

        assert response.status_code == HTTPStatus.OK
        assert response.get_json() == [agent.to_summary() for agent in agents]

    def test_nobody_qualified_returns_empty_array(self, make_client: MakeClient):
        shift = ShiftFactory(required_qualifications=["CROWD_CONTROL"])
        client = make_client(
            agents=[AgentFactory(codes=["GUARD_LICENSE"]), AgentFactory()],
            shifts=[shift],
        )

        response = client.get(f"/api/shifts/{shift.id}/available-agents")

        assert response.status_code == HTTPStatus.OK
        assert response.get_json() == []
