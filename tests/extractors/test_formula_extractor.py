import json

from services.extractors.formula_extractor import (
    FormulaExtractor,
)


def test_formula_extractor_with_sparse_fixture():

    with open(
        "tests/fixtures/matrices_1_10_canonical.json",
        encoding="utf-8",
    ) as f:

        canonical = json.load(f)

    extractor = FormulaExtractor()

    result = extractor.extract(canonical)

    # Current 10-page fixture contains section
    # headings but no reliable formula blocks.
    assert result == []
    
def test_formula_extractor_extracts_formulas():

    with open(
        "tests/fixtures/formula_extractor_sample.json",
        encoding="utf-8",
    ) as f:

        canonical = json.load(f)

    extractor = FormulaExtractor()

    result = extractor.extract(canonical)

    assert len(result) == 2

    assert result[0].expression == "A = B"
    assert result[0].section_number == "3.2"

    assert result[1].expression == "x + y = 10"
    assert result[1].section_number == "3.2"