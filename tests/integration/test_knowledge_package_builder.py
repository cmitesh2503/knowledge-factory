import json

from services.integration.knowledge_package_builder import (
    KnowledgePackageBuilder,
)


def test_knowledge_package_builder():

    with open(
        "tests/fixtures/matrices_1_10_canonical.json",
        encoding="utf-8",
    ) as f:

        canonical = json.load(f)

    builder = KnowledgePackageBuilder()

    package = builder.build(canonical)

    assert package.schema_version == "1.0"

    assert (
        package.document_id
        == "doc-bfd1b2df3ab6a13aa5759382812bc303"
    )

    assert len(package.chapters) == 1

    assert len(package.sections) == 5

    # The current 10-page fixture contains
    # structural information but insufficient
    # semantic content for concepts/formulas/examples/
    # exercises.
    assert package.concepts == []
    assert package.formulas == []
    assert package.examples == []
    assert package.exercises == []