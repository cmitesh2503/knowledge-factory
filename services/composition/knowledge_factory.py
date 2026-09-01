from __future__ import annotations

from google import genai
from google.cloud import firestore

from adapters.mathverse.knowledge_retrieval_adapter import (
    MathVerseKnowledgeRetrievalAdapter,
)
from services.retrieval.knowledge_retrieval_service import (
    KnowledgeRetrievalService,
)
from services.vector.firestore_vector_index import (
    FirestoreVectorIndex,
)
from services.vector.gemini_embedding_provider import (
    GeminiEmbeddingProvider,
)
from services.vector.knowledge_chunk_builder import (
    KnowledgeChunkBuilder,
)
from services.vector.knowledge_search_service import (
    KnowledgeSearchService,
)
from services.vector.vector_indexing_service import (
    VectorIndexingService,
)


class KnowledgeFactoryApplication:
    """
    Application composition root.

    This class wires concrete infrastructure providers
    to provider-independent Knowledge Factory services.
    """

    def __init__(
        self,
        *,
        firestore_client: firestore.Client | None = None,
        genai_client: genai.Client | None = None,
        embedding_model: str = "gemini-embedding-001",
        embedding_dimensions: int = 768,
    ) -> None:

        resolved_firestore_client = (
            firestore_client
            if firestore_client is not None
            else firestore.Client()
        )

        resolved_genai_client = (
            genai_client
            if genai_client is not None
            else genai.Client()
        )

        self.embedding_provider = (
            GeminiEmbeddingProvider(
                client=resolved_genai_client,
                embedding_model=embedding_model,
                embedding_dimensions=embedding_dimensions,
            )
        )

        self.vector_index = (
            FirestoreVectorIndex(
                client=resolved_firestore_client,
                
            )
        )

        self.chunk_builder = (
            KnowledgeChunkBuilder()
        )

        self.vector_indexing_service = (
            VectorIndexingService(
                embedding_provider=(
                    self.embedding_provider
                ),
                vector_index=(
                    self.vector_index
                ),
                chunk_builder=(
                    self.chunk_builder
                ),
            )
        )

        self.knowledge_search_service = (
            KnowledgeSearchService(
                embedding_provider=(
                    self.embedding_provider
                ),
                vector_index=(
                    self.vector_index
                ),
            )
        )

        self.knowledge_retrieval_service = (
            KnowledgeRetrievalService(
                knowledge_search_service=(
                    self.knowledge_search_service
                )
            )
        )

        self.mathverse_retrieval_adapter = (
            MathVerseKnowledgeRetrievalAdapter(
                knowledge_retrieval_service=(
                    self.knowledge_retrieval_service
                )
            )
        )