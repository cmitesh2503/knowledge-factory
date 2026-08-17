from __future__ import annotations

from typing import Any

from services.extractors.base_extractor import BaseExtractor
from services.models.table import Table
from services.models.table_candidate import TableCandidate


class TableExtractor(
    BaseExtractor[TableCandidate, Table]
):
    """
    Extract provider-independent tables
    from the canonical document.

    Phase 1:
    - Detect canonical table blocks
    - Preserve stable identifiers
    - Preserve table structure
    - Preserve provenance metadata

    Semantic interpretation is intentionally deferred.
    """

    def find_candidates(
        self,
        canonical_document: dict[str, Any],
    ) -> list[TableCandidate]:

        candidates: list[TableCandidate] = []

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
                if block.get("type") != "table":
                    continue

                table_id = block.get(
                    "id"
                )

                if not table_id:
                    continue

                metadata = dict(
                    block.get("metadata") or {}
                )

                metadata["page"] = page_number

                candidates.append(
                    TableCandidate(
                        id=table_id,
                        page=page_number,
                        rows=metadata.get(
                            "row_count",
                            0,
                        ),
                        columns=metadata.get(
                            "column_count",
                            0,
                        ),
                        cells=list(
                            metadata.get(
                                "cells",
                                [],
                            )
                        ),
                        metadata=metadata,
                    )
                )

        return candidates

    def validate_candidates(
        self,
        candidates: list[TableCandidate],
    ) -> list[TableCandidate]:

        valid: list[TableCandidate] = []

        for candidate in candidates:

            if not candidate.id:
                continue

            if candidate.rows <= 0:
                continue

            if candidate.columns <= 0:
                continue

            valid.append(candidate)

        return valid

    def build(
        self,
        candidates: list[TableCandidate],
    ) -> list[Table]:

        tables: list[Table] = []

        for candidate in candidates:

            tables.append(
                Table(
                    id=candidate.id,
                    rows=candidate.rows,
                    columns=candidate.columns,
                    cells=list(
                        candidate.cells
                    ),
                    metadata=dict(
                        candidate.metadata
                    ),
                )
            )

        return tables