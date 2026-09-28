"""Availability rules: whether an agent can work a shift, and if not, why."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from shift_scheduling.models import Agent, Shift
from shift_scheduling.storage import DataStorage


def is_qualified(agent: Agent, shift: Shift) -> bool:
    """
    Check if an agent holds every required qualification, unexpired at shift start.

    Args:
        agent: The agent to check.
        shift: The shift to check.

    Returns:
        True if the agent is qualified, False otherwise.
    """
    shift_day = shift.start.date()
    held = {qual.code for qual in agent.qualifications if qual.is_valid_on(shift_day)}
    return set(shift.required_qualifications) <= held


def is_double_booked(storage: DataStorage, agent: Agent, shift: Shift) -> bool:
    """
    Check if an agent is already assigned to a shift that overlaps this one.

    Being assigned to this same shift counts, since a shift overlaps itself.

    Args:
        storage: The data storage to use.
        agent: The agent to check.
        shift: The shift to check.

    Returns:
        True if the agent is already booked during this shift, False otherwise.
    """
    for assignment in storage.assignments:
        if assignment.agent_id != agent.id:
            continue
        booked = storage.find_shift(assignment.shift_id)
        if booked is not None and booked.overlaps(shift):
            return True
    return False


@dataclass(frozen=True)
class Rule:
    """A single availability check; `check` returns True when the agent passes."""

    reason: str
    check: Callable[[DataStorage, Agent, Shift], bool]

# Structure is not feasible for N+ rules. A better context manager is needed. For the assignment, it suffices.
RULES = [
    Rule(
        "missing or expired qualification",
        lambda storage, agent, shift: is_qualified(agent, shift),
    ),
    Rule(
        "already booked on an overlapping shift",
        lambda storage, agent, shift: not is_double_booked(storage, agent, shift),
    ),
]


def unavailability_reasons(
    storage: DataStorage, agent: Agent, shift: Shift
) -> list[str]:
    """
    List the reason for every rule the agent fails.

    Args:
        storage: The data storage to use.
        agent: The agent to check.
        shift: The shift to check.

    Returns:
        The reasons the agent can't work the shift; empty if they can.
    """
    return [rule.reason for rule in RULES if not rule.check(storage, agent, shift)]


def is_available(storage: DataStorage, agent: Agent, shift: Shift) -> bool:
    """
    Check if an agent passes every availability rule.

    Args:
        storage: The data storage to use.
        agent: The agent to check.
        shift: The shift to check.

    Returns:
        True if the agent is available, False otherwise.
    """
    return not unavailability_reasons(storage, agent, shift)
