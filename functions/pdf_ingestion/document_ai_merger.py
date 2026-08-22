"""
Merge persisted Google Document AI chunk results.

This module works only with already-persisted JSON artifacts.
It does NOT call Document AI.
"""

import json
from pathlib import Path
from typing import Any


class DocumentAIChunkMerger:
    """
    Merge Document AI chunk artifacts into one document representation.

    Chunk page spans are local to each chunk. The merger converts them
    into original-document page numbers.
    """

    def merge(
        self,
        chunk_files: list[str | Path],
        output_file: str | Path,
    ) -> Path:
        """
        Merge Document AI JSON chunk artifacts.

        Parameters
        ----------
        chunk_files:
            Ordered list of chunk JSON files.

        output_file:
            Destination for merged JSON.

        Returns
        -------
        Path
            Path to merged JSON artifact.
        """

        if not chunk_files:
            raise ValueError(
                "At least one chunk file is required."
            )

        chunks: list[dict[str, Any]] = []

        for chunk_file in chunk_files:

            path = Path(chunk_file)

            if not path.exists():
                raise FileNotFoundError(
                    f"Chunk artifact not found: {path}"
                )

            with path.open(
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            chunks.append(
                {
                    "path": path,
                    "data": data,
                }
            )

        merged_blocks: list[dict[str, Any]] = []

        chunk_metadata: list[dict[str, Any]] = []

        original_page_offset = 0

        for index, chunk in enumerate(chunks):

            path = chunk["path"]
            data = chunk["data"]

            document = data.get(
                "document",
                {},
            )

            layout = document.get(
                "document_layout",
                {},
            )

            blocks = layout.get(
                "blocks",
                [],
            )

            if not blocks:
                raise ValueError(
                    f"No layout blocks found in {path}"
                )

            # Determine the number of pages represented
            # by this chunk.
            chunk_page_end = 0

            for block in blocks:

                page_span = block.get(
                    "page_span"
                )

                if not page_span:
                    continue

                page_end = page_span.get(
                    "page_end",
                    0,
                )

                if page_end > chunk_page_end:
                    chunk_page_end = page_end

            if chunk_page_end <= 0:
                raise ValueError(
                    f"No valid page spans found in {path}"
                )

            chunk_original_start = (
                original_page_offset + 1
            )

            chunk_original_end = (
                original_page_offset
                + chunk_page_end
            )

            # Rebase every block's page span.
            for block in blocks:

                merged_block = dict(block)

                page_span = block.get(
                    "page_span"
                )

                if page_span:

                    merged_page_span = dict(
                        page_span
                    )

                    merged_page_span[
                        "page_start"
                    ] = (
                        page_span["page_start"]
                        + original_page_offset
                    )

                    merged_page_span[
                        "page_end"
                    ] = (
                        page_span["page_end"]
                        + original_page_offset
                    )

                    merged_block[
                        "page_span"
                    ] = merged_page_span

                merged_blocks.append(
                    merged_block
                )

            chunk_metadata.append(
                {
                    "chunk_number": index + 1,
                    "source_file": str(path),
                    "chunk_page_count": chunk_page_end,
                    "original_page_start": (
                        chunk_original_start
                    ),
                    "original_page_end": (
                        chunk_original_end
                    ),
                    "block_count": len(blocks),
                }
            )

            original_page_offset += (
                chunk_page_end
            )

        merged_document = {
            "document_layout": {
                "blocks": merged_blocks,
            },
        }

        merged_result = {
            "source": {
                "type": "gcp_document_ai_chunk_merge",
                "chunk_count": len(chunks),
                "original_page_count": (
                    original_page_offset
                ),
            },
            "chunks": chunk_metadata,
            "document": merged_document,
        }

        output_path = Path(
            output_file
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with output_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                merged_result,
                file,
                indent=2,
                ensure_ascii=False,
            )

        return output_path