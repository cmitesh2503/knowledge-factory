"""
Knowledge Factory

Generic Example Extractor
"""

from __future__ import annotations

from services.extractors.base_extractor import BaseExtractor
from services.extractors.example_detector import (
    ExampleDetector,
)
from services.extractors.section_number_parser import (
    SectionNumberParser,
)
from services.models import (
    Example,
    ExampleCandidate,
)


class ExampleExtractor(
    BaseExtractor[
        ExampleCandidate,
        Example,
    ]
):
    """
    Generic deterministic worked-example extractor.

    BaseExtractor owns:

        find_candidates()
              ↓
        validate_candidates()
              ↓
        build()
    """

    def find_candidates(
        self,
        canonical_document: dict,
    ) -> list[ExampleCandidate]:

        candidates: list[ExampleCandidate] = []

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

                # Track current section.
                parsed = SectionNumberParser.parse(
                    text
                )

                if parsed is not None:

                    section_number, _ = parsed

                    current_section = (
                        section_number.number
                    )

                    continue

                detected = ExampleDetector.detect(
                    text
                )

                if detected is None:
                    continue

                number, title = detected

                candidates.append(
                    ExampleCandidate(
                        block_id=block["id"],
                        page_number=page_number,
                        text=text,
                        number=number,
                        title=title,
                        section_number=current_section,
                    )
                )

        return candidates

    def validate_candidates(
        self,
        candidates: list[ExampleCandidate],
    ) -> list[ExampleCandidate]:

        validated: list[ExampleCandidate] = []

        for candidate in candidates:

            if not candidate.text.strip():
                continue

            validated.append(candidate)

        return validated

    def build(
        self,
        candidates: list[ExampleCandidate],
    ) -> list[Example]:

        examples: list[Example] = []

        for index, candidate in enumerate(
            candidates
        ):

            examples.append(
                Example(
                    id=f"example-{index + 1:03}",
                    number=candidate.number,
                    title=candidate.title,
                    content=candidate.text,
                    section_number=(
                        candidate.section_number
                    ),
                    page=candidate.page_number,
                    block_id=candidate.block_id,
                )
            )

        return examples