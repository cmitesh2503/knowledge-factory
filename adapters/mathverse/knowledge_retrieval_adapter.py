from __future__ import annotations

from typing import Any

from services.models.knowledge_search_result import (
    KnowledgeSearchResult,
)
from services.retrieval.knowledge_retrieval_service import (
    KnowledgeRetrievalService,
)


class MathVerseKnowledgeRetrievalAdapter:
    """
    Adapter between Knowledge Factory retrieval and MathVerse.

    MathVerse receives application-friendly retrieval data
    without depending directly on Knowledge Factory vector
    providers, indexes, or internal search result models.
    """

    def __init__(
        self,
        knowledge_retrieval_service: (
            KnowledgeRetrievalService
        ),
    ) -> None:

        self.knowledge_retrieval_service = (
            knowledge_retrieval_service
        )

    def retrieve(
        self,
        query: str,
        limit: int = 10,
    ) -> dict[str, Any]:
        """
        Retrieve knowledge relevant to a MathVerse query.

        Returns a MathVerse-oriented response structure.
        """

        context = (
            self.knowledge_retrieval_service.retrieve(
                query=query,
                limit=limit,
            )
        )

        return {
            "query": context.query,
            "results": [
                self._to_mathverse_result(
                    result
                )
                for result in context.results
            ],
        }

    def _to_mathverse_result(
        self,
        result: KnowledgeSearchResult,
    ) -> dict[str, Any]:
        """
        Convert a Knowledge Factory search result into
        a MathVerse retrieval result.
        """

        metadata = result.metadata or {}

        return {
            "id": result.source_id,
            "type": result.knowledge_type,
            "content": result.text,
            "distance": result.distance,
            "source": {
                "document_id": (
                    result.document_id
                ),
                "page": metadata.get(
                    "page"
                ),
                "section_number": metadata.get(
                    "section_number"
                ),
                "chapter_id": metadata.get(
                    "chapter_id"
                ),
            },
            "metadata": metadata,
        }