"""
Knowledge Factory

Example Domain Model
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Example:
    """
    Provider-independent worked example.
    """

    id: str

    number: str | None

    title: str | None

    content: list[str]

    section_number: str | None

    page: int

    block_id: str

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "number": self.number,
            "title": self.title,
            "content": self.content,
            "section_number": self.section_number,
            "page": self.page,
            "block_id": self.block_id,
            "metadata": self.metadata,
        }