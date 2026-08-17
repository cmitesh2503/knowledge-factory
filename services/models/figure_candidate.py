"""
Knowledge Factory

Figure Candidate Model
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class FigureCandidate:
    """
    Intermediate candidate discovered during figure extraction.
    """

    id: str

    page: int | None = None

    caption: str | None = None

    description: str | None = None

    related_concepts: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)