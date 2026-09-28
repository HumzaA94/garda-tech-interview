"""Tests for the shifts endpoints."""

import json
from collections.abc import Callable
from datetime import UTC, date, datetime
from http import HTTPStatus
from pathlib import Path

import pytest
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


def read_assignments(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["assignments"]


class TestCreateAssignment:
    def test_booking_marc_onto_shf_2_succeeds_and_is_saved(
        self, client: FlaskClient, sample_data_path: Path
    ):
        response = client.post(
            "/api/shifts/shf_2/assignments", json={"agentId": "agt_3"}
        )

        assert response.status_code == HTTPStatus.CREATED
        assert response.get_json() == {
            "id": "asg_2",
            "shiftId": "shf_2",
            "agentId": "agt_3",
        }
        assert read_assignments(sample_data_path)[-1] == response.get_json()

    def test_booking_immediately_changes_available_agents(self, client: FlaskClient):
        assert client.get("/api/shifts/shf_2/available-agents").get_json() == [
            {"id": "agt_3", "name": "Marc Tremblay"}
        ]

        client.post("/api/shifts/shf_2/assignments", json={"agentId": "agt_3"})

        assert client.get("/api/shifts/shf_2/available-agents").get_json() == []
        assert client.get("/api/shifts/shf_1/available-agents").get_json() == []

    @pytest.mark.parametrize(
        ("shift_id", "agent_id", "error"),
        [
            ("shf_missing", "agt_3", "shift not found"),
            ("shf_2", "agt_missing", "agent not found"),
        ],
        ids=["unknown-shift", "unknown-agent"],
    )
    def test_unknown_shift_or_agent_returns_404(
        self, client: FlaskClient, shift_id: str, agent_id: str, error: str
    ):
        response = client.post(
            f"/api/shifts/{shift_id}/assignments", json={"agentId": agent_id}
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.get_json() == {"error": error}

    def test_unqualified_agent_returns_422(self, client: FlaskClient):
        response = client.post(
            "/api/shifts/shf_2/assignments", json={"agentId": "agt_2"}
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert "missing or expired qualification" in response.get_json()["error"]

    def test_double_booked_agent_returns_422(self, make_client: MakeClient):
        overnight = ShiftFactory(
            start=datetime(2026, 9, 15, 22, tzinfo=UTC),
            end=datetime(2026, 9, 16, 6, tzinfo=UTC),
        )
        late_evening = ShiftFactory(
            start=datetime(2026, 9, 15, 23, tzinfo=UTC),
            end=datetime(2026, 9, 16, 3, tzinfo=UTC),
        )
        agent = AgentFactory()
        client = make_client(
            agents=[agent],
            shifts=[overnight, late_evening],
            assignments=[AssignmentFactory(agent_id=agent.id, shift_id=overnight.id)],
        )

        response = client.post(
            f"/api/shifts/{late_evening.id}/assignments", json={"agentId": agent.id}
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert "already booked on an overlapping shift" in response.get_json()["error"]

    def test_full_shift_returns_409(self, client: FlaskClient):
        client.post("/api/shifts/shf_2/assignments", json={"agentId": "agt_3"})
        response = client.post(
            "/api/shifts/shf_2/assignments", json={"agentId": "agt_1"}
        )

        assert response.status_code == HTTPStatus.CONFLICT
        assert response.get_json() == {"error": "shift is full"}

    @pytest.mark.parametrize(
        ("agent_id", "expected_status"),
        [
            ("agt_2", HTTPStatus.UNPROCESSABLE_ENTITY),
            ("agt_1", HTTPStatus.UNPROCESSABLE_ENTITY),
            ("agt_missing", HTTPStatus.NOT_FOUND),
        ],
        ids=["unqualified", "double-booked", "unknown-agent"],
    )
    def test_rejected_booking_writes_nothing(
        self,
        client: FlaskClient,
        sample_data_path: Path,
        agent_id: str,
        expected_status: HTTPStatus,
    ):
        before = sample_data_path.read_bytes()

        response = client.post(
            "/api/shifts/shf_2/assignments", json={"agentId": agent_id}
        )

        assert response.status_code == expected_status
        assert sample_data_path.read_bytes() == before
        assert client.get("/api/shifts/shf_2/available-agents").get_json() == [
            {"id": "agt_3", "name": "Marc Tremblay"}
        ]

    @pytest.mark.parametrize(
        "kwargs",
        [
            {},
            {"data": "not json", "content_type": "application/json"},
            {"json": []},
            {"json": {}},
            {"json": {"agentId": ""}},
            {"json": {"agentId": 3}},
        ],
        ids=[
            "no-body",
            "invalid-json",
            "not-an-object",
            "missing-id",
            "empty-id",
            "non-string-id",
        ],
    )
    def test_malformed_body_returns_400(
        self, client: FlaskClient, sample_data_path: Path, kwargs: dict
    ):
        before = sample_data_path.read_bytes()

        response = client.post("/api/shifts/shf_2/assignments", **kwargs)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert "agentId" in response.get_json()["error"]
        assert sample_data_path.read_bytes() == before
