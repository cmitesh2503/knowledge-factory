from services.models import (
    KnowledgePackage,
    Table,
)
from services.vector.embedding_provider import (
    EmbeddingProvider,
)
from services.vector.vector_index import (
    VectorIndex,
)
from services.vector.vector_indexing_service import (
    VectorIndexingService,
)


class FakeEmbeddingProvider(
    EmbeddingProvider,
):

    def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        return [
            [0.1, 0.2, 0.3]
            for _ in texts
        ]


class FakeVectorIndex(
    VectorIndex,
):

    def __init__(self) -> None:

        self.records = []

    def upsert(
        self,
        records,
    ) -> None:

        self.records.extend(
            records
        )

    def search(
        self,
        vector,
        limit=10,
    ):

        return []
    
def test_vector_indexing_service_indexes_chunks():

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
                    "page": 2,
                },
            )
        ],
    )

    embedding_provider = (
        FakeEmbeddingProvider()
    )

    vector_index = FakeVectorIndex()

    service = VectorIndexingService(
        embedding_provider=embedding_provider,
        vector_index=vector_index,
    )

    count = service.index(
        package
    )

    assert count == 1

    assert len(
        vector_index.records
    ) == 1

    record = vector_index.records[0]

    assert record["id"] == (
        "table-001"
    )

    assert record["knowledge_type"] == (
        "table"
    )

    assert record["vector"] == [
        0.1,
        0.2,
        0.3,
    ]