from extraction_quality import (
    ExtractionQualityEvaluator,
)


def test_rejects_sparse_extraction():

    evaluator = (
        ExtractionQualityEvaluator()
    )

    blocks = [
        {
            "type": "paragraph",
            "text": "Chapter 2",
            "page": 1,
        },
        {
            "type": "heading",
            "text": (
                "INVERSE TRIGONOMETRIC FUNCTIONS"
            ),
            "page": 1,
        },
        {
            "type": "heading",
            "text": "Historical Note",
            "page": 16,
        },
    ]

    result = evaluator.evaluate(
        blocks=blocks,
        page_count=16,
    )

    assert (
        result.is_acceptable is False
    )

    assert (
        result.pages_with_content == 2
    )