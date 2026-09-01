from __future__ import annotations

from services.retrieval.retrieval_context import (
    RetrievalContext,
)
from services.vector.knowledge_search_service import (
    KnowledgeSearchService,
)


class KnowledgeRetrievalService:
    """
    Application-facing retrieval boundary for
    Knowledge Factory consumers.

    Consumers such as MathVerse interact with this
    service instead of directly accessing vector
    search infrastructure.
    """

    def __init__(
        self,
        knowledge_search_service: KnowledgeSearchService,
    ) -> None:

        self.knowledge_search_service = (
            knowledge_search_service
        )

    def retrieve(
        self,
        query: str,
        limit: int = 10,
    ) -> RetrievalContext:
        """
        Retrieve knowledge relevant to a user query.

        Returns a provider-independent RetrievalContext
        suitable for downstream consumers.
        """

        results = (
            self.knowledge_search_service.search(
                query=query,
                limit=limit,
            )
        )

        return RetrievalContext(
            query=query,
            results=results,
        )