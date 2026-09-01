from services.models.knowledge_search_result import (
    KnowledgeSearchResult,
)
from services.retrieval.retrieval_context import (
    RetrievalContext,
)
from adapters.mathverse.knowledge_retrieval_adapter import (
    MathVerseKnowledgeRetrievalAdapter,
)


class FakeKnowledgeRetrievalService:
    """
    Test double for KnowledgeRetrievalService.
    """

    def __init__(
        self,
        results: list[KnowledgeSearchResult],
    ) -> None:

        self.results = results
        self.last_query = None
        self.last_limit = None

    def retrieve(
        self,
        query: str,
        limit: int = 10,
    ) -> RetrievalContext:

        self.last_query = query
        self.last_limit = limit

        return RetrievalContext(
            query=query,
            results=self.results,
        )


def test_mathverse_retrieval_adapter():

    retrieval_service = (
        FakeKnowledgeRetrievalService(
            results=[
                KnowledgeSearchResult(
                    document_id=(
                        "matrices-document"
                    ),
                    source_id="table-001",
                    knowledge_type="table",
                    text=(
                        "Name | Marks "
                        "Radha | 95"
                    ),
                    distance=0.12,
                    metadata={
                        "page": 2,
                        "table_id": "table-001",
                    },
                )
            ]
        )
    )

    adapter = (
        MathVerseKnowledgeRetrievalAdapter(
            knowledge_retrieval_service=(
                retrieval_service
            )
        )
    )

    response = adapter.retrieve(
        query="Who scored 95 marks?",
        limit=5,
    )

    assert (
        retrieval_service.last_query
        == "Who scored 95 marks?"
    )

    assert retrieval_service.last_limit == 5

    assert response["query"] == (
        "Who scored 95 marks?"
    )

    assert len(response["results"]) == 1

    result = response["results"][0]

    assert result["id"] == "table-001"

    assert result["type"] == "table"

    assert result["content"] == (
        "Name | Marks Radha | 95"
    )

    assert result["distance"] == 0.12

    assert (
        result["source"]["document_id"]
        == "matrices-document"
    )

    assert result["source"]["page"] == 2

    assert result["metadata"]["table_id"] == (
        "table-001"
    )


def test_mathverse_retrieval_adapter_returns_empty_results():

    retrieval_service = (
        FakeKnowledgeRetrievalService(
            results=[]
        )
    )

    adapter = (
        MathVerseKnowledgeRetrievalAdapter(
            knowledge_retrieval_service=(
                retrieval_service
            )
        )
    )

    response = adapter.retrieve(
        query="Unknown mathematics topic"
    )

    assert response["query"] == (
        "Unknown mathematics topic"
    )

    assert response["results"] == []


def test_mathverse_retrieval_adapter_preserves_provenance():

    retrieval_service = (
        FakeKnowledgeRetrievalService(
            results=[
                KnowledgeSearchResult(
                    document_id="document-001",
                    source_id="concept-001",
                    knowledge_type="concept",
                    text=(
                        "A matrix is a rectangular "
                        "arrangement of values."
                    ),
                    metadata={
                        "page": 4,
                        "section_number": "1.2",
                        "chapter_id": "chapter-001",
                    },
                )
            ]
        )
    )

    adapter = (
        MathVerseKnowledgeRetrievalAdapter(
            knowledge_retrieval_service=(
                retrieval_service
            )
        )
    )

    response = adapter.retrieve(
        query="What is a matrix?"
    )

    source = (
        response["results"][0]["source"]
    )

    assert source["document_id"] == (
        "document-001"
    )

    assert source["page"] == 4

    assert source["section_number"] == "1.2"

    assert source["chapter_id"] == (
        "chapter-001"
    )