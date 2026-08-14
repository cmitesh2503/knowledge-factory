"""
Knowledge Factory

Formula Domain Model
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Formula:
    """
    Provider-independent mathematical formula.
    """

    id: str

    expression: str

    section_number: str | None

    page: int

    block_id: str

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "expression": self.expression,
            "section_number": self.section_number,
            "page": self.page,
            "block_id": self.block_id,
            "metadata": self.metadata,
        }