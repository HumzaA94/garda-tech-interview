"""Routes for the shifts API."""

from __future__ import annotations

from http import HTTPStatus

from flask import Blueprint, Response, jsonify, request

from shift_scheduling.errors import BadRequestError
from shift_scheduling.services import shifts
from shift_scheduling.storage import get_storage

bp = Blueprint("shifts", __name__, url_prefix="/api/shifts")


@bp.get("/<shift_id>/available-agents")
def list_available_agents(shift_id: str) -> tuple[Response, HTTPStatus]:
    """List the available agents for a shift."""
    available = shifts.available_agents(get_storage(), shift_id)
    return jsonify([agent.to_summary() for agent in available]), HTTPStatus.OK


@bp.post("/<shift_id>/assignments")
def create_assignment(shift_id: str) -> tuple[Response, HTTPStatus]:
    """Book an agent onto a shift."""
    body = request.get_json(silent=True)
    agent_id = body.get("agentId") if isinstance(body, dict) else None
    if not isinstance(agent_id, str) or not agent_id:
        raise BadRequestError("request body must be JSON with a string 'agentId'")

    assignment = shifts.book_agent(get_storage(), shift_id, agent_id)
    return jsonify(assignment.to_dict()), HTTPStatus.CREATED
