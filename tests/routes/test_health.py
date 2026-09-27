"""Tests for the health check endpoint."""

from http import HTTPStatus

from flask.testing import FlaskClient

from shift_scheduling.routes.health import HealthStatus


class TestHealthCheck:
    def test_health_check(self, client: FlaskClient):
        response = client.get("/health")
        assert response.status_code == HTTPStatus.OK
        assert response.get_json() == {"status": HealthStatus.OK}
