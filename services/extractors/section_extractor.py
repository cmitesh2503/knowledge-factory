"""
Knowledge Factory

Generic Section Extractor
"""

from __future__ import annotations

from services.extractors.base_extractor import BaseExtractor
from services.extractors.section_number_parser import (
    SectionNumberParser,
)
from services.models import (
    Section,
    SectionCandidate,
)


class SectionExtractor(
    BaseExtractor[
        SectionCandidate,
        Section,
    ]
):
    """
    Generic deterministic section extractor.

    BaseExtractor owns the orchestration:

        find_candidates
              ↓
        validate_candidates
              ↓
        build

    This class only implements section-specific logic.
    """

    def find_candidates(
        self,
        canonical_document: dict,
    ) -> list[SectionCandidate]:

        candidates: list[SectionCandidate] = []

        for page in canonical_document.get(
            "pages",
            [],
        ):

            page_number = page.get("page_number")

            for block in page.get(
                "blocks",
                [],
            ):

                text = str(
                    block.get("text", "")
                ).strip()

                parsed = SectionNumberParser.parse(
                    text
                )

                if parsed is None:
                    continue

                section_number, title = parsed

                candidates.append(
                    SectionCandidate(
                        block_id=block["id"],
                        page_number=page_number,
                        text=text,
                        number=section_number.number,
                        title=title,
                        level=section_number.level,
                        parent_number=(
                            section_number.parent_number
                        ),
                    )
                )

        return candidates

    def validate_candidates(
        self,
        candidates: list[SectionCandidate],
    ) -> list[SectionCandidate]:

        validated: list[SectionCandidate] = []

        for candidate in candidates:

            if not candidate.number:
                continue

            if not candidate.title:
                continue

            validated.append(candidate)

        return validated

    def build(
        self,
        candidates: list[SectionCandidate],
    ) -> list[Section]:

        sections: list[Section] = []

        for index, candidate in enumerate(
            candidates
        ):

            sections.append(
                Section(
                    id=f"section-{index + 1:03}",
                    number=candidate.number,
                    title=candidate.title,
                    level=candidate.level,
                    parent_number=(
                        candidate.parent_number
                    ),
                    page=candidate.page_number,
                    block_id=candidate.block_id,
                )
            )

        return sections