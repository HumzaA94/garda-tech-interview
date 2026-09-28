from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data.json"


@dataclass(frozen=True)
class Config:
    """Configuration for the shift scheduling application."""

    data_path: Path = DEFAULT_DATA_PATH

    @classmethod
    def from_env(cls) -> Config:
        """Create a Config instance from environment variables."""
        return cls(data_path=Path(os.environ.get("DATA_PATH", DEFAULT_DATA_PATH)))
