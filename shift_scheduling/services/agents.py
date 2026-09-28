"""Agent-related business logic."""

from __future__ import annotations

from shift_scheduling.errors import NotFoundError
from shift_scheduling.models import Agent
from shift_scheduling.storage import DataStorage


def get_agent(storage: DataStorage, agent_id: str) -> Agent:
    """
    Find an agent by its ID.

    Args:
        storage: The data storage to use.
        agent_id: The ID of the agent to find.

    Returns:
        The agent if found, otherwise raises a NotFoundError.
    """
    agent = storage.find_agent(agent_id)
    if agent is None:
        raise NotFoundError("agent not found")
    return agent
