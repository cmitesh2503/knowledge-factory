import json
from pathlib import Path

from services.integration.knowledge_package_builder import (
    KnowledgePackageBuilder,
)
from services.models import KnowledgePackage
from services.validators.knowledge_package_validator import (
    KnowledgePackageValidator,
)


FIXTURE = Path(
    "tests/fixtures/matrices_gcp_canonical.json"
)


def load_canonical_document() -> dict:
    assert FIXTURE.exists(), (
        f"Canonical fixture not found: {FIXTURE}"
    )

    return json.loads(
        FIXTURE.read_text(
            encoding="utf-8"
        )
    )


def test_real_canonical_document_builds_knowledge_package():

    canonical = load_canonical_document()

    builder = KnowledgePackageBuilder()

    package = builder.build(
        canonical
    )

    assert isinstance(
        package,
        KnowledgePackage,
    )

    assert package.schema_version == "1.0"

    assert (
        package.document_id
        == canonical["document"]["document_id"]
    )

    assert len(package.chapters) == 1
    assert len(package.sections) == 10
    assert len(package.concepts) == 440
    assert len(package.formulas) == 77
    assert len(package.examples) == 6
    assert len(package.exercises) == 2
    assert len(package.figures) == 0
    
    assert [
        section.number
        for section in package.sections
    ] == [
        "3.1",
        "3.2",
        "3.2.1",
        "3.4",
        "3.4.1",
        "3.4.5",
        "3.5",
        "3.5.1",
        "3.6",
        "3.7",
    ]


def test_real_knowledge_package_passes_validation():

    canonical = load_canonical_document()

    package = KnowledgePackageBuilder().build(
        canonical
    )

    validator = KnowledgePackageValidator()

    errors = validator.validate(
        package
    )

    assert errors == [], (
        "KnowledgePackage validation failed:\n"
        + "\n".join(errors)
    )


def test_real_knowledge_package_preserves_examples():

    canonical = load_canonical_document()

    package = KnowledgePackageBuilder().build(
        canonical
    )

    assert len(package.examples) == 6

    numbers = [
        example.number
        for example in package.examples
    ]

    assert numbers == [
        "20",
        "21",
        "22",
        "23",
        "24",
        "25",
    ]

    for example in package.examples:

        assert example.id
        assert example.number
        assert example.block_id
        assert example.page >= 1
        assert example.section_number
        assert example.content


def test_real_knowledge_package_preserves_exercises():

    canonical = load_canonical_document()

    package = KnowledgePackageBuilder().build(
        canonical
    )

    assert len(package.exercises) == 2

    numbers = [
        exercise.number
        for exercise in package.exercises
    ]

    assert numbers == [
        "3.3",
        "3.4",
    ]

    for exercise in package.exercises:

        assert exercise.id
        assert exercise.number
        assert exercise.block_id
        assert exercise.page >= 1
        assert exercise.section_number
        assert exercise.questions

        for question in exercise.questions:

            assert question.block_id
            assert question.page >= 1
            assert question.question.strip()


def test_real_knowledge_package_round_trip():

    canonical = load_canonical_document()

    package = KnowledgePackageBuilder().build(
        canonical
    )

    serialized = package.to_dict()

    restored = KnowledgePackage.from_dict(
        serialized
    )

    assert (
        restored.to_dict()
        == serialized
    )
