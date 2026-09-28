"""Loads data.json into memory at startup and writes it back after each booking."""

from __future__ import annotations

import json
import os
import tempfile
import threading
from pathlib import Path

from flask import current_app

from shift_scheduling.models import Agent, Assignment, Shift

ASSIGNMENT_ID_PREFIX = "asg_"


class DataStorage:
    """Holds data.json in memory; bookings are written back to the same file."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.agents: list[Agent] = []
        self.shifts: list[Shift] = []
        self.assignments: list[Assignment] = []
        self.lock = threading.Lock()

    def load(self) -> None:
        """Loads data.json into memory at startup."""
        with open(self.path, encoding="utf-8") as file:
            data = json.load(file)
        self.agents = [Agent.from_dict(agent) for agent in data["agents"]]
        self.shifts = [Shift.from_dict(shift) for shift in data["shifts"]]
        self.assignments = [
            Assignment.from_dict(assignment) for assignment in data["assignments"]
        ]

    def save(self) -> None:
        """
        Write the in-memory data back to data.json.

        Writes to a temporary file first and swaps it in, so a failed write never
        leaves a half-written data.json behind.
        """
        data = {
            "agents": [agent.to_dict() for agent in self.agents],
            "shifts": [shift.to_dict() for shift in self.shifts],
            "assignments": [assignment.to_dict() for assignment in self.assignments],
        }
        fd, tmp_path = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)
                file.write("\n")
            os.replace(tmp_path, self.path)
        except BaseException:
            Path(tmp_path).unlink(missing_ok=True)
            raise

    def find_shift(self, shift_id: str) -> Shift | None:
        """Find a shift by its id."""
        return next((shift for shift in self.shifts if shift.id == shift_id), None)

    def find_agent(self, agent_id: str) -> Agent | None:
        """Find an agent by its id."""
        return next((agent for agent in self.agents if agent.id == agent_id), None)

    def assignments_for_shift(self, shift_id: str) -> list[Assignment]:
        """All assignments booked onto a shift."""
        return [
            assignment
            for assignment in self.assignments
            if assignment.shift_id == shift_id
        ]

    def next_assignment_id(self) -> str:
        """The next `asg_<n>` id, one higher than the largest existing number."""
        numbers = [
            int(suffix)
            for assignment in self.assignments
            if (suffix := assignment.id.removeprefix(ASSIGNMENT_ID_PREFIX)).isdigit()
        ]
        return f"{ASSIGNMENT_ID_PREFIX}{max(numbers, default=0) + 1}"

    def add_assignment(self, assignment: Assignment) -> None:
        """
        Add an assignment and persist it; on a failed write, memory is left unchanged.

        Args:
            assignment: The assignment to add.
        """
        self.assignments.append(assignment)
        try:
            self.save()
        except BaseException:
            self.assignments.pop()
            raise


def get_storage() -> DataStorage:
    """The DataStorage attached to the current Flask app."""
    return current_app.extensions["storage"]
