"""Dataclasses for the records in data.json, plus conversion to and from JSON."""

from shift_scheduling.models.agent import Agent
from shift_scheduling.models.assignment import Assignment
from shift_scheduling.models.qualification import Qualification
from shift_scheduling.models.shift import Shift

__all__ = ["Agent", "Assignment", "Qualification", "Shift"]
