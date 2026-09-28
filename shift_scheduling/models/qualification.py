"""Dataclasses for the qualifications in data.json, plus conversion to and from JSON."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class QualificationCode(StrEnum):
    GUARD_LICENSE = "GUARD_LICENSE"
    FIRST_AID = "FIRST_AID"
    CROWD_CONTROL = "CROWD_CONTROL"


@dataclass
class Qualification:
    code: QualificationCode
    expires_on: date

    @classmethod
    def from_dict(cls, data: dict) -> Qualification:
        return cls(
            code=QualificationCode(data["code"]),
            expires_on=date.fromisoformat(data["expiresOn"]),
        )

    def to_dict(self) -> dict:
        return {"code": self.code.value, "expiresOn": self.expires_on.isoformat()}
