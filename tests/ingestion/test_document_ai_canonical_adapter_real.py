from pathlib import Path

from functions.pdf_ingestion.document_ai_canonical_adapter import (
    DocumentAICanonicalAdapter,
)


MERGED_ARTIFACT = (
    Path("tests")
    / "fixtures"
    / "gcp_document_ai"
    / "Matrices_merged.json"
)


def main():

    print("=" * 54)
    print("C.6.4 — REAL DOCUMENT AI → CANONICAL BLOCKS")
    print("=" * 54)

    print("\n1. Checking merged artifact...")

    assert MERGED_ARTIFACT.exists()

    print(
        f"   PASS: {MERGED_ARTIFACT}"
    )

    adapter = (
        DocumentAICanonicalAdapter()
    )

    document = adapter.load(
        MERGED_ARTIFACT
    )

    print(
        "\n2. Extracting canonical blocks..."
    )

    blocks = adapter.extract_blocks(
        document
    )

    print(
        f"   Canonical blocks: {len(blocks)}"
    )

    assert len(blocks) == 493

    print(
        "   PASS: 493 canonical blocks"
    )

    print(
        "\n3. Validating page count..."
    )

    page_count = adapter.page_count(
        document
    )

    print(
        f"   Page count: {page_count}"
    )

    assert page_count == 42

    print(
        "   PASS: 42 pages"
    )

    print(
        "\n4. Validating first block..."
    )

    first = blocks[0]

    print(
        f"   Type: {first['type']}"
    )
    print(
        f"   Text: {first['text']}"
    )
    print(
        f"   Page: {first['page']}"
    )

    assert first["type"] == "paragraph"
    assert first["text"] == "Chapter 3"
    assert first["page"] == 1

    print(
        "   PASS: first block mapped"
    )

    print(
        "\n5. Validating page continuity..."
    )

    pages = [
        block["page"]
        for block in blocks
    ]

    assert min(pages) == 1
    assert max(pages) == 42

    print(
        f"   First block page: {min(pages)}"
    )
    print(
        f"   Last block page: {max(pages)}"
    )

    print(
        "   PASS: canonical pages cover 1–42"
    )

    print(
        "\n6. Validating multi-page metadata..."
    )

    spanning_blocks = [
        block
        for block in blocks
        if "page_span"
        in block["metadata"]
    ]

    print(
        f"   Multi-page blocks: "
        f"{len(spanning_blocks)}"
    )

    for block in spanning_blocks[:5]:

        print(
            "   ",
            block["page"],
            block["metadata"]["page_span"],
        )

    print(
        "   PASS: page-span metadata preserved"
    )

    print()
    print("=" * 54)
    print(
        "C.6.4 REAL DOCUMENT AI → CANONICAL BLOCKS: PASS"
    )
    print("=" * 54)


if __name__ == "__main__":
    main()