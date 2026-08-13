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