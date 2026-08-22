"""
Adapter from merged Google Document AI JSON
to Knowledge Factory canonical blocks.

This module does not create the final canonical document.
It only converts provider-specific Document AI layout
blocks into the provider-independent canonical block shape.
"""

from pathlib import Path
import json


class DocumentAICanonicalAdapter:
    """Convert merged Document AI JSON into canonical blocks."""

    def load(self, input_file: str | Path) -> dict:
        """
        Load a merged Document AI JSON artifact.
        """

        input_path = Path(input_file)

        if not input_path.exists():
            raise FileNotFoundError(
                f"Document AI artifact not found: {input_path}"
            )

        return json.loads(
            input_path.read_text(
                encoding="utf-8"
            )
        )

    def extract_blocks(
        self,
        document_ai_json: dict,
    ) -> list[dict]:
        """
        Convert Document AI layout blocks into canonical blocks.
        """

        document = document_ai_json.get(
            "document",
            {}
        )

        layout = document.get(
            "document_layout",
            {}
        )

        provider_blocks = layout.get(
            "blocks",
            []
        )

        canonical_blocks = []

        for provider_block in provider_blocks:

            canonical_blocks.append(
                self._build_block(
                    provider_block
                )
            )

        return canonical_blocks

    def page_count(
        self,
        document_ai_json: dict,
    ) -> int:
        """
        Return original document page count.
        """

        source = document_ai_json.get(
            "source",
            {}
        )

        return int(
            source.get(
                "original_page_count",
                0,
            )
        )

    def _build_block(
        self,
        provider_block: dict,
    ) -> dict:
        """
        Convert one Document AI block.
        """

        block_type, text = (
            self._extract_content(
                provider_block
            )
        )

        page_span = provider_block.get(
            "page_span",
            {}
        )

        page_start = (
            page_span.get("page_start")
            or 1
        )

        page_end = (
            page_span.get("page_end")
            or page_start
        )

        metadata = {}

        if page_end != page_start:
            metadata["page_span"] = {
                "start": page_start,
                "end": page_end,
            }

        return {
            "type": self._normalize_type(
                block_type
            ),
            "text": text,
            "page": page_start,
            "confidence": None,
            "geometry": {},
            "metadata": metadata,
        }

    def _extract_content(
        self,
        block: dict,
    ) -> tuple[str, str]:

        text_block = block.get(
            "text_block"
        )

        if text_block is not None:

            return (
                text_block.get(
                    "type_"
                ),
                text_block.get(
                    "text",
                    "",
                ),
            )

        if "table_block" in block:
            return "table", ""

        if "list_block" in block:
            return "list", ""

        if "image_block" in block:
            return "image", ""

        return "text", ""

    def _normalize_type(
        self,
        provider_type: str | None,
    ) -> str:

        block_type = str(
            provider_type or ""
        ).strip().lower()

        if not block_type:
            return "text"

        heading_level = (
            block_type.removeprefix(
                "heading-"
            )
        )

        if (
            heading_level != block_type
            and heading_level.isdigit()
        ):
            return "heading"

        mapping = {
            "paragraph": "paragraph",
            "table": "table",
            "list": "list",
            "image": "image",
            "text": "text",
        }

        return mapping.get(
            block_type,
            "text",
        )