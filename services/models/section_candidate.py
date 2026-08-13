"""
Knowledge Factory

Section Candidate
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SectionCandidate:
    """
    Candidate section detected from the Canonical Document.
    """

    block_id: str

    page_number: int

    text: str

    number: str

    title: str

    level: int

    parent_number: str | None

    metadata: dict[str, Any] = field(default_factory=dict)