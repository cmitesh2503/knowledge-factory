from __future__ import annotations

from typing import Any

from services.models.knowledge_package import (
    KnowledgePackage,
)
from services.vector.embedding_provider import (
    EmbeddingProvider,
)
from services.vector.knowledge_chunk_builder import (
    KnowledgeChunkBuilder,
)
from services.vector.vector_index import (
    VectorIndex,
)


class VectorIndexingService:
    """
    Builds semantic chunks from a KnowledgePackage,
    generates embeddings, and stores them in a
    provider-independent VectorIndex.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_index: VectorIndex,
        chunk_builder: KnowledgeChunkBuilder | None = None,
    ) -> None:

        self.embedding_provider = (
            embedding_provider
        )

        self.vector_index = vector_index

        self.chunk_builder = (
            chunk_builder
            or KnowledgeChunkBuilder()
        )

    def index(
        self,
        package: KnowledgePackage,
    ) -> int:
        """
        Index a KnowledgePackage.

        Returns the number of indexed chunks.
        """

        chunks = self.chunk_builder.build(
            package
        )

        if not chunks:
            return 0

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = (
            self.embedding_provider.embed(
                texts
            )
        )

        records: list[dict[str, Any]] = []

        for (
            chunk,
            embedding,
        ) in zip(
            chunks,
            embeddings,
        ):

            records.append(
                {
                    "id": chunk["id"],
                    "vector": embedding,
                    "text": chunk["text"],
                    "metadata": chunk[
                        "metadata"
                    ],
                    "knowledge_type": chunk[
                        "knowledge_type"
                    ],
                }
            )

        self.vector_index.upsert(
            records
        )

        return len(records)