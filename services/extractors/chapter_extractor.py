"""
Knowledge Factory

Chapter Extractor

Extracts educational chapters from a Canonical Document.

Pipeline

Canonical Document
        │
        ▼
Find Candidates
        ▼
Validate Candidates
        ▼
Build Chapters
"""

from __future__ import annotations

import re

from services.extractors.base_extractor import BaseExtractor
from services.extractors.heading_classifier import HeadingClassifier

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
    """

    CHAPTER_PATTERNS = [

        re.compile(r"^chapter\s+(\d+)", re.IGNORECASE),

        re.compile(r"^chapter\s+([ivxlcdm]+)", re.IGNORECASE),

    ]

    def __init__(self):

        self.heading_classifier = HeadingClassifier()

    # -----------------------------------------------------
    # Public API
    # -----------------------------------------------------

    def extract(
        self,
        canonical_document: dict,
    ) -> ExtractionResult[Chapter]:

        candidates = self.find_candidates(canonical_document)

        candidates = self.validate_candidates(candidates)

        chapters = self.build(candidates)

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

            for block in page.get("blocks", []):

                if not self.heading_classifier.is_heading(block):
                    continue

                score = self._score_candidate(block)

                if score < 60:
                    continue

                candidates.append(

                    ChapterCandidate(

                        block_id=block["id"],

                        page_number=page["page_number"],

                        text=block["text"],

                        score=score,

                        geometry=block.get("geometry", {}),

                    )

                )

        return candidates

    def validate_candidates(
        self,
        candidates: list[ChapterCandidate],
    ) -> list[ChapterCandidate]:

        return candidates

    def build(
        self,
        candidates: list[ChapterCandidate],
    ) -> list[Chapter]:

        chapters: list[Chapter] = []

        for index, candidate in enumerate(candidates):

            chapters.append(

                Chapter(

                    id=f"chapter-{index+1:03}",

                    number=self._chapter_number(candidate.text),

                    title=self._chapter_title(candidate.text),

                    start_page=candidate.page_number,

                    end_page=candidate.page_number,

                    block_ids=[candidate.block_id],

                )

            )

        return chapters

    # -----------------------------------------------------
    # Candidate Scoring
    # -----------------------------------------------------

    def _score_candidate(
        self,
        block: dict,
    ) -> float:

        score = 0.0

        text = str(block.get("text", "")).strip()

        if block.get("type") == "heading":
            score += 40

        if len(text.split()) <= 8:
            score += 10

        if not text.endswith("."):
            score += 10

        geometry = block.get("geometry", {})

        bbox = geometry.get("bounding_box", {})

        top = bbox.get("top")

        if top is not None and top <= 0.20:
            score += 20

        if text.lower().startswith("chapter"):
            score += 20

        if text.isupper():
            score += 10

        return score

    # -----------------------------------------------------
    # Helpers
    # -----------------------------------------------------

    def _chapter_number(
        self,
        text: str,
    ):

        for pattern in self.CHAPTER_PATTERNS:

            match = pattern.match(text)

            if not match:
                continue

            value = match.group(1)

            if value.isdigit():
                return int(value)

            return None

        return None

    def _chapter_title(
        self,
        text: str,
    ) -> str:

        text = text.strip()

        for pattern in self.CHAPTER_PATTERNS:

            match = pattern.match(text)

            if not match:
                continue

            return text[match.end():].strip(" :-")

        return text