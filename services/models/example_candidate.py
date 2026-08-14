"""
Knowledge Factory

Example Candidate
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExampleCandidate:
    """
    Candidate worked example detected from the Canonical Document.
    """

    block_id: str

    page_number: int

    text: str

    number: str | None

    title: str | None

    section_number: str | None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )