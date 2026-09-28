"""Health check endpoint."""

from __future__ import annotations

from enum import StrEnum
from http import HTTPStatus

from flask import Blueprint, Response, jsonify

bp = Blueprint("health", __name__)


class HealthStatus(StrEnum):
    OK = "ok"


@bp.get("/health")
def health() -> tuple[Response, HTTPStatus]:
    """Health check endpoint."""
    return jsonify({"status": HealthStatus.OK}), HTTPStatus.OK
