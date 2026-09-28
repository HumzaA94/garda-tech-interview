"""Loads data.json into memory at startup."""

from __future__ import annotations

import json
from pathlib import Path

from flask import current_app

from shift_scheduling.models import Agent, Assignment, Shift


class DataStorage:
    """Loads data.json into memory at startup."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.agents: list[Agent] = []
        self.shifts: list[Shift] = []
        self.assignments: list[Assignment] = []

    def load(self) -> None:
        """Loads data.json into memory at startup."""
        with open(self.path, encoding="utf-8") as file:
            data = json.load(file)
        self.agents = [Agent.from_dict(agent) for agent in data["agents"]]
        self.shifts = [Shift.from_dict(shift) for shift in data["shifts"]]
        self.assignments = [
            Assignment.from_dict(assignment) for assignment in data["assignments"]
        ]

    def find_shift(self, shift_id: str) -> Shift | None:
        """Find a shift by its id."""
        return next((s for s in self.shifts if s.id == shift_id), None)


def get_storage() -> DataStorage:
    """Loads data.json into memory at startup."""
    return current_app.extensions["storage"]
