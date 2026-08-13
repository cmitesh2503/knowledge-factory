"""
Knowledge Factory

Chapter Extractor

Extracts educational chapters from a Canonical Document.

Pipeline

Canonical Document
        │
        ▼
Find Chapter Candidates
        │
        ▼
Validate Candidates
        │
        ▼
Build Chapters
"""

from __future__ import annotations

import re

from services.extractors.base_extractor import BaseExtractor
from services.models import (
    Chapter,
    ChapterCandidate,
    ExtractionResult,
)


class ChapterExtractor(
    BaseExtractor[
        ChapterCandidate,
        Chapter,
    ]
):
    """
    Deterministic Chapter Extractor.

    Chapter detection is based on chapter-specific structure,
    not on Document AI heading classification.

    Example:

        Chapter 3
        MATRICES

    becomes:

        number = 3
        title  = MATRICES
    """

    CHAPTER_PATTERNS = [
        re.compile(r"^chapter\s+(\d+)\s*$", re.IGNORECASE),
        re.compile(
            r"^chapter\s+([ivxlcdm]+)\s*$",
            re.IGNORECASE,
        ),
    ]

    # -----------------------------------------------------
    # Public API
    # -----------------------------------------------------

    def extract(
        self,
        canonical_document: dict,
    ) -> ExtractionResult[Chapter]:

        candidates = self.find_candidates(canonical_document)

        candidates = self.validate_candidates(candidates)

        chapters = self.build(candidates,page_count=len(canonical_document.get("pages", [])),)

        return ExtractionResult(items=chapters)

    # -----------------------------------------------------
    # BaseExtractor
    # -----------------------------------------------------

    def find_candidates(
        self,
        canonical_document: dict,
    ) -> list[ChapterCandidate]:

        candidates: list[ChapterCandidate] = []

        pages = canonical_document.get("pages", [])

        for page in pages:

            page_number = page.get("page_number")

            blocks = page.get("blocks", [])

            for index, block in enumerate(blocks):

                text = str(block.get("text", "")).strip()

                if not self._is_chapter_marker(text):
                    continue

                title = self._find_adjacent_title(
                    blocks=blocks,
                    index=index,
                )

                score = self._score_candidate(
                    block=block,
                    title=title,
                )

                candidates.append(
                    ChapterCandidate(
                        block_id=block["id"],
                        page_number=page_number,
                        text=text,
                        score=score,
                        geometry=block.get("geometry", {}),
                        metadata={
                            "chapter_title": title,
                        },
                    )
                )

        return candidates

    def validate_candidates(
        self,
        candidates: list[ChapterCandidate],
    ) -> list[ChapterCandidate]:

        validated: list[ChapterCandidate] = []

        for candidate in candidates:

            title = candidate.metadata.get(
                "chapter_title"
            )

            if not title:
                continue

            validated.append(candidate)

        return validated

    def build(
        self,
        candidates: list[ChapterCandidate],
        page_count: int,
    ) -> list[Chapter]:

        chapters: list[Chapter] = []

        for index, candidate in enumerate(candidates):

            title = candidate.metadata["chapter_title"]

            # Determine chapter end page.
            # If another chapter exists, this chapter ends
            # on the page immediately before the next chapter.
            # Otherwise, it ends at the last page of the document.
            if index + 1 < len(candidates):
                end_page = candidates[index + 1].page_number - 1
            else:
                end_page = page_count

            chapters.append(
                Chapter(
                    id=f"chapter-{index + 1:03}",
                    number=self._chapter_number(
                        candidate.text
                    ),
                    title=title,
                    start_page=candidate.page_number,
                    end_page=end_page,
                    block_ids=[
                        candidate.block_id
                    ],
                    metadata={
                        "title_block_id": candidate.metadata.get(
                            "title_block_id"
                        ),
                    },
                )
            )

        return chapters

    # -----------------------------------------------------
    # Chapter Detection
    # -----------------------------------------------------

    def _is_chapter_marker(
        self,
        text: str,
    ) -> bool:

        for pattern in self.CHAPTER_PATTERNS:

            if pattern.match(text):
                return True

        return False

    # -----------------------------------------------------
    # Title Detection
    # -----------------------------------------------------

    def _find_adjacent_title(
        self,
        blocks: list[dict],
        index: int,
    ) -> str | None:

        for next_index in range(index + 1, len(blocks)):

            next_block = blocks[next_index]

            title = str(
                next_block.get("text", "")
            ).strip()

            if not title:
                continue

            # Ignore document/header codes such as:
            # 12079CH03
            if re.fullmatch(r"[A-Za-z0-9_-]+", title) and any(
                char.isdigit() for char in title
            ):
                continue

            # Do not cross into numbered sections.
            if self._looks_like_section_heading(title):
                return None

            # Chapter title in our reference document:
            # MATRICES
            if title.isupper():
                return title.title()

        return None

    def _looks_like_section_heading(
        self,
        text: str,
    ) -> bool:

        return bool(
            re.match(
                r"^\d+(?:\.\d+)+\s+",
                text,
            )
        )

    # -----------------------------------------------------
    # Candidate Scoring
    # -----------------------------------------------------

    def _score_candidate(
        self,
        block: dict,
        title: str | None,
    ) -> float:

        score = 0.0

        text = str(
            block.get("text", "")
        ).strip()

        # Chapter marker itself is strong evidence.
        if self._is_chapter_marker(text):
            score += 60

        # Document AI classification is only supporting
        # evidence. It must NOT be required.
        if block.get("type") == "heading":
            score += 10

        # A valid adjacent uppercase title strongly
        # confirms the chapter structure.
        if title:
            score += 30

        return score

    # -----------------------------------------------------
    # Helpers
    # -----------------------------------------------------

    def _chapter_number(
        self,
        text: str,
    ) -> int | None:

        for pattern in self.CHAPTER_PATTERNS:

            match = pattern.match(text)

            if not match:
                continue

            value = match.group(1)

            if value.isdigit():
                return int(value)

            # Roman numerals are currently not converted.
            return None

        return None