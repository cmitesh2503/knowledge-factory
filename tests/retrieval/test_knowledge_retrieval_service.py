from services.models.knowledge_search_result import (
    KnowledgeSearchResult,
)
from services.retrieval.knowledge_retrieval_service import (
    KnowledgeRetrievalService,
)


class FakeKnowledgeSearchService:
    """
    Deterministic fake used to test the retrieval
    boundary without vector infrastructure.
    """

    def __init__(self) -> None:

        self.received_query: str | None = None
        self.received_limit: int | None = None

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[KnowledgeSearchResult]:

        self.received_query = query
        self.received_limit = limit

        return [
            KnowledgeSearchResult(
                document_id="matrices-document",
                source_id="concept-001",
                knowledge_type="concept",
                text=(
                    "A matrix is a rectangular "
                    "arrangement of numbers."
                ),
                distance=0.12,
                metadata={
                    "section_number": "1.1",
                    "page": 1,
                },
            )
        ]


def test_knowledge_retrieval_service_returns_context():

    search_service = (
        FakeKnowledgeSearchService()
    )

    retrieval_service = (
        KnowledgeRetrievalService(
            knowledge_search_service=search_service
        )
    )

    context = retrieval_service.retrieve(
        query="What is a matrix?",
        limit=5,
    )

    assert context.query == "What is a matrix?"

    assert context.is_empty() is False

    assert len(context.results) == 1

    result = context.results[0]

    assert result.document_id == (
        "matrices-document"
    )

    assert result.source_id == "concept-001"

    assert result.knowledge_type == "concept"

    assert search_service.received_query == (
        "What is a matrix?"
    )

    assert search_service.received_limit == 5