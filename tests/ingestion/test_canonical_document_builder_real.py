import json
from pathlib import Path

from functions.pdf_ingestion.canonical_document_builder import (
    CanonicalDocumentBuilder,
)
from functions.pdf_ingestion.document_ai_canonical_adapter import (
    DocumentAICanonicalAdapter,
)


MERGED_ARTIFACT = (
    Path("tests")
    / "fixtures"
    / "gcp_document_ai"
    / "Matrices_merged.json"
)

OUTPUT = (
    Path("tests")
    / "fixtures"
    / "matrices_gcp_canonical.json"
)


def main():
    print("=" * 54)
    print("C.6.5 — REAL DOCUMENT AI → CANONICAL DOCUMENT")
    print("=" * 54)

    # --------------------------------------------------
    # 1. Check merged artifact
    # --------------------------------------------------

    print("\n1. Checking merged Document AI artifact...")

    assert MERGED_ARTIFACT.exists(), (
        f"Missing artifact: {MERGED_ARTIFACT}"
    )

    print(f"   PASS: {MERGED_ARTIFACT}")

    # --------------------------------------------------
    # 2. Load merged artifact
    # --------------------------------------------------

    print("\n2. Loading merged artifact...")

    adapter = DocumentAICanonicalAdapter()

    document_ai_json = adapter.load(
        MERGED_ARTIFACT
    )

    print("   PASS: artifact loaded")

    # --------------------------------------------------
    # 3. Extract canonical blocks
    # --------------------------------------------------

    print("\n3. Adapting Document AI blocks...")

    canonical_blocks = adapter.extract_blocks(
        document_ai_json
    )

    print(
        f"   Canonical blocks: {len(canonical_blocks)}"
    )

    assert len(canonical_blocks) == 493

    print(
        "   PASS: 493 canonical blocks"
    )

    # --------------------------------------------------
    # 4. Determine page count
    # --------------------------------------------------

    print("\n4. Reading original page count...")

    page_count = adapter.page_count(
        document_ai_json
    )

    print(
        f"   Page count: {page_count}"
    )

    assert page_count == 42

    print(
        "   PASS: 42 pages"
    )
  
    
    # --------------------------------------------------
    # 4. Build canonical document
    # --------------------------------------------------

    print("\n5. Building canonical document...")

    builder = CanonicalDocumentBuilder()

    canonical_document = builder.build(
        blocks=canonical_blocks,
        page_count=42,
        filename="Matrices.pdf",
        raw_bucket="knowledge-factory-prod-raw",
        raw_object="test/Matrices.pdf",
        generation="fixture",
    )

    print("   PASS: canonical document built")

    # --------------------------------------------------
    # 5. Validate schema
    # --------------------------------------------------

    print("\n6. Validating canonical schema...")

    assert canonical_document["schema_version"] == "1.0"

    assert (
        canonical_document["document"]["filename"]
        == "Matrices.pdf"
    )

    assert (
        canonical_document["document"]["mime_type"]
        == "application/pdf"
    )

    assert (
        canonical_document["document"]["page_count"]
        == 42
    )

    assert len(
        canonical_document["pages"]
    ) == 42

    print("   PASS: schema structure valid")

    # --------------------------------------------------
    # 6. Validate page numbering
    # --------------------------------------------------

    print("\n7. Validating page numbering...")

    page_numbers = [
        page["page_number"]
        for page in canonical_document["pages"]
    ]

    assert page_numbers == list(
        range(1, 43)
    )

    print("   PASS: pages cover 1–42")

    # --------------------------------------------------
    # 7. Validate first block
    # --------------------------------------------------

    print("\n8. Validating first canonical block...")

    first_page_blocks = (
        canonical_document["pages"][0]["blocks"]
    )

    assert first_page_blocks

    first_block = first_page_blocks[0]

    print(
        f"   Type: {first_block['type']}"
    )

    print(
        f"   Text: {first_block['text']}"
    )

    print(
        f"   Page: {first_block['page']}"
    )

    assert first_block["id"] == "block-000001"
    assert first_block["type"] == "paragraph"
    assert first_block["text"] == "Chapter 3"
    assert first_block["page"] == 1

    print("   PASS: first block valid")

    # --------------------------------------------------
    # 8. Validate total blocks
    # --------------------------------------------------

    print("\n9. Validating total canonical blocks...")

    total_blocks = sum(
        len(page["blocks"])
        for page in canonical_document["pages"]
    )

    print(
        f"   Total blocks: {total_blocks}"
    )

    assert total_blocks == 493

    print(
        "   PASS: 493 blocks preserved"
    )

    # --------------------------------------------------
    # 9. Validate block IDs
    # --------------------------------------------------

    print("\n10. Validating canonical block IDs...")

    all_blocks = [
        block
        for page in canonical_document["pages"]
        for block in page["blocks"]
    ]

    assert all_blocks[0]["id"] == "block-000001"
    assert all_blocks[-1]["id"] == "block-000493"

    assert len(
        {
            block["id"]
            for block in all_blocks
        }
    ) == 493

    print(
        "   PASS: block IDs are unique and sequential"
    )

    # --------------------------------------------------
    # 10. Validate output
    # --------------------------------------------------

    print("\n11. Saving canonical fixture...")

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            canonical_document,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    assert OUTPUT.exists()

    print(
        f"   PASS: saved {OUTPUT}"
    )

    # --------------------------------------------------
    # 11. Reload and verify
    # --------------------------------------------------

    print("\n12. Reloading saved canonical fixture...")

    saved = json.loads(
        OUTPUT.read_text(
            encoding="utf-8"
        )
    )

    assert (
        saved["schema_version"]
        == "1.0"
    )

    assert (
        saved["document"]["page_count"]
        == 42
    )

    assert len(
        saved["pages"]
    ) == 42

    print(
        "   PASS: saved artifact reloads correctly"
    )

    print("\n" + "=" * 54)
    print(
        "C.6.5 REAL DOCUMENT AI → CANONICAL DOCUMENT: PASS"
    )
    print("=" * 54)


if __name__ == "__main__":
    main()