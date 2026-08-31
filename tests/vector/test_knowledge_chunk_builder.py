from services.models import KnowledgePackage, Table, Concept
from services.vector.knowledge_chunk_builder import (
    KnowledgeChunkBuilder,
)


def test_knowledge_chunk_builder_builds_table_chunk():

    package = KnowledgePackage(
        schema_version="1.0",
        document_id="table-test-document",
        tables=[
            Table(
                id="table-001",
                rows=2,
                columns=2,
                cells=[
                    {
                        "row_index": 0,
                        "column_index": 0,
                        "content": "Name",
                        "kind": "columnHeader",
                    },
                    {
                        "row_index": 0,
                        "column_index": 1,
                        "content": "Marks",
                        "kind": "columnHeader",
                    },
                    {
                        "row_index": 1,
                        "column_index": 0,
                        "content": "Radha",
                        "kind": None,
                    },
                    {
                        "row_index": 1,
                        "column_index": 1,
                        "content": "95",
                        "kind": None,
                    },
                ],
                metadata={
                    "page": 2,
                    "table_index": 0,
                },
            )
        ],
    )

    chunks = KnowledgeChunkBuilder().build(
        package
    )

    assert len(chunks) == 1

    chunk = chunks[0]

    assert chunk["id"] == "table-001"
    assert chunk["knowledge_type"] == "table"

    assert (
        chunk["metadata"]["document_id"]
        == "table-test-document"
    )

    assert (
        chunk["metadata"]["table_id"]
        == "table-001"
    )

    assert chunk["metadata"]["page"] == 2
    assert chunk["metadata"]["rows"] == 2
    assert chunk["metadata"]["columns"] == 2

    assert "Name" in chunk["text"]
    assert "Marks" in chunk["text"]
    assert "Radha" in chunk["text"]
    assert "95" in chunk["text"]
    
def test_knowledge_chunk_builder_preserves_sparse_table_structure():

    package = KnowledgePackage(
        schema_version="1.0",
        document_id="sparse-table-document",
        tables=[
            Table(
                id="table-sparse-001",
                rows=2,
                columns=3,
                cells=[
                    {
                        "row_index": 0,
                        "column_index": 0,
                        "content": "Name",
                    },
                    {
                        "row_index": 0,
                        "column_index": 2,
                        "content": "Marks",
                    },
                    {
                        "row_index": 1,
                        "column_index": 0,
                        "content": "Radha",
                    },
                    {
                        "row_index": 1,
                        "column_index": 2,
                        "content": "95",
                    },
                ],
                metadata={
                    "page": 3,
                    "table_index": 1,
                },
            )
        ],
    )

    chunks = KnowledgeChunkBuilder().build(
        package
    )

    assert len(chunks) == 1

    chunk = chunks[0]

    assert chunk["knowledge_type"] == "table"

    assert (
        chunk["text"]
        == "Name |  | Marks\n"
        "Radha |  | 95"
    )

    assert chunk["metadata"]["rows"] == 2
    assert chunk["metadata"]["columns"] == 3
    
def test_knowledge_chunk_builder_keeps_tables_atomic():

    package = KnowledgePackage(
        schema_version="1.0",
        document_id="atomic-table-document",
        concepts=[
            Concept(
                id="concept-001",
                name="Matrix Addition",
                section_number="1.1",
                page=1,
                block_id="block-concept-001",
                metadata={
                    "description": (
                        "Matrix addition is performed by "
                        "adding corresponding elements from "
                        "two matrices of equal dimensions."
                    ),
                },
            )
        ],
        tables=[
            Table(
                id="table-001",
                rows=2,
                columns=2,
                cells=[
                    {
                        "row_index": 0,
                        "column_index": 0,
                        "content": "Name",
                    },
                    {
                        "row_index": 0,
                        "column_index": 1,
                        "content": "Marks",
                    },
                    {
                        "row_index": 1,
                        "column_index": 0,
                        "content": "Radha",
                    },
                    {
                        "row_index": 1,
                        "column_index": 1,
                        "content": "95",
                    },
                ],
                metadata={
                    "page": 1,
                    "table_index": 0,
                },
            )
        ],
    )

    chunks = KnowledgeChunkBuilder().build(
        package
    )

    assert len(chunks) == 2

    concept_chunk = next(
        chunk
        for chunk in chunks
        if chunk["knowledge_type"] == "concept"
    )

    table_chunk = next(
        chunk
        for chunk in chunks
        if chunk["knowledge_type"] == "table"
    )

    assert concept_chunk["id"] == "concept-001"

    assert table_chunk["id"] == "table-001"

    assert "Name | Marks" not in (
        concept_chunk["text"]
    )

    assert (
        "Matrix Addition"
        not in table_chunk["text"]
    )