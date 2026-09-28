"""Shift-related business logic: which agents are qualified for a shift."""

from __future__ import annotations

from shift_scheduling.errors import NotFoundError
from shift_scheduling.models import Agent, Shift
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


def is_qualified(agent: Agent, shift: Shift) -> bool:
    """
    Check if an agent is qualified for a shift.

    Args:
        agent: The agent to check.
        shift: The shift to check.

    Returns:
        True if the agent is qualified, False otherwise.
    """
    held = {qual.code for qual in agent.qualifications}
    return set(shift.required_qualifications) <= held


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
    return [agent for agent in storage.agents if is_qualified(agent, shift)]
