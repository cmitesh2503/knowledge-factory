"""
Knowledge Factory

Figure Domain Model

Represents one provider-independent educational figure
that can be used by MathVerse for rendering, explanation,
modification, and animation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Figure:
    """
    Provider-independent educational figure.

    The Figure model describes an educational or mathematical
    visual concept independently of the document extraction
    provider and independently of the MathVerse rendering engine.

    A figure may originate from a textbook, be reconstructed by
    MathVerse, or be extended dynamically by the tutor while
    explaining a concept or solving a problem.
    """

    # Stable canonical identifier.
    id: str

    # Human-readable information extracted from the source.
    caption: str | None = None
    description: str | None = None

    # High-level provider-independent classification.
    #
    # Examples:
    # - geometry_diagram
    # - coordinate_graph
    # - function_plot
    # - trigonometric_graph
    # - number_line
    # - mathematical_diagram
    # - chart
    # - illustration
    figure_type: str | None = None

    # Mathematical concepts represented or supported by the figure.
    related_concepts: list[str] = field(default_factory=list)

    # Textual labels associated with the figure.
    #
    # Examples:
    # - A
    # - B
    # - C
    # - theta
    # - x
    # - y
    # - 5 cm
    labels: list[str] = field(default_factory=list)

    # Structured mathematical representation.
    #
    # This contains provider-independent primitives such as
    # points, lines, circles, axes, curves, polygons, angles,
    # dimensions, and annotations.
    geometry: dict[str, Any] = field(default_factory=dict)

    # Rendering hints for MathVerse.
    #
    # These are hints rather than renderer-specific commands.
    rendering: dict[str, Any] = field(default_factory=dict)

    # Educational behaviour associated with the figure.
    #
    # Examples may include:
    # - what should be highlighted
    # - what may be animated
    # - what should be introduced step-by-step
    educational: dict[str, Any] = field(default_factory=dict)

    # Determines whether the tutor may extend or modify
    # the figure during explanation or problem solving.
    #
    # Examples:
    # - add auxiliary line
    # - add point
    # - add label
    # - highlight region
    # - modify existing construction
    interaction: dict[str, Any] = field(default_factory=dict)

    # Source and extraction provenance.
    #
    # Examples:
    # - page number
    # - source block id
    # - extraction provider
    # - source reference
    provenance: dict[str, Any] = field(default_factory=dict)

    # Confidence associated with extraction or interpretation.
    confidence: float | None = None

    # Whether the figure is considered educationally relevant
    # to the document or surrounding learning context.
    is_educationally_relevant: bool | None = None

    # Additional information that is not yet part of the
    # stable canonical contract.
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the canonical figure."""

        return {
            "id": self.id,
            "caption": self.caption,
            "description": self.description,
            "figure_type": self.figure_type,
            "related_concepts": list(self.related_concepts),
            "labels": list(self.labels),
            "geometry": dict(self.geometry),
            "rendering": dict(self.rendering),
            "educational": dict(self.educational),
            "interaction": dict(self.interaction),
            "provenance": dict(self.provenance),
            "confidence": self.confidence,
            "is_educationally_relevant": (
                self.is_educationally_relevant
            ),
            "metadata": dict(self.metadata),
        }