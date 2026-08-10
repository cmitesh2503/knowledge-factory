"""
Knowledge Factory

Chapter Domain Model

Represents one educational chapter extracted from a canonical document.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Chapter:
    """
    Provider-independent educational chapter.
    """

    id: str

    title: str

    number: int |None = None

    start_page: int = 1

    end_page: int = 1

    block_ids: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "number": self.number,
            "title": self.title,
            "start_page": self.start_page,
            "end_page": self.end_page,
            "block_ids": self.block_ids,
            "metadata": self.metadata,
        }