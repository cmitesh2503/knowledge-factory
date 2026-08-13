"""
Knowledge Factory

Generic Concept Extractor
"""

from __future__ import annotations

import re

from services.extractors.base_extractor import BaseExtractor
from services.extractors.section_number_parser import (
    SectionNumberParser,
)
from services.models import (
    Concept,
    ConceptCandidate,
)


class ConceptExtractor(
    BaseExtractor[
        ConceptCandidate,
        Concept,
    ]
):
    """
    Generic deterministic concept extractor.

    BaseExtractor owns orchestration:

        find_candidates()
              ↓
        validate_candidates()
              ↓
        build()

    This extractor does not use AI inference.
    """

    CHAPTER_CODE_PATTERN = re.compile(
        r"^[A-Za-z0-9_-]*\d+[A-Za-z0-9_-]*$"
    )

    def find_candidates(
        self,
        canonical_document: dict,
    ) -> list[ConceptCandidate]:

        candidates: list[ConceptCandidate] = []

        current_section: str | None = None

        for page in canonical_document.get(
            "pages",
            [],
        ):

            page_number = page.get(
                "page_number"
            )

            for block in page.get(
                "blocks",
                [],
            ):

                text = str(
                    block.get(
                        "text",
                        "",
                    )
                ).strip()

                if not text:
                    continue

                # Section heading?
                parsed = SectionNumberParser.parse(
                    text
                )

                if parsed is not None:

                    section_number, _ = parsed

                    current_section = (
                        section_number.number
                    )

                    continue

                # Ignore obvious document/chapter codes.
                if self.CHAPTER_CODE_PATTERN.fullmatch(
                    text
                ):
                    continue

                # Only consider actual textual content.
                candidates.append(
                    ConceptCandidate(
                        block_id=block["id"],
                        page_number=page_number,
                        text=text,
                        section_number=current_section,
                    )
                )

        return candidates

    def validate_candidates(
        self,
        candidates: list[ConceptCandidate],
    ) -> list[ConceptCandidate]:

        validated: list[ConceptCandidate] = []

        for candidate in candidates:

            text = candidate.text.strip()

            if not text:
                continue

            # A concept candidate needs section context.
            if candidate.section_number is None:
                continue

            validated.append(candidate)

        return validated

    def build(
        self,
        candidates: list[ConceptCandidate],
    ) -> list[Concept]:

        concepts: list[Concept] = []

        for index, candidate in enumerate(
            candidates
        ):

            concepts.append(
                Concept(
                    id=f"concept-{index + 1:03}",
                    name=candidate.text,
                    section_number=(
                        candidate.section_number
                    ),
                    page=candidate.page_number,
                    block_id=candidate.block_id,
                )
            )

        return concepts