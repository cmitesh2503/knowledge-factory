from services.vector.embedding_provider import (
    EmbeddingProvider,
)
from services.vector.vector_index import (
    VectorIndex,
)
from services.vector.knowledge_search_service import (
    KnowledgeSearchService,
)


class FakeEmbeddingProvider(
    EmbeddingProvider,
):

    def __init__(self) -> None:

        self.texts = []

    def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        self.texts.extend(texts)

        return [
            [0.1, 0.2, 0.3]
            for _ in texts
        ]


class FakeVectorIndex(
    VectorIndex,
):

    def __init__(self) -> None:

        self.vector = None
        self.limit = None

    def upsert(
        self,
        records,
    ) -> None:

        pass

    def search(
        self,
        vector,
        limit=10,
    ):

        self.vector = vector
        self.limit = limit

        return [
            {
                "id": "table-001",
                "knowledge_type": "table",
                "text": (
                    "Name | Marks "
                    "Radha | 95"
                ),
                "distance": 0.12,
                "metadata": {
                    "document_id": (
                        "document-001"
                    ),
                    "page": 2,
                    "table_id": "table-001",
                },
            }
        ]


def test_knowledge_search_service():

    embedding_provider = (
        FakeEmbeddingProvider()
    )

    vector_index = FakeVectorIndex()

    service = KnowledgeSearchService(
        embedding_provider=embedding_provider,
        vector_index=vector_index,
    )

    results = service.search(
        query="What marks did Radha get?",
        limit=5,
    )

    assert (
        embedding_provider.texts
        == [
            "What marks did Radha get?"
        ]
    )

    assert vector_index.vector == [
        0.1,
        0.2,
        0.3,
    ]

    assert vector_index.limit == 5

    assert len(results) == 1

    result = results[0]

    assert result.document_id == (
        "document-001"
    )

    assert result.source_id == (
        "table-001"
    )

    assert result.knowledge_type == (
        "table"
    )

    assert result.text == (
        "Name | Marks Radha | 95"
    )

    assert result.distance == 0.12

    assert result.metadata["page"] == 2
    
def test_knowledge_search_service_rejects_empty_query():

    embedding_provider = (
        FakeEmbeddingProvider()
    )

    vector_index = FakeVectorIndex()

    service = KnowledgeSearchService(
        embedding_provider=embedding_provider,
        vector_index=vector_index,
    )

    results = service.search(
        query="   ",
    )

    assert results == []

    assert embedding_provider.texts == []
    
class InvalidQueryEmbeddingProvider(
    EmbeddingProvider,
):

    def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        return [
            [0.1, 0.2],
            [0.3, 0.4],
        ]


def test_knowledge_search_service_rejects_multiple_query_embeddings():

    service = KnowledgeSearchService(
        embedding_provider=(
            InvalidQueryEmbeddingProvider()
        ),
        vector_index=FakeVectorIndex(),
    )

    try:
        service.search(
            query="test query",
        )

        assert False, (
            "Expected ValueError."
        )

    except ValueError as error:

        assert (
            "exactly one embedding"
            in str(error)
        )