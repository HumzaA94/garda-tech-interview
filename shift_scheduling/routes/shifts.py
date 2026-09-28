"""Routes for the shifts API."""

from __future__ import annotations

from http import HTTPStatus

from flask import Blueprint, Response, jsonify

from shift_scheduling.services import shifts
from shift_scheduling.storage import get_storage

bp = Blueprint("shifts", __name__, url_prefix="/api/shifts")


@bp.get("/<shift_id>/available-agents")
def list_available_agents(shift_id: str) -> tuple[Response, HTTPStatus]:
    """List the available agents for a shift."""
    available = shifts.available_agents(get_storage(), shift_id)
    return jsonify([agent.to_summary() for agent in available]), HTTPStatus.OK
