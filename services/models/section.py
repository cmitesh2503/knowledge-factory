"""
Knowledge Factory

Section Domain Model
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Section:
    """
    Provider-independent educational section.

    Hierarchy is derived from the section number.
    """

    id: str

    number: str

    title: str

    level: int

    parent_number: str | None

    page: int

    block_id: str

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "number": self.number,
            "title": self.title,
            "level": self.level,
            "parent_number": self.parent_number,
            "page": self.page,
            "block_id": self.block_id,
            "metadata": self.metadata,
        }