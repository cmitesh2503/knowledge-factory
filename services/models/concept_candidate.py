"""
Knowledge Factory

Concept Candidate
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ConceptCandidate:
    """
    Candidate concept detected from the Canonical Document.
    """

    block_id: str

    page_number: int

    text: str

    section_number: str | None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )