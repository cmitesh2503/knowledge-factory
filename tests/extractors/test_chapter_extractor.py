import json

from services.extractors.chapter_extractor import ChapterExtractor
from tests.validators.chapter_validator import ChapterValidator


def test_chapter_extractor():

    with open(
        "tests/fixtures/matrices_1_10_canonical.json",
        encoding="utf-8",
    ) as f:

        canonical = json.load(f)

    with open(
        "tests/fixtures/expected_chapter.json",
        encoding="utf-8",
    ) as f:

        expected = json.load(f)

    extractor = ChapterExtractor()

    result = extractor.extract(canonical)
    
    validator = ChapterValidator()

    errors = validator.validate(
        result.items,
        expected,
    )

    assert errors == []
    
def test_chapter_marker_does_not_require_heading_type():
    canonical = {
        "pages": [
            {
                "page_number": 1,
                "blocks": [
                    {
                        "id": "block-001",
                        "type": "text",
                        "text": "Chapter 3",
                    },
                    {
                        "id": "block-002",
                        "type": "heading",
                        "text": "MATRICES",
                    },
                ],
            }
        ]
    }

    result = ChapterExtractor().extract(canonical)

    assert len(result.items) == 1

    chapter = result.items[0]

    assert chapter.number == 3
    assert chapter.title == "Matrices"
    assert chapter.start_page == 1
    assert chapter.end_page == 1


def test_chapter_extractor_ignores_document_code_before_title():
    canonical = {
        "pages": [
            {
                "page_number": 1,
                "blocks": [
                    {
                        "id": "block-001",
                        "type": "text",
                        "text": "Chapter 3",
                    },
                    {
                        "id": "block-002",
                        "type": "text",
                        "text": "12079CH03",
                    },
                    {
                        "id": "block-003",
                        "type": "heading",
                        "text": "MATRICES",
                    },
                ],
            }
        ]
    }

    result = ChapterExtractor().extract(canonical)

    assert len(result.items) == 1
    assert result.items[0].number == 3
    assert result.items[0].title == "Matrices"


def test_chapter_extractor_does_not_use_section_as_title():
    canonical = {
        "pages": [
            {
                "page_number": 1,
                "blocks": [
                    {
                        "id": "block-001",
                        "type": "text",
                        "text": "Chapter 3",
                    },
                    {
                        "id": "block-002",
                        "type": "heading",
                        "text": "3.1 Introduction",
                    },
                ],
            }
        ]
    }

    result = ChapterExtractor().extract(canonical)

    assert result.items == []


def test_chapter_end_page_uses_document_page_count():
    canonical = {
        "pages": [
            {
                "page_number": 1,
                "blocks": [
                    {
                        "id": "block-001",
                        "type": "text",
                        "text": "Chapter 3",
                    },
                    {
                        "id": "block-002",
                        "type": "heading",
                        "text": "MATRICES",
                    },
                ],
            },
            {
                "page_number": 2,
                "blocks": [
                    {
                        "id": "block-003",
                        "type": "paragraph",
                        "text": "Matrix content",
                    }
                ],
            },
        ]
    }

    result = ChapterExtractor().extract(canonical)

    assert len(result.items) == 1

    chapter = result.items[0]

    assert chapter.start_page == 1
    assert chapter.end_page == 2