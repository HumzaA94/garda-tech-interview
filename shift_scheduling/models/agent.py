"""Dataclasses for the agents in data.json, plus conversion to and from JSON."""

from __future__ import annotations

from dataclasses import dataclass, field

from shift_scheduling.models.qualification import Qualification


@dataclass
class Agent:
    id: str
    name: str
    qualifications: list[Qualification] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> Agent:
        return cls(
            id=data["id"],
            name=data["name"],
            qualifications=[
                Qualification.from_dict(q) for q in data.get("qualifications", [])
            ],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "qualifications": [q.to_dict() for q in self.qualifications],
        }

    def to_summary(self) -> dict:
        return {"id": self.id, "name": self.name}
