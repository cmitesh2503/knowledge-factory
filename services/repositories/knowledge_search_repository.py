from __future__ import annotations

from abc import ABC, abstractmethod

from services.models.knowledge_search_result import (
    KnowledgeSearchResult,
)


class KnowledgeSearchRepository(ABC):
    """
    Provider-independent read-only search contract.

    MathVerse depends on this interface, not Firestore.
    """

    @abstractmethod
    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        filters: dict | None = None,
    ) -> list[KnowledgeSearchResult]:
        """
        Search knowledge and return relevant results.
        """

        raise NotImplementedError