from __future__ import annotations

import re
from typing import Any

from services.models.knowledge_package import KnowledgePackage


class KnowledgeChunkBuilder:
    """
    Builds semantic-search chunks from a KnowledgePackage.

    The KnowledgePackage remains the canonical source.
    These chunks are derived data for vector indexing.
    """

    MIN_TEXT_LENGTH = 40
    MIN_WORDS = 6

    def build(
        self,
        package: KnowledgePackage,
    ) -> list[dict[str, Any]]:
        """
        Build meaningful chunks from concepts.

        Adjacent concepts belonging to the same section
        are merged when they form a coherent passage.
        """

        candidates = self._build_candidates(package)

        if not candidates:
            return []

        return self._merge_adjacent_chunks(
            candidates
        )

    def _build_candidates(
        self,
        package: KnowledgePackage,
    ) -> list[dict[str, Any]]:

        candidates: list[dict[str, Any]] = []

        for concept in package.concepts:

            text = self._clean_text(
                self._concept_text(concept)
            )

            if not self._is_meaningful(text):
                continue

            candidates.append(
                {
                    "id": concept.id,
                    "knowledge_type": "concept",
                    "text": text,
                    "metadata": {
                        "document_id": package.document_id,
                        "concept_id": concept.id,
                        "section_number": (
                            concept.section_number
                        ),
                        "page": concept.page,
                        "block_id": concept.block_id,
                    },
                }
            )

        return candidates

    def _merge_adjacent_chunks(
        self,
        candidates: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        chunks: list[dict[str, Any]] = []

        current = candidates[0]

        for candidate in candidates[1:]:

            if self._should_merge(
                current,
                candidate,
            ):
                current = self._merge(
                    current,
                    candidate,
                )
            else:
                chunks.append(current)
                current = candidate

        chunks.append(current)

        return chunks

    def _should_merge(
        self,
        current: dict[str, Any],
        candidate: dict[str, Any],
    ) -> bool:

        current_metadata = current["metadata"]
        candidate_metadata = candidate["metadata"]

        # Only merge content from the same section.
        if (
            current_metadata["section_number"]
            != candidate_metadata["section_number"]
        ):
            return False

        # Only merge adjacent pages/blocks.
        current_page = current_metadata["page"]
        candidate_page = candidate_metadata["page"]

        if candidate_page < current_page:
            return False

        # Avoid creating excessively large chunks.
        combined_length = (
            len(current["text"])
            + len(candidate["text"])
            + 1
        )

        if combined_length > 1500:
            return False

        return True

    def _merge(
        self,
        current: dict[str, Any],
        candidate: dict[str, Any],
    ) -> dict[str, Any]:

        current["text"] = (
            current["text"]
            + " "
            + candidate["text"]
        )

        current["metadata"][
            "source_ids"
        ] = (
            current["metadata"].get(
                "source_ids",
                [current["metadata"]["concept_id"]],
            )
            + [
                candidate["metadata"][
                    "concept_id"
                ]
            ]
        )

        current["metadata"][
            "end_page"
        ] = candidate["metadata"]["page"]

        current["metadata"][
            "end_block_id"
        ] = candidate["metadata"]["block_id"]

        return current

    def _concept_text(
        self,
        concept: Any,
    ) -> str:

        parts: list[str] = []

        name = getattr(
            concept,
            "name",
            None,
        )

        if name:
            parts.append(str(name))

        metadata = getattr(
            concept,
            "metadata",
            {}
        ) or {}

        for key in (
            "description",
            "text",
            "content",
            "body",
        ):
            value = metadata.get(key)

            if value:
                parts.append(str(value))

        return " ".join(parts)

    def _clean_text(
        self,
        text: str,
    ) -> str:

        text = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        return text

    def _is_meaningful(
        self,
        text: str,
    ) -> bool:

        if len(text) < self.MIN_TEXT_LENGTH:
            return False

        if len(text.split()) < self.MIN_WORDS:
            return False

        return True