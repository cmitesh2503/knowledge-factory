import json
from pathlib import Path

from services.extractors.example_extractor import (
    ExampleExtractor,
)


FIXTURE = Path(
    "tests/fixtures/matrices_gcp_canonical.json"
)


def load_canonical_document() -> dict:
    return json.loads(
        FIXTURE.read_text(
            encoding="utf-8"
        )
    )


def test_real_matrices_examples_are_detected():

    document = load_canonical_document()

    examples = ExampleExtractor().extract(
        document
    )

    assert len(examples) == 6

    numbers = [
        example.number
        for example in examples
    ]

    assert numbers == [
        "20",
        "21",
        "22",
        "23",
        "24",
        "25",
    ]


def test_real_matrices_examples_have_metadata():

    document = load_canonical_document()

    examples = ExampleExtractor().extract(
        document
    )

    expected = {
        "20": {
            "section": "3.5.1",
            "page": 28,
        },
        "21": {
            "section": "3.5.1",
            "page": 30,
        },
        "22": {
            "section": "3.6",
            "page": 32,
        },
        "23": {
            "section": "3.7",
            "page": 37,
        },
        "24": {
            "section": "3.7",
            "page": 37,
        },
        "25": {
            "section": "3.7",
            "page": 38,
        },
    }

    for example in examples:

        expected_metadata = expected[
            example.number
        ]

        assert (
            example.section_number
            == expected_metadata["section"]
        )

        assert (
            example.page
            == expected_metadata["page"]
        )


def test_real_matrices_examples_have_content():

    document = load_canonical_document()

    examples = ExampleExtractor().extract(
        document
    )

    for example in examples:

        assert example.content

        combined = "\n".join(
            example.content
        )

        assert combined.strip()


def test_real_matrices_examples_preserve_solutions():

    document = load_canonical_document()

    examples = ExampleExtractor().extract(
        document
    )

    for example in examples:

        combined = "\n".join(
            example.content
        ).lower()

        assert (
            "solution" in combined
            or example.number == "20"
        )
