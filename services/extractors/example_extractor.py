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
        current_example: ExampleCandidate | None = None

        def flush_example() -> None:
            nonlocal current_example

            if current_example is not None:
                candidates.append(current_example)

            current_example = None

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
                    block.get(
                        "text",
                        "",
                    )
                ).strip()

                if not text:
                    continue

                # Section boundary
                parsed = SectionNumberParser.parse(text)

                if parsed is not None:

                    flush_example()

                    section_number, _ = parsed

                    current_section = (
                        section_number.number
                    )

                    continue

                # Example marker
                detected = ExampleDetector.detect(text)

                if detected is not None:

                    flush_example()

                    number, title = detected

                    current_example = ExampleCandidate(
                        block_id=block["id"],
                        page_number=page_number,
                        text=text,
                        number=number,
                        title=title,
                        section_number=current_section,
                    )

                    continue

                # Content belonging to current example
                if current_example is not None:

                    current_example.content.append(text)

        flush_example()

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
                    content=candidate.content,
                    section_number=(
                        candidate.section_number
                    ),
                    page=candidate.page_number,
                    block_id=candidate.block_id,
                )
            )

        return examples