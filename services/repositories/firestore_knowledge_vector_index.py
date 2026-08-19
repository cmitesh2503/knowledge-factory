from __future__ import annotations

import hashlib
from typing import Any

from google import genai
from google.cloud import firestore

from services.models.knowledge_package import KnowledgePackage
from services.repositories.knowledge_vector_index import (
    KnowledgeVectorIndex,
)
from google.cloud.firestore_v1.vector import Vector
from services.vector.knowledge_chunk_builder import (
    KnowledgeChunkBuilder,
)
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from services.models.knowledge_search_result import (
    KnowledgeSearchResult,
)

from services.repositories.knowledge_search_repository import (
    KnowledgeSearchRepository,
)


class FirestoreKnowledgeVectorIndex(
    KnowledgeSearchRepository
):
    """
    Firestore Vector Search implementation.

    Stores derived vector-search documents separately
    from the canonical KnowledgePackage collection.
    """

    COLLECTION_NAME = "knowledge_vectors"

    def __init__(
        self,
        client: firestore.Client | None = None,
        genai_client: genai.Client | None = None,
        embedding_model: str = "gemini-embedding-001",
        embedding_dimensions: int = 768,
    ) -> None:

        self.client = (
            client
            if client is not None
            else firestore.Client()
        )

        self.collection = self.client.collection(
            self.COLLECTION_NAME
        )

        self.genai_client = (
            genai_client
            if genai_client is not None
            else genai.Client()
        )

        self.embedding_model = embedding_model
        self.embedding_dimensions = (
            embedding_dimensions
        )
        
        self.chunk_builder = (
            KnowledgeChunkBuilder()
        )

    def index(
        self,
        package: KnowledgePackage,
    ) -> None:
        """
        Index searchable knowledge from a package.

        The canonical KnowledgePackage remains the
        source of truth. Vector documents are derived data.
        """

        if not package.document_id:
            raise ValueError(
                "KnowledgePackage.document_id "
                "cannot be empty"
            )

        chunks = self.chunk_builder.build(
            package
        )

        for item in chunks:

            vector = self._embed(
                item["text"]
            )

            vector_document_id = (
                self._vector_document_id(
                    package.document_id,
                    item["id"],
                )
            )

            self.collection.document(
                vector_document_id
            ).set(
                {
                    "document_id": package.document_id,
                    "source_id": item["id"],
                    "knowledge_type": item[
                        "knowledge_type"
                    ],
                    "text": item["text"],
                    "metadata": item["metadata"],
                    "embedding": Vector(vector)
                    ,
                }
            )

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[KnowledgeSearchResult]:
        """
        Search indexed knowledge using Firestore Vector Search.

        Firestore-specific details remain inside this
        implementation. Callers receive only the
        provider-independent KnowledgeSearchResult model.
        """

        if not query.strip():
            raise ValueError(
                "query cannot be empty"
            )

        if top_k < 1:
            raise ValueError(
                "top_k must be greater than zero"
            )

        query_vector = self._embed(query)

        vector_query = (
            self.collection.find_nearest(
                vector_field="embedding",
                query_vector=query_vector,
                distance_measure=(
                    DistanceMeasure.COSINE
                ),
                limit=top_k,
                distance_result_field=(
                    "vector_distance"
                ),
            )
        )

        if filters:
            for field, value in filters.items():
                vector_query = (
                    vector_query.where(
                        filter=firestore.FieldFilter(
                            field,
                            "==",
                            value,
                        )
                    )
                )

        snapshots = vector_query.stream()

        results: list[
            KnowledgeSearchResult
        ] = []

        for snapshot in snapshots:

            data = snapshot.to_dict() or {}

            results.append(
                KnowledgeSearchResult(
                    document_id=data.get(
                        "document_id",
                        "",
                    ),
                    source_id=data.get(
                        "source_id",
                        "",
                    ),
                    knowledge_type=data.get(
                        "knowledge_type",
                        "",
                    ),
                    text=data.get(
                        "text",
                        "",
                    ),
                    distance=data.get(
                        "vector_distance"
                    ),
                    metadata=data.get(
                        "metadata",
                        {},
                    ),
                )
            )

    
        return results

    def _embed(
        self,
        text: str,
    ) -> list[float]:

        response = (
            self.genai_client.models.embed_content(
                model=self.embedding_model,
                contents=text,
                config={
                    "output_dimensionality": (
                        self.embedding_dimensions
                    ),
                },
            )
        )

        if not response.embeddings:
            raise RuntimeError(
                "Embedding API returned no embeddings."
            )

        values = response.embeddings[0].values

        if values is None:
            raise RuntimeError(
                "Embedding API returned empty vector."
            )

        return list(values)

    def _build_search_documents(
        self,
        package: KnowledgePackage,
    ) -> list[dict[str, Any]]:
        """
        Convert provider-independent KnowledgePackage
        entities into searchable vector documents.

        This is intentionally simple for MVP.
        """

        documents: list[dict[str, Any]] = []

        for concept in package.concepts:

            text = self._concept_text(
                concept
            )

            if text:
                documents.append(
                    {
                        "id": concept.id,
                        "knowledge_type": "concept",
                        "text": text,
                        "metadata": {
                            "document_id": (
                                package.document_id
                            ),
                            "concept_id": concept.id,
                        },
                    }
                )

        return documents

    def _concept_text(
        self,
        concept: Any,
    ) -> str:

        parts: list[str] = []

        title = getattr(
            concept,
            "title",
            None,
        )

        if title:
            parts.append(str(title))

        name = getattr(
            concept,
            "name",
            None,
        )

        if name and str(name) not in parts:
            parts.append(str(name))

        description = getattr(
            concept,
            "description",
            None,
        )

        if description:
            parts.append(str(description))

        return "\n".join(
            part.strip()
            for part in parts
            if part and str(part).strip()
        )

    def _vector_document_id(
        self,
        document_id: str,
        source_id: str,
    ) -> str:

        raw = (
            f"{document_id}:{source_id}"
        )

        digest = hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()[:32]

        return f"vec-{digest}"