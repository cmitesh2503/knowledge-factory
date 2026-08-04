"""
Canonical document builder.

Transforms canonical blocks into the provider-independent
Knowledge Factory canonical JSON structure.
"""

from datetime import datetime, timezone
import hashlib
import os


class CanonicalDocumentBuilder:
    """Build provider-independent canonical JSON from canonical blocks."""

    SCHEMA_VERSION = "1.0"

    def build(
        self,
        *,
        blocks: list,
        page_count: int,
        filename: str,
        raw_bucket: str,
        raw_object: str,
        generation: str | None,
        mime_type: str = "application/pdf",
        created_at: str | None = None,
    ) -> dict:
        """
        Build the canonical document object.

        The returned object contains only technology-independent data.
        """

        created_at = created_at or self._utc_now()
        document_id = self.create_document_id(
            raw_bucket=raw_bucket,
            raw_object=raw_object,
            generation=generation,
        )

        canonical_blocks = [
            self._build_block(block=block, index=index)
            for index, block in enumerate(blocks)
        ]

        page_count = self._page_count(page_count, canonical_blocks)
        pages = [
            {
                "page_number": page_number,
                "blocks": [],
            }
            for page_number in range(1, page_count + 1)
        ]

        for block in canonical_blocks:
            page_index = max(block["page"], 1) - 1
            if page_index >= len(pages):
                continue
            pages[page_index]["blocks"].append(block)

        return {
            "schema_version": self.SCHEMA_VERSION,
            "document": {
                "document_id": document_id,
                "filename": os.path.basename(filename),
                "mime_type": mime_type,
                "page_count": page_count,
                "created_at": created_at,
            },
            "pages": pages,
        }

    def create_document_id(
        self,
        *,
        raw_bucket: str,
        raw_object: str,
        generation: str | None,
    ) -> str:
        """Create a deterministic ID for a raw object generation."""

        source_key = f"{raw_bucket}/{raw_object}#{generation or 'latest'}"
        digest = hashlib.sha256(source_key.encode("utf-8")).hexdigest()
        return f"doc-{digest[:32]}"

    def _build_block(self, *, block: dict, index: int) -> dict:
        metadata = dict(block.get("metadata") or {})

        return {
            "id": f"block-{index + 1:06d}",
            "type": block["type"],
            "text": block.get("text") or "",
            "page": block.get("page") or 1,
            "confidence": block.get("confidence"),
            "bbox": block["bbox"],
            "metadata": metadata,
        }

    def _page_count(self, source_page_count: int, blocks: list[dict]) -> int:
        page_count = self._positive_int(source_page_count) or 0

        for block in blocks:
            page_count = max(page_count, int(block["page"]))
            page_span = block.get("metadata", {}).get("page_span", {})
            if page_span.get("end"):
                page_count = max(page_count, int(page_span["end"]))

        return max(page_count, 1)

    def _positive_int(self, value) -> int | None:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return None

        if parsed < 1:
            return None

        return parsed

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
