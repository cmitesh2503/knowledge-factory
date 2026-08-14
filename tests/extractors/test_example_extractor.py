import json

from services.extractors.example_extractor import (
    ExampleExtractor,
)


def test_example_extractor_with_sparse_fixture():

    with open(
        "tests/fixtures/matrices_1_10_canonical.json",
        encoding="utf-8",
    ) as f:

        canonical = json.load(f)

    extractor = ExampleExtractor()

    result = extractor.extract(canonical)

    # Current 10-page fixture contains structural
    # headings but no explicit worked-example markers.
    assert result == []
    
def test_example_extractor_extracts_examples():

    with open(
        "tests/fixtures/example_extractor_sample.json",
        encoding="utf-8",
    ) as f:

        canonical = json.load(f)

    extractor = ExampleExtractor()

    result = extractor.extract(canonical)

    assert len(result) == 2

    assert result[0].number == "3.1"
    assert result[0].section_number == "3.2"
    assert result[0].page == 1
    assert result[0].content == [
            "Find the order of the following matrix.",
            "The matrix has 2 rows and 3 columns.",
            "Therefore its order is 2 × 3.",
        ]
    assert result[1].content == [
            "Determine whether the two matrices are equal."
        ]

    assert result[1].number == "3.2"
    assert result[1].section_number == "3.2"
    assert result[1].page == 2