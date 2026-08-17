"""
Knowledge Factory

Figure Extractor

Extracts provider-independent educational figures
from the canonical document.
"""

from __future__ import annotations

from typing import Any

from services.extractors.base_extractor import BaseExtractor
from services.models.figure import Figure
from services.models.figure_candidate import FigureCandidate


class FigureExtractor(BaseExtractor):
    """
    Extract figures from a canonical document.

    Phase 1:
    - Detect canonical figure blocks
    - Preserve stable identifiers
    - Preserve provenance metadata
    - Build Figure domain objects

    Semantic enrichment such as educational purpose,
    related concepts, and explanation strategy is
    intentionally deferred.
    """

    def find_candidates(
        self,
        canonical_document: dict[str, Any],
    ) -> list[FigureCandidate]:

        candidates: list[FigureCandidate] = []

        for page in canonical_document.get("pages", []):

            page_number = page.get("page_number")

            for block in page.get("blocks", []):

                if block.get("type") != "figure":
                    continue

                figure_id = block.get("id")

                if not figure_id:
                    continue

                metadata = dict(
                    block.get("metadata") or {}
                )

                metadata["page"] = page_number

                candidates.append(
                    FigureCandidate(
                        id=figure_id,
                        page=page_number,
                        caption=metadata.get("caption"),
                        description=block.get("text"),
                        metadata=metadata,
                    )
                )

        return candidates

    def validate_candidates(
        self,
        candidates: list[FigureCandidate],
    ) -> list[FigureCandidate]:

        valid: list[FigureCandidate] = []

        for candidate in candidates:

            if not candidate.id:
                continue

            valid.append(candidate)

        return valid

    def build(
        self,
        candidates: list[FigureCandidate],
    ) -> list[Figure]:

        figures: list[Figure] = []

        for candidate in candidates:

            figures.append(
                Figure(
                    id=candidate.id,
                    caption=candidate.caption,
                    description=candidate.description,
                    related_concepts=list(
                        candidate.related_concepts
                    ),
                    metadata=dict(candidate.metadata),
                )
            )

        return figures