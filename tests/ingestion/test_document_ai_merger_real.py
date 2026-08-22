import json
from pathlib import Path

from functions.pdf_ingestion.document_ai_merger import (
    DocumentAIChunkMerger,
)


FIXTURE_DIR = (
    Path("tests")
    / "fixtures"
    / "gcp_document_ai"
)

OUTPUT_FILE = (
    FIXTURE_DIR
    / "Matrices_merged.json"
)


def main():

    print(
        "======================================================"
    )
    print(
        "C.6.3 — REAL DOCUMENT AI CHUNK MERGE"
    )
    print(
        "======================================================"
    )

    chunk_1 = (
        FIXTURE_DIR
        / "Matrices_chunk_001.json"
    )

    chunk_2 = (
        FIXTURE_DIR
        / "Matrices_chunk_002.json"
    )

    print(
        "\n1. Checking chunk artifacts..."
    )

    assert chunk_1.exists(), (
        f"Missing: {chunk_1}"
    )

    assert chunk_2.exists(), (
        f"Missing: {chunk_2}"
    )

    print(
        "   PASS: both chunk artifacts exist"
    )

    print(
        "\n2. Merging saved Document AI results..."
    )

    merger = DocumentAIChunkMerger()

    merged_file = merger.merge(
        [
            chunk_1,
            chunk_2,
        ],
        OUTPUT_FILE,
    )

    print(
        "   PASS: merged artifact created:"
    )
    print(
        f"      {merged_file}"
    )

    print(
        "\n3. Validating merged document..."
    )

    data = json.loads(
        merged_file.read_text(
            encoding="utf-8"
        )
    )

    assert (
        data["source"]["chunk_count"]
        == 2
    )

    assert (
        data["source"]["original_page_count"]
        == 42
    )

    print(
        "   PASS: total page count = 42"
    )

    blocks = (
        data
        ["document"]
        ["document_layout"]
        ["blocks"]
    )

    assert blocks

    print(
        f"   PASS: merged blocks = {len(blocks)}"
    )

    print(
        "\n4. Validating page spans..."
    )

    page_starts = []
    page_ends = []

    for block in blocks:

        page_span = block.get(
            "page_span"
        )

        if not page_span:
            continue

        page_starts.append(
            page_span["page_start"]
        )

        page_ends.append(
            page_span["page_end"]
        )

    assert page_starts
    assert page_ends

    print(
        f"   First page span: "
        f"{min(page_starts)}"
    )

    print(
        f"   Last page span: "
        f"{max(page_ends)}"
    )

    assert min(page_starts) == 1
    assert max(page_ends) == 42

    print(
        "   PASS: merged page spans cover 1–42"
    )

    print(
        "\n5. Validating chunk boundaries..."
    )

    chunk_1_end = None
    chunk_2_start = None

    for block in blocks:

        page_span = block.get(
            "page_span"
        )

        if not page_span:
            continue

        page_start = (
            page_span["page_start"]
        )

        page_end = (
            page_span["page_end"]
        )

        if page_end <= 25:

            chunk_1_end = max(
                chunk_1_end or 0,
                page_end,
            )

        if page_start >= 26:

            chunk_2_start = min(
                chunk_2_start or 9999,
                page_start,
            )

    assert chunk_1_end == 25
    assert chunk_2_start == 26

    print(
        "   PASS: chunk boundary is 25 → 26"
    )

    print(
        "\n6. Checking extracted text..."
    )

    text_blocks = []

    for block in blocks:

        text_block = block.get(
            "text_block"
        )

        if not text_block:
            continue

        text = text_block.get(
            "text",
            "",
        )

        if text.strip():

            text_blocks.append(
                text
            )

    combined_text = "\n".join(
        text_blocks
    )

    assert combined_text.strip()

    print(
        "   PASS: extracted text present"
    )

    print(
        f"   Combined text length: "
        f"{len(combined_text)}"
    )

    print(
        "\n======================================================"
    )

    print(
        "C.6.3 REAL DOCUMENT AI CHUNK MERGE: PASS"
    )

    print(
        "======================================================"
    )


if __name__ == "__main__":
    main()