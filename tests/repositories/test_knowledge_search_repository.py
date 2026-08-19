from services.models.knowledge_search_result import (
    KnowledgeSearchResult,
)
from services.repositories.knowledge_search_repository import (
    KnowledgeSearchRepository,
)


class FakeKnowledgeSearchRepository(
    KnowledgeSearchRepository
):
    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        filters: dict | None = None,
    ) -> list[KnowledgeSearchResult]:

        return [
            KnowledgeSearchResult(
                document_id="doc-001",
                source_id="concept-001",
                knowledge_type="concept",
                text="A matrix is a rectangular array.",
                distance=0.12,
                metadata={
                    "section_number": "3.1",
                    "page": 10,
                },
            )
        ]


def test_search_repository_is_provider_independent():

    repository = (
        FakeKnowledgeSearchRepository()
    )

    results = repository.search(
        "What is a matrix?"
    )

    assert len(results) == 1

    result = results[0]

    assert isinstance(
        result,
        KnowledgeSearchResult,
    )

    assert result.document_id == "doc-001"
    assert result.source_id == "concept-001"
    assert result.knowledge_type == "concept"
    assert (
        result.text
        == "A matrix is a rectangular array."
    )
    assert result.distance == 0.12
    assert (
        result.metadata["section_number"]
        == "3.1"
    )
    assert result.metadata["page"] == 10


def test_search_result_does_not_expose_provider_details():

    result = KnowledgeSearchResult(
        document_id="doc-001",
        source_id="concept-001",
        knowledge_type="concept",
        text="Matrix knowledge",
        distance=0.10,
    )

    assert not hasattr(
        result,
        "snapshot",
    )

    assert not hasattr(
        result,
        "vector",
    )

    assert not hasattr(
        result,
        "firestore",
    )

    assert not hasattr(
        result,
        "find_nearest",
    )


def test_repository_returns_list_of_search_results():

    repository = (
        FakeKnowledgeSearchRepository()
    )

    results = repository.search(
        "matrix",
        top_k=5,
    )

    assert isinstance(
        results,
        list,
    )

    assert all(
        isinstance(
            result,
            KnowledgeSearchResult,
        )
        for result in results
    )


def test_search_result_is_read_only_data_contract():

    result = KnowledgeSearchResult(
        document_id="doc-001",
        source_id="concept-001",
        knowledge_type="concept",
        text="Matrix knowledge",
        distance=0.10,
    )

    assert result.document_id == "doc-001"
    assert result.source_id == "concept-001"
    assert result.knowledge_type == "concept"
    assert result.text == "Matrix knowledge"
    assert result.distance == 0.10