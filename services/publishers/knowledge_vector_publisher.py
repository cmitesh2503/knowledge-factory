from __future__ import annotations

from services.models.knowledge_package import (
    KnowledgePackage,
)
from services.vector.vector_indexing_service import (
    VectorIndexingService,
)


class KnowledgeVectorPublisher:
    """
    Application-level entry point for publishing a
    KnowledgePackage into the semantic vector index.

    The publisher does not know about Firestore, Gemini,
    embeddings, or vector database implementation details.
    Those responsibilities belong to VectorIndexingService
    and the dependencies wired by the composition root.
    """

    def __init__(
        self,
        vector_indexing_service: VectorIndexingService,
    ) -> None:

        self.vector_indexing_service = (
            vector_indexing_service
        )

    def publish(
        self,
        package: KnowledgePackage,
    ) -> int:
        """
        Publish one KnowledgePackage into the vector index.

        Returns the number of indexed chunks.
        """

        if not package.document_id:
            raise ValueError(
                "KnowledgePackage.document_id "
                "cannot be empty"
            )

        return (
            self.vector_indexing_service.index(
                package
            )
        )