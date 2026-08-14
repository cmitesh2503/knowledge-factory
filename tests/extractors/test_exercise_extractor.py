import json

from services.extractors.exercise_extractor import (
    ExerciseExtractor,
)


def test_exercise_extractor_with_sparse_fixture():

    with open(
        "tests/fixtures/matrices_1_10_canonical.json",
        encoding="utf-8",
    ) as f:

        canonical = json.load(f)

    extractor = ExerciseExtractor()

    result = extractor.extract(canonical)

    # Current 10-page fixture contains structural
    # headings but no explicit exercise markers.
    assert result == []
    
def test_exercise_extractor_extracts_questions():

    with open(
        "tests/fixtures/exercise_extractor_sample.json",
        encoding="utf-8",
    ) as f:

        canonical = json.load(f)

    extractor = ExerciseExtractor()

    result = extractor.extract(canonical)

    
    assert len(result) == 1

    assert result[0].number == "3.1"
    assert result[0].section_number == "3.2"

    assert len(result[0].questions) == 2

    assert result[0].questions[0].number == "1"
    assert result[0].questions[0].question == (
        "Find the order of the matrix."
    )

    assert result[0].questions[1].number == "2"
    assert result[0].questions[1].question == (
        "Determine whether the matrices are equal."
    )