from __future__ import annotations

from services.models.knowledge_search_result import (
    KnowledgeSearchResult,
)
from services.vector.embedding_provider import (
    EmbeddingProvider,
)
from services.vector.vector_index import (
    VectorIndex,
)


class KnowledgeSearchService:
    """
    Provider-independent semantic search service.

    Generates an embedding for a query, searches the
    configured VectorIndex, and returns application-level
    KnowledgeSearchResult objects.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_index: VectorIndex,
    ) -> None:

        self.embedding_provider = (
            embedding_provider
        )

        self.vector_index = vector_index

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[KnowledgeSearchResult]:
        """
        Search knowledge using semantic similarity.
        """

        query = query.strip()

        if not query:
            return []

        embeddings = (
            self.embedding_provider.embed(
                [query]
            )
        )

        if len(embeddings) != 1:
            raise ValueError(
                "Embedding provider must return exactly "
                "one embedding for a search query."
            )

        records = self.vector_index.search(
            vector=embeddings[0],
            limit=limit,
        )

        return [
            self._to_search_result(record)
            for record in records
        ]

    def _to_search_result(
        self,
        record: dict,
    ) -> KnowledgeSearchResult:

        metadata = record.get(
            "metadata",
            {},
        )

        return KnowledgeSearchResult(
            document_id=metadata.get(
                "document_id",
                "",
            ),
            source_id=record.get(
                "id",
                "",
            ),
            knowledge_type=record.get(
                "knowledge_type",
                "",
            ),
            text=record.get(
                "text",
                "",
            ),
            distance=record.get(
                "distance",
            ),
            metadata=metadata,
        )