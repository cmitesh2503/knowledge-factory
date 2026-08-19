from __future__ import annotations

from google import genai
from google.cloud import firestore

from services.models.knowledge_package import KnowledgePackage
from services.repositories.firestore_knowledge_vector_index import (
    FirestoreKnowledgeVectorIndex,
)


class KnowledgeVectorPublisher:
    """
    Publishes any KnowledgePackage into the
    Firestore vector-search index.

    KnowledgePackage remains the canonical source.
    Vector documents are derived data.
    """

    def __init__(
        self,
        *,
        firestore_client: firestore.Client,
        genai_client: genai.Client,
        embedding_model: str = "gemini-embedding-001",
        embedding_dimensions: int = 768,
    ) -> None:

        self.vector_index = (
            FirestoreKnowledgeVectorIndex(
                client=firestore_client,
                genai_client=genai_client,
                embedding_model=embedding_model,
                embedding_dimensions=embedding_dimensions,
            )
        )

    def publish(
        self,
        package: KnowledgePackage,
    ) -> None:
        """
        Publish one KnowledgePackage into the
        vector-search index.
        """

        if not package.document_id:
            raise ValueError(
                "KnowledgePackage.document_id "
                "cannot be empty"
            )

        self.vector_index.index(package)