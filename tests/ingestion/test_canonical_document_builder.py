from functions.pdf_ingestion.canonical_document_builder import (
    CanonicalDocumentBuilder,
)


def test_canonical_builder_preserves_page_boundaries():

    blocks = [
        {
            "id": "block-001",
            "type": "paragraph",
            "text": "Page 1 content",
            "page": 1,
            "confidence": 0.99,
            "geometry": {},
            "metadata": {},
        },
        {
            "id": "block-002",
            "type": "paragraph",
            "text": "Page 2 content",
            "page": 2,
            "confidence": 0.99,
            "geometry": {},
            "metadata": {},
        },
        {
            "id": "block-003",
            "type": "paragraph",
            "text": "Page 4 content",
            "page": 4,
            "confidence": 0.99,
            "geometry": {},
            "metadata": {},
        },
    ]

    builder = CanonicalDocumentBuilder()

    result = builder.build(
        blocks=blocks,
        page_count=4,
        filename="test.pdf",
        raw_bucket="test-bucket",
        raw_object="test/document.pdf",
        generation="1",
    )

    assert len(result["pages"]) == 4

    assert result["pages"][0]["blocks"][0]["text"] == (
        "Page 1 content"
    )

    assert result["pages"][1]["blocks"][0]["text"] == (
        "Page 2 content"
    )

    assert result["pages"][2]["blocks"] == []

    assert result["pages"][3]["blocks"][0]["text"] == (
        "Page 4 content"
    )