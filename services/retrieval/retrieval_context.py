from __future__ import annotations

from dataclasses import dataclass, field

from services.models.knowledge_search_result import (
    KnowledgeSearchResult,
)


@dataclass(slots=True)
class RetrievalContext:
    """
    Provider-independent knowledge context returned
    to a consumer such as MathVerse.

    This is the retrieval boundary between the
    Knowledge Factory and downstream applications.
    """

    query: str

    results: list[KnowledgeSearchResult] = field(
        default_factory=list
    )

    def is_empty(self) -> bool:
        """
        Return whether retrieval produced no results.
        """

        return not self.results