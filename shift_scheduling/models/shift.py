"""Dataclasses for the shifts in data.json, plus conversion to and from JSON."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from shift_scheduling.models.qualification import QualificationCode
from shift_scheduling.utils.time import format_time, parse_time


@dataclass
class Shift:
    id: str
    site: str
    start: datetime
    end: datetime
    headcount: int
    required_qualifications: list[QualificationCode] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> Shift:
        return cls(
            id=data["id"],
            site=data["site"],
            start=parse_time(data["start"]),
            end=parse_time(data["end"]),
            headcount=data["headcount"],
            required_qualifications=[
                QualificationCode(code)
                for code in data.get("requiredQualifications") or []
            ],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "site": self.site,
            "start": format_time(self.start),
            "end": format_time(self.end),
            "requiredQualifications": [
                code.value for code in self.required_qualifications
            ],
            "headcount": self.headcount,
        }

    def overlaps(self, other: Shift) -> bool:
        """Touching endpoints (one ends exactly when the other starts) don't overlap."""
        return self.start < other.end and other.start < self.end
