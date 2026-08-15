import json

from services.extractors.concept_extractor import (
    ConceptExtractor,
)


def test_concept_extractor_with_sparse_fixture():

    with open(
        "tests/fixtures/matrices_1_10_canonical.json",
        encoding="utf-8",
    ) as f:

        canonical = json.load(f)

    extractor = ConceptExtractor()

    result = extractor.extract(canonical)

    # The current 10-page fixture contains structural
    # headings but insufficient body content to
    # deterministically identify concepts.
    assert result == []
    
def test_concept_extractor_extracts_content():

    with open(
        "tests/fixtures/concept_extractor_sample.json",
        encoding="utf-8",
    ) as f:

        canonical = json.load(f)

    extractor = ConceptExtractor()

    result = extractor.extract(canonical)

    assert len(result) == 2

    assert result[0].name == (
        "A matrix is a rectangular arrangement of numbers."
    )

    assert result[0].section_number == "3.2"

    assert result[1].name == (
        "The order of a matrix describes its number of rows and columns."
    )

    assert result[1].section_number == "3.2"
    
