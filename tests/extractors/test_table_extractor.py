from services.extractors.table_extractor import (
    TableExtractor,
)


def test_table_extractor_extracts_tables():

    canonical_document = {
        "pages": [
            {
                "page_number": 2,
                "blocks": [
                    {
                        "id": "block-000082",
                        "type": "table",
                        "text": "",
                        "page": 2,
                        "metadata": {
                            "source": (
                                "azure_document_intelligence"
                            ),
                            "table_index": 0,
                            "row_count": 3,
                            "column_count": 6,
                            "cells": [
                                {
                                    "row_index": 0,
                                    "column_index": 0,
                                    "content": "Radha",
                                    "kind": None,
                                    "elements": [
                                        "/paragraphs/14"
                                    ],
                                }
                            ],
                        },
                    },
                    {
                        "id": "block-000083",
                        "type": "table",
                        "text": "",
                        "page": 2,
                        "metadata": {
                            "source": (
                                "azure_document_intelligence"
                            ),
                            "table_index": 1,
                            "row_count": 4,
                            "column_count": 3,
                            "cells": [
                                {
                                    "row_index": 0,
                                    "column_index": 1,
                                    "content": "Notebooks",
                                    "kind": "columnHeader",
                                    "elements": [
                                        "/paragraphs/33"
                                    ],
                                }
                            ],
                        },
                    },
                ],
            }
        ]
    }

    tables = TableExtractor().extract(
        canonical_document
    )

    assert len(tables) == 2

    assert tables[0].id == "block-000082"
    assert tables[0].rows == 3
    assert tables[0].columns == 6
    assert tables[0].cells[0]["content"] == "Radha"

    assert tables[1].id == "block-000083"
    assert tables[1].rows == 4
    assert tables[1].columns == 3
    assert (
        tables[1].cells[0]["kind"]
        == "columnHeader"
    )
    
def test_table_extractor_rejects_invalid_dimensions():

    canonical_document = {
        "pages": [
            {
                "page_number": 2,
                "blocks": [
                    {
                        "id": "table-invalid-1",
                        "type": "table",
                        "metadata": {
                            "row_count": 0,
                            "column_count": 3,
                            "cells": [],
                        },
                    },
                    {
                        "id": "table-invalid-2",
                        "type": "table",
                        "metadata": {
                            "row_count": 3,
                            "column_count": 0,
                            "cells": [],
                        },
                    },
                ],
            }
        ]
    }

    tables = TableExtractor().extract(
        canonical_document
    )

    assert tables == []
    
def test_table_extractor_preserves_sparse_and_empty_cells():

    canonical_document = {
        "pages": [
            {
                "page_number": 2,
                "blocks": [
                    {
                        "id": "table-sparse-1",
                        "type": "table",
                        "metadata": {
                            "row_count": 2,
                            "column_count": 3,
                            "cells": [
                                {
                                    "row_index": 0,
                                    "column_index": 0,
                                    "content": "Name",
                                    "kind": "columnHeader",
                                },
                                {
                                    "row_index": 0,
                                    "column_index": 1,
                                    "content": "",
                                    "kind": "columnHeader",
                                },
                                {
                                    "row_index": 1,
                                    "column_index": 0,
                                    "content": "Radha",
                                    "kind": None,
                                },
                            ],
                        },
                    }
                ],
            }
        ]
    }

    tables = TableExtractor().extract(
        canonical_document
    )

    assert len(tables) == 1

    table = tables[0]

    assert table.rows == 2
    assert table.columns == 3
    assert len(table.cells) == 3

    assert table.cells[1]["content"] == ""
    assert table.cells[1]["kind"] == "columnHeader"

    assert table.cells[2]["content"] == "Radha"
    
def test_table_extractor_preserves_identity_and_provenance():

    canonical_document = {
        "pages": [
            {
                "page_number": 2,
                "blocks": [
                    {
                        "id": "block-table-001",
                        "type": "table",
                        "metadata": {
                            "source": "azure_document_intelligence",
                            "table_index": 1,
                            "row_count": 4,
                            "column_count": 3,
                            "cells": [],
                        },
                    }
                ],
            }
        ]
    }

    tables = TableExtractor().extract(
        canonical_document
    )

    assert len(tables) == 1

    table = tables[0]

    assert table.id == "block-table-001"
    assert table.metadata["source"] == (
        "azure_document_intelligence"
    )
    assert table.metadata["table_index"] == 1
    assert table.metadata["page"] == 2