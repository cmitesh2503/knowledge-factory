"""
Knowledge Factory

Concept Domain Model
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Concept:
    """
    Provider-independent educational concept.

    A concept belongs to a section and represents
    a teachable mathematical idea.
    """

    id: str

    name: str

    section_number: str | None

    page: int

    block_id: str

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "section_number": self.section_number,
            "page": self.page,
            "block_id": self.block_id,
            "metadata": self.metadata,
        }