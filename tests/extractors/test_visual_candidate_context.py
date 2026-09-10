from services.extractors.visual_candidate_context import (
    VisualCandidateContextBuilder,
)
from services.extractors.visual_region_detector import VisualRegion


def _region(
    *,
    region_id="visual-region-1",
    page_number=1,
    bbox=(100, 200, 300, 400),
    source_types=None,
    metadata=None,
):
    return VisualRegion(
        id=region_id,
        page_number=page_number,
        bbox=bbox,
        source_types=source_types or ["drawing"],
        image_count=0,
        drawing_count=1,
        metadata=metadata or {
            "repeated": False,
            "region_role": "localized_visual_candidate",
        },
    )


def test_build_preserves_visual_region_identity():
    region = _region()

    document = {
        "pages": [
            {
                "page_number": 1,
                "blocks": [],
            }
        ]
    }

    result = VisualCandidateContextBuilder().build(
        [region],
        document,
    )

    assert len(result) == 1
    assert result[0].id == "visual-region-1"
    assert result[0].page_number == 1
    assert result[0].bbox == (100.0, 200.0, 300.0, 400.0)


def test_build_collects_nearby_text():
    region = _region()

    document = {
        "pages": [
            {
                "page_number": 1,
                "blocks": [
                    {
                        "id": "text-1",
                        "type": "text",
                        "text": "Consider triangle ABC.",
                        "bbox": [100, 150, 300, 180],
                    },
                    {
                        "id": "text-2",
                        "type": "text",
                        "text": "AB = 5 cm.",
                        "bbox": [100, 420, 300, 450],
                    },
                ],
            }
        ]
    }

    result = VisualCandidateContextBuilder().build(
        [region],
        document,
    )

    context = result[0]

    assert "Consider triangle ABC." in context.nearby_text
    assert "AB = 5 cm." in context.nearby_text
    assert context.evidence["has_nearby_text"] is True


def test_build_detects_caption():
    region = _region(
        bbox=(100, 200, 300, 400),
    )

    document = {
        "pages": [
            {
                "page_number": 1,
                "blocks": [
                    {
                        "id": "caption-1",
                        "type": "text",
                        "text": "Figure 2.1: Triangle ABC",
                        "bbox": [100, 410, 300, 440],
                    }
                ],
            }
        ]
    }

    result = VisualCandidateContextBuilder().build(
        [region],
        document,
    )

    context = result[0]

    assert context.caption == "Figure 2.1: Triangle ABC"
    assert context.evidence["has_caption"] is True


def test_uncaptioned_region_is_retained():
    region = _region()

    document = {
        "pages": [
            {
                "page_number": 1,
                "blocks": [
                    {
                        "id": "text-1",
                        "type": "text",
                        "text": "The following diagram illustrates the concept.",
                        "bbox": [100, 150, 300, 180],
                    }
                ],
            }
        ]
    }

    result = VisualCandidateContextBuilder().build(
        [region],
        document,
    )

    context = result[0]

    assert context.caption is None
    assert context.id == region.id


def test_repeated_region_is_preserved():
    region = _region(
        metadata={
            "repeated": True,
            "region_role": "repeated_structural_region",
        }
    )

    document = {
        "pages": [
            {
                "page_number": 1,
                "blocks": [],
            }
        ]
    }

    result = VisualCandidateContextBuilder().build(
        [region],
        document,
    )

    context = result[0]

    assert context.repeated is True
    assert context.region_role == "repeated_structural_region"
    assert context.evidence["is_repeated"] is True
    assert context.evidence["is_localized"] is False


def test_localized_region_is_marked_as_localized():
    region = _region(
        metadata={
            "repeated": False,
            "region_role": "localized_visual_candidate",
        }
    )

    document = {
        "pages": [
            {
                "page_number": 1,
                "blocks": [],
            }
        ]
    }

    context = VisualCandidateContextBuilder().build_one(
        region,
        document,
    )

    assert context.evidence["is_localized"] is True
    assert context.repeated is False


def test_missing_page_context_does_not_fail():
    region = _region(page_number=99)

    document = {
        "pages": []
    }

    context = VisualCandidateContextBuilder().build_one(
        region,
        document,
    )

    assert context.id == region.id
    assert context.page_number == 99
    assert context.nearby_text == []
    assert context.caption is None
    assert context.evidence["page_context_available"] is False


def test_document_order_fallback_without_bboxes():
    region = _region()

    document = {
        "pages": [
            {
                "page_number": 1,
                "blocks": [
                    {
                        "id": "text-1",
                        "type": "text",
                        "text": "Introduction to the diagram.",
                    },
                    {
                        "id": "text-2",
                        "type": "text",
                        "text": "The angle is 30 degrees.",
                    },
                ],
            }
        ]
    }

    context = VisualCandidateContextBuilder().build_one(
        region,
        document,
    )

    assert context.nearby_text == [
        "Introduction to the diagram.",
        "The angle is 30 degrees.",
    ]

    assert context.evidence["has_nearby_text"] is True
    assert context.evidence["has_spatial_context"] is False


def test_to_dict_is_json_friendly():
    region = _region()

    document = {
        "pages": [
            {
                "page_number": 1,
                "blocks": [],
            }
        ]
    }

    context = VisualCandidateContextBuilder().build_one(
        region,
        document,
    )

    data = context.to_dict()

    assert data["id"] == region.id
    assert data["page_number"] == 1
    assert data["bbox"] == [100.0, 200.0, 300.0, 400.0]
    assert isinstance(data["evidence"], dict)
    assert isinstance(data["provenance"], dict)