"""
Canonical document builder.

Transforms extracted layout blocks into the provider-independent
Knowledge Factory canonical JSON structure.
"""

from datetime import datetime, timezone
import hashlib
import os


class CanonicalDocumentBuilder:
    """Build provider-independent canonical JSON from layout blocks."""

    SCHEMA_VERSION = "1.0"
    PROCESSOR = {
        "engine": "document-ai",
        "version": "v1",
        "type": "layout-parser",
    }

    def build(
        self,
        *,
        document,
        blocks: list,
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

        page_count = self._page_count(document, canonical_blocks)
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
                "processor": dict(self.PROCESSOR),
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

    def _build_block(self, *, block, index: int) -> dict:
        text_block = getattr(block, "text_block", None)
        page_start, page_end = self._page_span(block)

        metadata = {}
        if page_start and page_end and page_start != page_end:
            metadata["page_span"] = {
                "start": page_start,
                "end": page_end,
            }

        return {
            "id": f"block-{index + 1:06d}",
            "type": self._block_type(text_block),
            "text": self._block_text(text_block),
            "page": page_start or 1,
            "confidence": self._confidence(block),
            "bbox": self._bbox(block),
            "metadata": metadata,
        }

    def _page_count(self, document, blocks: list[dict]) -> int:
        page_count = len(getattr(document, "pages", []) or [])

        for block in blocks:
            page_count = max(page_count, int(block["page"]))
            page_span = block.get("metadata", {}).get("page_span", {})
            if page_span.get("end"):
                page_count = max(page_count, int(page_span["end"]))

        return max(page_count, 1)

    def _page_span(self, block) -> tuple[int | None, int | None]:
        page_span = getattr(block, "page_span", None)
        if not page_span:
            return None, None

        page_start = getattr(page_span, "page_start", None)
        page_end = getattr(page_span, "page_end", None)

        return self._positive_int(page_start), self._positive_int(page_end)

    def _block_type(self, text_block) -> str:
        if not text_block:
            return "text"

        block_type = getattr(text_block, "type_", None)
        if not block_type:
            return "text"

        return str(block_type).strip().lower() or "text"

    def _block_text(self, text_block) -> str:
        if not text_block:
            return ""

        text = getattr(text_block, "text", "")
        return str(text or "")

    def _confidence(self, block) -> float | None:
        confidence = getattr(block, "confidence", None)
        if confidence is None:
            return None

        try:
            return float(confidence)
        except (TypeError, ValueError):
            return None

    def _bbox(self, block) -> dict:
        layout = getattr(block, "layout", None)
        bounding_poly = None

        if layout:
            bounding_poly = getattr(layout, "bounding_poly", None)

        if not bounding_poly:
            bounding_poly = getattr(block, "bounding_poly", None)

        if not bounding_poly:
            return {}

        vertices = (
            getattr(bounding_poly, "normalized_vertices", None)
            or getattr(bounding_poly, "vertices", None)
            or []
        )

        points = []
        for vertex in vertices:
            point = {}
            x = getattr(vertex, "x", None)
            y = getattr(vertex, "y", None)

            if x is not None:
                point["x"] = float(x)
            if y is not None:
                point["y"] = float(y)

            if point:
                points.append(point)

        if not points:
            return {}

        return {
            "vertices": points,
        }

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
