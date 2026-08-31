from __future__ import annotations

import re
from typing import Any

from services.models.knowledge_package import KnowledgePackage


class KnowledgeChunkBuilder:
    """
    Builds semantic-search chunks from a KnowledgePackage.

    The KnowledgePackage remains the canonical source.
    These chunks are derived data for vector indexing.

    Concept chunks may be merged when adjacent and
    semantically related. Table chunks remain atomic.
    """

    MIN_TEXT_LENGTH = 40
    MIN_WORDS = 6
    MAX_CHUNK_LENGTH = 1500

    def build(
        self,
        package: KnowledgePackage,
    ) -> list[dict[str, Any]]:
        """
        Build semantic-search chunks from a KnowledgePackage.
        """

        candidates = self._build_candidates(
            package
        )

        if not candidates:
            return []

        concept_candidates = [
            candidate
            for candidate in candidates
            if candidate["knowledge_type"] == "concept"
        ]

        table_chunks = [
            candidate
            for candidate in candidates
            if candidate["knowledge_type"] == "table"
        ]

        concept_chunks: list[dict[str, Any]] = []

        if concept_candidates:
            concept_chunks = (
                self._merge_adjacent_chunks(
                    concept_candidates
                )
            )

        return concept_chunks + table_chunks

    def _build_candidates(
        self,
        package: KnowledgePackage,
    ) -> list[dict[str, Any]]:

        candidates: list[dict[str, Any]] = []

        # ---------------------------------------------
        # Concept candidates
        # ---------------------------------------------

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
                        "document_id": (
                            package.document_id
                        ),
                        "concept_id": concept.id,
                        "section_number": (
                            concept.section_number
                        ),
                        "page": concept.page,
                        "block_id": concept.block_id,
                    },
                }
            )

        # ---------------------------------------------
        # Table candidates
        # ---------------------------------------------

        for table in package.tables:

            text = self._table_text(
                table
            )

            if not text.strip():
                continue

            candidates.append(
                {
                    "id": table.id,
                    "knowledge_type": "table",
                    "text": text,
                    "metadata": {
                        "document_id": (
                            package.document_id
                        ),
                        "table_id": table.id,
                        "page": table.metadata.get(
                            "page"
                        ),
                        "table_index": (
                            table.metadata.get(
                                "table_index"
                            )
                        ),
                        "rows": table.rows,
                        "columns": table.columns,
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

        current_metadata = current[
            "metadata"
        ]

        candidate_metadata = candidate[
            "metadata"
        ]

        # Only merge concepts from the same section.

        if (
            current_metadata["section_number"]
            != candidate_metadata["section_number"]
        ):
            return False

        # Do not merge backwards across pages.

        current_page = current_metadata[
            "page"
        ]

        candidate_page = candidate_metadata[
            "page"
        ]

        if (
            current_page is not None
            and candidate_page is not None
            and candidate_page < current_page
        ):
            return False

        # Avoid excessively large chunks.

        combined_length = (
            len(current["text"])
            + len(candidate["text"])
            + 1
        )

        if combined_length > self.MAX_CHUNK_LENGTH:
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
                [
                    current["metadata"][
                        "concept_id"
                    ]
                ],
            )
            + [
                candidate["metadata"][
                    "concept_id"
                ]
            ]
        )

        current["metadata"][
            "end_page"
        ] = candidate["metadata"][
            "page"
        ]

        current["metadata"][
            "end_block_id"
        ] = candidate["metadata"][
            "block_id"
        ]

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
            parts.append(
                str(name)
            )

        metadata = getattr(
            concept,
            "metadata",
            {},
        ) or {}

        for key in (
            "description",
            "text",
            "content",
            "body",
        ):

            value = metadata.get(
                key
            )

            if value:
                parts.append(
                    str(value)
                )

        return " ".join(parts)

    def _table_text(
        self,
        table: Any,
    ) -> str:
        """
        Convert a structured table into searchable text
        while preserving row and column structure.

        Sparse cells remain represented as empty positions.
        """

        cells_by_row: dict[
            int,
            dict[int, str],
        ] = {}

        for cell in table.cells:

            row_index = cell.get(
                "row_index"
            )

            column_index = cell.get(
                "column_index"
            )

            if (
                row_index is None
                or column_index is None
            ):
                continue

            cells_by_row.setdefault(
                row_index,
                {},
            )[column_index] = str(
                cell.get(
                    "content",
                    "",
                )
            )

        rows: list[str] = []

        # Preserve the declared table dimensions,
        # including completely empty rows.

        for row_index in range(
            table.rows
        ):

            row = cells_by_row.get(
                row_index,
                {},
            )

            values = [
                row.get(
                    column_index,
                    "",
                )
                for column_index in range(
                    table.columns
                )
            ]

            rows.append(
                " | ".join(values)
            )

        return "\n".join(rows)

    def _clean_text(
        self,
        text: str,
    ) -> str:
        """
        Normalize ordinary semantic text.

        This is intentionally not used for tables because
        whitespace inside tables carries structural meaning.
        """

        return re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

    def _is_meaningful(
        self,
        text: str,
    ) -> bool:

        if (
            len(text)
            < self.MIN_TEXT_LENGTH
        ):
            return False

        if (
            len(text.split())
            < self.MIN_WORDS
        ):
            return False

        return True