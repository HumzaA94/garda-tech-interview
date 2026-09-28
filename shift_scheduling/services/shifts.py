"""Shift-related business logic: who is available for a shift, and booking onto it."""

from __future__ import annotations

from shift_scheduling.errors import ConflictError, NotFoundError, UnprocessableError
from shift_scheduling.models import Agent, Assignment, Shift
from shift_scheduling.services.agents import get_agent
from shift_scheduling.services.availability import (
    is_available,
    unavailability_reasons,
)
from shift_scheduling.storage import DataStorage


def get_shift(storage: DataStorage, shift_id: str) -> Shift:
    """
    Find a shift by its ID.

    Args:
        storage: The data storage to use.
        shift_id: The ID of the shift to find.

    Returns:
        The shift if found, otherwise raises a NotFoundError.
    """
    shift = storage.find_shift(shift_id)
    if shift is None:
        raise NotFoundError("shift not found")
    return shift


def available_agents(storage: DataStorage, shift_id: str) -> list[Agent]:
    """
    Get the list of agents available for a shift.

    Args:
        storage: The data storage to use.
        shift_id: The ID of the shift to get the available agents for.

    Returns:
        The list of agents available for the shift.
    """
    shift = get_shift(storage, shift_id)
    return [agent for agent in storage.agents if is_available(storage, agent, shift)]


def is_full(storage: DataStorage, shift: Shift) -> bool:
    """
    Check if a shift has reached its headcount.

    Args:
        storage: The data storage to use.
        shift: The shift to check.

    Returns:
        True if no more agents can be booked onto the shift, False otherwise.
    """
    return len(storage.assignments_for_shift(shift.id)) >= shift.headcount


def book_agent(storage: DataStorage, shift_id: str, agent_id: str) -> Assignment:
    """
    Book an agent onto a shift and persist the new assignment.

    Checks run in order: shift exists, agent exists, shift not full, agent
    available. Nothing is changed if any check fails.

    Args:
        storage: The data storage to use.
        shift_id: The ID of the shift to book onto.
        agent_id: The ID of the agent to book.

    Returns:
        The newly created assignment.

    Raises:
        NotFoundError: The shift or agent doesn't exist.
        ConflictError: The shift has already reached its headcount.
        UnprocessableError: The agent isn't available for the shift.
    """
    with storage.lock:
        shift = get_shift(storage, shift_id)
        agent = get_agent(storage, agent_id)

        if is_full(storage, shift):
            raise ConflictError("shift is full")

        reasons = unavailability_reasons(storage, agent, shift)
        if reasons:
            raise UnprocessableError(
                f"agent is not available for this shift: {'; '.join(reasons)}"
            )

        assignment = Assignment(
            id=storage.next_assignment_id(), shift_id=shift.id, agent_id=agent.id
        )
        storage.add_assignment(assignment)
        return assignment
