"""
Knowledge Factory

Figure Domain Model

Represents one educational figure extracted from a
provider-independent canonical document.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Figure:
    """
    Provider-independent educational figure.
    """

    id: str

    caption: str | None = None

    description: str | None = None

    related_concepts: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "caption": self.caption,
            "description": self.description,
            "related_concepts": self.related_concepts,
            "metadata": self.metadata,
        }