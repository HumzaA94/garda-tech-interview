"""API errors raised by services, and the handlers that render them as JSON."""

from __future__ import annotations

from flask import Flask, Response, jsonify
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    """Base class for API errors."""
    status_code = 500

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(ApiError):
    """Error raised when a resource is not found."""
    status_code = 404


def register_error_handlers(app: Flask) -> None:
    """Register error handlers for the Flask app."""
    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError) -> tuple[Response, int]:
        """Handle API errors."""
        return jsonify({"error": error.message}), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException) -> tuple[Response, int]:
        """Handle HTTP errors."""
        return jsonify({"error": error.description}), error.code
