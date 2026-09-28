"""Tests for the shifts endpoints."""

from collections.abc import Callable
from datetime import UTC, date, datetime
from http import HTTPStatus

from flask.testing import FlaskClient

from shift_scheduling.factories import (
    AgentFactory,
    AssignmentFactory,
    QualificationFactory,
    ShiftFactory,
)
from shift_scheduling.models import QualificationCode

MakeClient = Callable[..., FlaskClient]


class TestListAvailableAgents:
    def test_returns_every_agent_holding_the_required_code(
        self, make_client: MakeClient
    ):
        guard = AgentFactory(codes=[QualificationCode.GUARD_LICENSE])
        guard_with_first_aid = AgentFactory(
            codes=[QualificationCode.GUARD_LICENSE, QualificationCode.FIRST_AID]
        )
        unqualified = AgentFactory(codes=[QualificationCode.FIRST_AID])
        shift = ShiftFactory(required_qualifications=[QualificationCode.GUARD_LICENSE])
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
        guard_only = AgentFactory(codes=[QualificationCode.GUARD_LICENSE])
        crowd_controller = AgentFactory(
            codes=[QualificationCode.GUARD_LICENSE, QualificationCode.CROWD_CONTROL]
        )
        shift = ShiftFactory(
            required_qualifications=[
                QualificationCode.GUARD_LICENSE,
                QualificationCode.CROWD_CONTROL,
            ]
        )
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
        agents = [AgentFactory(codes=[QualificationCode.GUARD_LICENSE]), AgentFactory()]
        shift = ShiftFactory()
        client = make_client(agents=agents, shifts=[shift])

        response = client.get(f"/api/shifts/{shift.id}/available-agents")

        assert response.status_code == HTTPStatus.OK
        assert response.get_json() == [agent.to_summary() for agent in agents]

    def test_nobody_qualified_returns_empty_array(self, make_client: MakeClient):
        shift = ShiftFactory(required_qualifications=[QualificationCode.CROWD_CONTROL])
        client = make_client(
            agents=[
                AgentFactory(codes=[QualificationCode.GUARD_LICENSE]),
                AgentFactory(),
            ],
            shifts=[shift],
        )

        response = client.get(f"/api/shifts/{shift.id}/available-agents")

        assert response.status_code == HTTPStatus.OK
        assert response.get_json() == []

    def test_excludes_agents_whose_required_qualification_has_expired(
        self, make_client: MakeClient
    ):
        shift = ShiftFactory(
            start=datetime(2026, 9, 15, 22, tzinfo=UTC),
            required_qualifications=[QualificationCode.GUARD_LICENSE],
        )
        current = AgentFactory(codes=[QualificationCode.GUARD_LICENSE])
        expired = AgentFactory(
            qualifications=[
                QualificationFactory(
                    code=QualificationCode.GUARD_LICENSE, expires_on=date(2026, 8, 31)
                )
            ]
        )
        client = make_client(agents=[current, expired], shifts=[shift])

        response = client.get(f"/api/shifts/{shift.id}/available-agents")

        assert response.status_code == HTTPStatus.OK
        assert response.get_json() == [current.to_summary()]

    def test_excludes_agents_booked_on_an_overlapping_shift(
        self, make_client: MakeClient
    ):
        overnight = ShiftFactory(
            start=datetime(2026, 9, 15, 22, tzinfo=UTC),
            end=datetime(2026, 9, 16, 6, tzinfo=UTC),
        )
        late_evening = ShiftFactory(
            start=datetime(2026, 9, 15, 23, tzinfo=UTC),
            end=datetime(2026, 9, 16, 3, tzinfo=UTC),
        )
        free, booked = AgentFactory(), AgentFactory()
        client = make_client(
            agents=[free, booked],
            shifts=[overnight, late_evening],
            assignments=[AssignmentFactory(agent_id=booked.id, shift_id=overnight.id)],
        )

        for shift in (overnight, late_evening):
            response = client.get(f"/api/shifts/{shift.id}/available-agents")

            assert response.status_code == HTTPStatus.OK
            assert response.get_json() == [free.to_summary()]

    def test_includes_agents_booked_on_a_back_to_back_shift(
        self, make_client: MakeClient
    ):
        night = ShiftFactory(
            start=datetime(2026, 9, 15, 22, tzinfo=UTC),
            end=datetime(2026, 9, 16, 6, tzinfo=UTC),
        )
        morning = ShiftFactory(
            start=datetime(2026, 9, 16, 6, tzinfo=UTC),
            end=datetime(2026, 9, 16, 14, tzinfo=UTC),
        )
        agent = AgentFactory()
        client = make_client(
            agents=[agent],
            shifts=[night, morning],
            assignments=[AssignmentFactory(agent_id=agent.id, shift_id=night.id)],
        )

        response = client.get(f"/api/shifts/{morning.id}/available-agents")

        assert response.status_code == HTTPStatus.OK
        assert response.get_json() == [agent.to_summary()]
