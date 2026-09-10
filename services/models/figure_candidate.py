"""
Knowledge Factory

Provider-Independent Figure Candidate Model

Represents an intermediate figure candidate discovered during
document extraction before it is transformed into the canonical
MathVerse Figure model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class FigureCandidate:
    """
    Intermediate provider-independent figure candidate.

    A FigureCandidate represents a possible educational figure
    discovered in the source document.

    It intentionally preserves extraction and provenance information
    while allowing later pipeline stages to determine:

    - whether the figure is educationally relevant
    - what mathematical concept it represents
    - whether MathVerse should render or redraw it
    - whether the tutor should modify the figure during explanation
    """

    # Stable identifier from the canonical document.
    id: str

    # Source location.
    page: int | None = None
    source_block_id: str | None = None

    # Human-readable source information.
    caption: str | None = None
    description: str | None = None

    # Provider-independent classification.
    figure_type: str | None = None

    # Text or labels detected as belonging to the figure.
    labels: list[str] = field(default_factory=list)

    # Structured mathematical representation, when available.
    geometry: dict[str, Any] = field(default_factory=dict)

    # Rendering hints for downstream consumers.
    rendering: dict[str, Any] = field(default_factory=dict)

    # Educational behaviour or interpretation hints.
    educational: dict[str, Any] = field(default_factory=dict)

    # Potential tutor interaction capabilities.
    interaction: dict[str, Any] = field(default_factory=dict)

    # Mathematical concepts potentially related to this figure.
    related_concepts: list[str] = field(default_factory=list)

    # Educational relevance determined during extraction/linking.
    is_educationally_relevant: bool | None = None

    # Confidence associated with figure detection or interpretation.
    confidence: float | None = None

    # Provider-independent extraction provenance.
    provenance: dict[str, Any] = field(default_factory=dict)

    # Additional information that does not yet belong in the
    # stable canonical schema.
    metadata: dict[str, Any] = field(default_factory=dict)