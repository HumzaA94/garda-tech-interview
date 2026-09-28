"""Dataclasses for the qualifications in data.json, plus conversion to and from JSON."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class Qualification:
    code: str
    expires_on: date

    @classmethod
    def from_dict(cls, data: dict) -> Qualification:
        return cls(code=data["code"], expires_on=date.fromisoformat(data["expiresOn"]))

    def to_dict(self) -> dict:
        return {"code": self.code, "expiresOn": self.expires_on.isoformat()}
