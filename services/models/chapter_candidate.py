"""
Knowledge Factory

Chapter Candidate

Represents a possible chapter detected from the
Canonical Document before validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ChapterCandidate:
    """
    Candidate chapter found during extraction.
    """

    block_id: str

    page_number: int

    text: str

    score: float = 0.0

    geometry: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "block_id": self.block_id,
            "page_number": self.page_number,
            "text": self.text,
            "score": self.score,
            "geometry": self.geometry,
            "metadata": self.metadata,
        }