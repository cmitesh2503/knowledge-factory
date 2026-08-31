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
    assert isinstance(
        package.tables,
        list,
    )

def test_knowledge_package_builder_preserves_tables():

    canonical = {
        "schema_version": "1.0",
        "document": {
            "document_id": "table-test-document",
        },
        "pages": [
            {
                "page_number": 1,
                "blocks": [
                    {
                        "id": "table-001",
                        "type": "table",
                        "metadata": {
                            "row_count": 2,
                            "column_count": 2,
                            "cells": [
                                {
                                    "row_index": 0,
                                    "column_index": 0,
                                    "text": "A",
                                },
                                {
                                    "row_index": 0,
                                    "column_index": 1,
                                    "text": "B",
                                },
                                {
                                    "row_index": 1,
                                    "column_index": 0,
                                    "text": "1",
                                },
                                {
                                    "row_index": 1,
                                    "column_index": 1,
                                    "text": "2",
                                },
                            ],
                        },
                    },
                ],
            },
        ],
    }

    package = KnowledgePackageBuilder().build(
        canonical
    )

    assert len(package.tables) == 1

    table = package.tables[0]

    assert table.id == "table-001"
    assert table.rows == 2
    assert table.columns == 2
    assert len(table.cells) == 4

    assert table.metadata["page"] == 1