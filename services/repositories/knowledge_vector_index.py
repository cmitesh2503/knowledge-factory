from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from services.models.knowledge_package import (
    KnowledgePackage,
)


class KnowledgeVectorIndex(ABC):
    """
    Provider-independent vector indexing boundary.

    Knowledge Factory core code must depend only on this
    contract and must not know whether the underlying
    implementation is Firestore Vector Search, Vertex AI
    Vector Search, another vector database, etc.
    """

    @abstractmethod
    def index(
        self,
        package: KnowledgePackage,
    ) -> None:
        """
        Index a KnowledgePackage for semantic retrieval.
        """
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search indexed knowledge semantically.

        Returns provider-independent search results.
        """
        raise NotImplementedError