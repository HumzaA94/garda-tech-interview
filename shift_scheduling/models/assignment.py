"""Dataclasses for the assignments in data.json, plus conversion to and from JSON."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Assignment:
    id: str
    shift_id: str
    agent_id: str

    @classmethod
    def from_dict(cls, data: dict) -> Assignment:
        return cls(id=data["id"], shift_id=data["shiftId"], agent_id=data["agentId"])

    def to_dict(self) -> dict:
        return {"id": self.id, "shiftId": self.shift_id, "agentId": self.agent_id}
