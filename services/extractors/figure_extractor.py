"""
Knowledge Factory

Figure Extractor

Extracts provider-independent educational figures
from the canonical document.

The extractor reads canonical figure blocks and converts
them into provider-independent FigureCandidate objects.

It does not depend on Google Document AI, Azure Document
Intelligence, or any other extraction provider.
"""

from __future__ import annotations

from typing import Any

from services.extractors.base_extractor import BaseExtractor
from services.models.figure import Figure
from services.models.figure_candidate import FigureCandidate


class FigureExtractor(BaseExtractor):
    """
    Extract figures from a canonical document.

    Phase 1 responsibilities:

    - Detect canonical figure blocks
    - Preserve stable identifiers
    - Preserve source block identifiers
    - Preserve captions and descriptions
    - Preserve figure classification
    - Preserve labels
    - Preserve related concepts
    - Preserve educational relevance
    - Preserve provenance
    - Preserve extraction confidence

    Semantic interpretation and figure reconstruction
    are intentionally deferred to later stages.
    """

    def find_candidates(
        self,
        canonical_document: dict[str, Any],
    ) -> list[FigureCandidate]:
        """Find figure candidates from a canonical document."""

        candidates: list[FigureCandidate] = []

        for page in canonical_document.get("pages", []):
            page_number = page.get("page_number")

            for block in page.get("blocks", []):
                if block.get("type") != "figure":
                    continue

                figure_id = (
                    block.get("figure", {}).get("id")
                    or block.get("id")
                )

                if not figure_id:
                    continue

                figure_data = dict(
                    block.get("figure") or {}
                )

                metadata = dict(
                    block.get("metadata") or {}
                )

                # Preserve page provenance even when the
                # provider did not explicitly include it.
                metadata.setdefault(
                    "page",
                    page_number,
                )

                provenance = dict(
                    figure_data.get("provenance") or {}
                )

                provenance.setdefault(
                    "page",
                    page_number,
                )

                provenance.setdefault(
                    "source_block_id",
                    block.get("id"),
                )

                candidate = FigureCandidate(
                    id=figure_id,
                    page=page_number,
                    source_block_id=(
                        figure_data.get(
                            "source_block_id"
                        )
                        or block.get("id")
                    ),
                    caption=(
                        figure_data.get("caption")
                        or metadata.get("caption")
                    ),
                    description=(
                        figure_data.get("description")
                        or block.get("text")
                    ),
                    figure_type=figure_data.get(
                        "figure_type"
                    ),
                    labels=list(
                        figure_data.get("labels") or []
                    ),
                    geometry=dict(
                        figure_data.get("geometry") or {}
                    ),
                    rendering=dict(
                        figure_data.get("rendering") or {}
                    ),
                    educational=dict(
                        figure_data.get("educational") or {}
                    ),
                    interaction=dict(
                        figure_data.get("interaction") or {}
                    ),
                    related_concepts=list(
                        figure_data.get(
                            "related_concepts"
                        )
                        or []
                    ),
                    is_educationally_relevant=(
                        figure_data.get(
                            "is_educationally_relevant"
                        )
                    ),
                    confidence=figure_data.get(
                        "confidence"
                    ),
                    provenance=provenance,
                    metadata=metadata,
                )

                candidates.append(candidate)

        return candidates

    def validate_candidates(
        self,
        candidates: list[FigureCandidate],
    ) -> list[FigureCandidate]:
        """Validate figure candidates for downstream processing."""

        valid: list[FigureCandidate] = []

        for candidate in candidates:
            if not candidate.id:
                continue

            # A candidate must have at least some source
            # location information to remain traceable.
            if (
                candidate.page is None
                and not candidate.source_block_id
            ):
                continue

            valid.append(candidate)

        return valid

    def build(
        self,
        candidates: list[FigureCandidate],
    ) -> list[Figure]:
        """Convert validated candidates into Figure domain models."""

        return self.to_figures(candidates)

    def to_figures(
        self,
        candidates: list[FigureCandidate],
    ) -> list[Figure]:
        """Convert validated figure candidates into Figures."""

        figures: list[Figure] = []

        for candidate in candidates:
            figures.append(
                Figure(
                    id=candidate.id,
                    caption=candidate.caption,
                    description=candidate.description,
                    figure_type=candidate.figure_type,
                    related_concepts=list(
                        candidate.related_concepts
                    ),
                    labels=list(
                        candidate.labels
                    ),
                    geometry=dict(
                        candidate.geometry
                    ),
                    rendering=dict(
                        candidate.rendering
                    ),
                    educational=dict(
                        candidate.educational
                    ),
                    interaction=dict(
                        candidate.interaction
                    ),
                    provenance=dict(
                        candidate.provenance
                    ),
                    confidence=candidate.confidence,
                    is_educationally_relevant=(
                        candidate.is_educationally_relevant
                    ),
                    metadata=dict(
                        candidate.metadata
                    ),
                )
            )

        return figures