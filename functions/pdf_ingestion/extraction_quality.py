"""
Extraction quality evaluation.

Determines whether extracted canonical blocks contain
sufficient content to represent the source document.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractionQuality:
    """
    Summary of extraction quality.
    """

    is_acceptable: bool

    page_count: int
    block_count: int

    pages_with_content: int
    coverage_ratio: float

    total_characters: int
    average_characters_per_page: float

    reason: str


class ExtractionQualityEvaluator:
    """
    Evaluate whether extracted blocks provide sufficient
    document coverage and text content.
    """

    def evaluate(
        self,
        *,
        blocks: list[dict],
        page_count: int,
    ) -> ExtractionQuality:
        """
        Evaluate extracted canonical blocks.
        """

        if page_count < 1:

            return ExtractionQuality(
                is_acceptable=False,
                page_count=page_count,
                block_count=len(blocks),
                pages_with_content=0,
                coverage_ratio=0.0,
                total_characters=0,
                average_characters_per_page=0.0,
                reason="Source document has no valid pages.",
            )

        populated_pages = set()
        total_characters = 0

        for block in blocks:

            text = (
                block.get("text")
                or ""
            ).strip()

            if not text:
                continue

            page = block.get("page")

            if isinstance(page, int) and page >= 1:
                populated_pages.add(page)

            total_characters += len(text)

        pages_with_content = len(
            populated_pages
        )

        coverage_ratio = (
            pages_with_content / page_count
        )

        average_characters_per_page = (
            total_characters / page_count
        )

        is_acceptable = (
            coverage_ratio >= 0.60
            and average_characters_per_page >= 100
        )

        if coverage_ratio < 0.60:

            reason = (
                "Too few pages contain extracted text."
            )

        elif average_characters_per_page < 100:

            reason = (
                "Extracted text volume is too low."
            )

        else:

            reason = (
                "Extraction meets minimum quality thresholds."
            )

        return ExtractionQuality(
            is_acceptable=is_acceptable,
            page_count=page_count,
            block_count=len(blocks),
            pages_with_content=pages_with_content,
            coverage_ratio=coverage_ratio,
            total_characters=total_characters,
            average_characters_per_page=(
                average_characters_per_page
            ),
            reason=reason,
        )