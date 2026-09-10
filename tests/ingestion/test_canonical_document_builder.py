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

def test_canonical_builder_preserves_canonical_figure_contract():

    blocks = [
        {
            "id": "figure-source-001",
            "type": "figure",
            "text": "Figure 1",
            "page": 1,
            "confidence": 0.91,
            "geometry": {
                "bbox": [10, 20, 100, 120],
            },
            "metadata": {},
            "figure": {
                "id": "figure-001",
                "caption": "Triangle ABC",
                "description": "A triangle with labelled vertices.",
                "figure_type": "triangle",
                "related_concepts": [
                    "triangle",
                    "geometry",
                ],
                "labels": [
                    "A",
                    "B",
                    "C",
                ],
                "geometry": {
                    "coordinate_system": {
                        "type": "cartesian",
                    },
                    "elements": [
                        {
                            "type": "triangle",
                            "vertices": [
                                "A",
                                "B",
                                "C",
                            ],
                        },
                    ],
                },
                "rendering": {
                    "renderer": "mathverse",
                },
                "educational": {
                    "purpose": "explain_triangle",
                    "importance": "high",
                },
                "interaction": {
                    "modifiable": True,
                    "can_highlight": True,
                    "can_animate": True,
                },
                "provenance": {
                    "source": "document_ai",
                    "source_block_id": "figure-source-001",
                    "page": 1,
                    "provider": "google_document_ai",
                },
                "confidence": 0.91,
                "is_educationally_relevant": True,
                "metadata": {
                    "test": True,
                },
            },
        },
    ]

    builder = CanonicalDocumentBuilder()

    result = builder.build(
        blocks=blocks,
        page_count=1,
        filename="test.pdf",
        raw_bucket="test-bucket",
        raw_object="test/document.pdf",
        generation="1",
    )

    figure = result["pages"][0]["blocks"][0]["figure"]

    assert figure["id"] == "figure-001"
    assert figure["caption"] == "Triangle ABC"
    assert figure["description"] == (
        "A triangle with labelled vertices."
    )
    assert figure["figure_type"] == "triangle"

    assert figure["related_concepts"] == [
        "triangle",
        "geometry",
    ]

    assert figure["labels"] == [
        "A",
        "B",
        "C",
    ]

    assert figure["geometry"]["coordinate_system"]["type"] == (
        "cartesian"
    )

    assert figure["geometry"]["elements"][0]["type"] == (
        "triangle"
    )

    assert figure["rendering"]["renderer"] == "mathverse"

    assert figure["educational"]["purpose"] == (
        "explain_triangle"
    )

    assert figure["interaction"]["modifiable"] is True
    assert figure["interaction"]["can_highlight"] is True
    assert figure["interaction"]["can_animate"] is True

    assert figure["provenance"]["provider"] == (
        "google_document_ai"
    )

    assert figure["confidence"] == 0.91
    assert figure["is_educationally_relevant"] is True
    assert figure["metadata"]["test"] is True

    assert "kind" not in figure
    assert "relevance" not in figure
    assert "animation" not in figure
    assert "capabilities" not in figure