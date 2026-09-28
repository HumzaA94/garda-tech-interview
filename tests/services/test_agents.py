"""Tests for the agent service."""

import pytest

from shift_scheduling.errors import NotFoundError
from shift_scheduling.services import agents
from shift_scheduling.storage import DataStorage


class TestGetAgent:
    def test_returns_existing_agent(self, sample_storage: DataStorage):
        assert agents.get_agent(sample_storage, "agt_3").name == "Marc Tremblay"

    def test_unknown_agent_raises_not_found(self, sample_storage: DataStorage):
        with pytest.raises(NotFoundError):
            agents.get_agent(sample_storage, "agt_missing")
