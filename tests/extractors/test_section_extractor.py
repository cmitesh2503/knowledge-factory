import json

from services.extractors.section_extractor import (
    SectionExtractor,
)


def test_section_extractor():

    with open(
        "tests/fixtures/matrices_1_10_canonical.json",
        encoding="utf-8",
    ) as f:

        canonical = json.load(f)

    extractor = SectionExtractor()

    result = extractor.extract(canonical)

    assert len(result) == 5

    # 3.1
    assert result[0].number == "3.1"
    assert result[0].title == "Introduction"
    assert result[0].level == 1
    assert result[0].parent_number is None

    # 3.2
    assert result[1].number == "3.2"
    assert result[1].title == "Matrix"
    assert result[1].level == 1
    assert result[1].parent_number is None

    # 3.2.1
    assert result[2].number == "3.2.1"
    assert result[2].title == "Order of a matrix"
    assert result[2].level == 2
    assert result[2].parent_number == "3.2"

    # 3.4
    assert result[3].number == "3.4"
    assert result[3].title == "Operations on Matrices"
    assert result[3].level == 1
    assert result[3].parent_number is None

    # 3.4.1
    assert result[4].number == "3.4.1"
    assert result[4].title == "Addition of matrices"
    assert result[4].level == 2
    assert result[4].parent_number == "3.4"