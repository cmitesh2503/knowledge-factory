"""
Knowledge Factory

Generic Formula Extractor
"""

from __future__ import annotations

from services.extractors.base_extractor import BaseExtractor
from services.extractors.formula_detector import (
    FormulaDetector,
)
from services.extractors.section_number_parser import (
    SectionNumberParser,
)
from services.models import (
    Formula,
    FormulaCandidate,
)


class FormulaExtractor(
    BaseExtractor[
        FormulaCandidate,
        Formula,
    ]
):
    """
    Generic deterministic formula extractor.

    BaseExtractor owns orchestration.

    This extractor:

        1. tracks section context
        2. detects formula-like blocks
        3. validates candidates
        4. builds Formula models
    """

    def find_candidates(
        self,
        canonical_document: dict,
    ) -> list[FormulaCandidate]:

        candidates: list[FormulaCandidate] = []

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

                # Update section context.
                parsed = SectionNumberParser.parse(
                    text
                )

                if parsed is not None:

                    section_number, _ = parsed

                    current_section = (
                        section_number.number
                    )

                    continue

                # Detect mathematical expression.
                if not FormulaDetector.is_formula(
                    text
                ):
                    continue

                candidates.append(
                    FormulaCandidate(
                        block_id=block["id"],
                        page_number=page_number,
                        text=text,
                        section_number=current_section,
                    )
                )

        return candidates

    def validate_candidates(
        self,
        candidates: list[FormulaCandidate],
    ) -> list[FormulaCandidate]:

        validated: list[FormulaCandidate] = []

        for candidate in candidates:

            if not candidate.text.strip():
                continue

            validated.append(candidate)

        return validated

    def build(
        self,
        candidates: list[FormulaCandidate],
    ) -> list[Formula]:

        formulas: list[Formula] = []

        for index, candidate in enumerate(
            candidates
        ):

            formulas.append(
                Formula(
                    id=f"formula-{index + 1:03}",
                    expression=candidate.text,
                    section_number=(
                        candidate.section_number
                    ),
                    page=candidate.page_number,
                    block_id=candidate.block_id,
                )
            )

        return formulas