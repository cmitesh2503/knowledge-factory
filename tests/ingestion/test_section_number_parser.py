from services.extractors.section_number_parser import (
    SectionNumberParser,
)


def test_parses_section_without_period():

    result = SectionNumberParser.parse(
        "3.5 Transpose of a Matrix"
    )

    assert result is not None

    parsed, title = result

    assert parsed.number == "3.5"
    assert parsed.level == 1
    assert parsed.parent_number is None
    assert title == "Transpose of a Matrix"


def test_parses_section_with_period():

    result = SectionNumberParser.parse(
        "3.5. Transpose of a Matrix"
    )

    assert result is not None

    parsed, title = result

    assert parsed.number == "3.5"
    assert parsed.level == 1
    assert parsed.parent_number is None
    assert title == "Transpose of a Matrix"


def test_parses_nested_section_with_period():

    result = SectionNumberParser.parse(
        "3.5.1. Properties of transpose"
    )

    assert result is not None

    parsed, title = result

    assert parsed.number == "3.5.1"
    assert parsed.level == 2
    assert parsed.parent_number == "3.5"
    assert title == "Properties of transpose"


def test_parses_existing_nested_section():

    result = SectionNumberParser.parse(
        "3.2.1 Order of a matrix"
    )

    assert result is not None

    parsed, title = result

    assert parsed.number == "3.2.1"
    assert parsed.level == 2
    assert parsed.parent_number == "3.2"
    assert title == "Order of a matrix"