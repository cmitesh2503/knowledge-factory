from __future__ import annotations

import hashlib
from typing import Any

from google.cloud import firestore
from google.cloud.firestore_v1.base_vector_query import (
    DistanceMeasure,
)
from google.cloud.firestore_v1.vector import (
    Vector,
)

from services.vector.vector_index import (
    VectorIndex,
)


class FirestoreVectorIndex(VectorIndex):
    """
    Google Firestore implementation of the provider-independent
    VectorIndex contract.

    This class knows about Firestore, but callers depend only on
    the VectorIndex abstraction.
    """

    COLLECTION_NAME = "knowledge_vectors"

    def __init__(
        self,
        client: firestore.Client | None = None,
        collection_name: str | None = None,
    ) -> None:

        self.client = (
            client
            if client is not None
            else firestore.Client()
        )

        self.collection_name = (
            collection_name
            or self.COLLECTION_NAME
        )

        self.collection = (
            self.client.collection(
                self.collection_name
            )
        )

    def upsert(
        self,
        records: list[dict[str, Any]],
    ) -> None:
        """
        Insert or update vector records in Firestore.
        """

        for record in records:

            self._validate_record(
                record
            )

            metadata = record.get(
                "metadata",
                {},
            )

            document_id = metadata.get(
                "document_id",
                "",
            )

            firestore_document_id = (
                self._document_id(
                    document_id=document_id,
                    source_id=record["id"],
                )
            )

            self.collection.document(
                firestore_document_id
            ).set(
                {
                    "id": record["id"],
                    "text": record["text"],
                    "knowledge_type": (
                        record[
                            "knowledge_type"
                        ]
                    ),
                    "metadata": metadata,
                    "embedding": Vector(
                        record["vector"]
                    ),
                }
            )

    def search(
        self,
        vector: list[float],
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Search Firestore using vector similarity.

        Returns provider-independent records compatible
        with KnowledgeSearchService.
        """

        if not vector:
            raise ValueError(
                "Search vector cannot be empty"
            )

        if limit < 1:
            raise ValueError(
                "limit must be greater than zero"
            )

        vector_query = (
            self.collection.find_nearest(
                vector_field="embedding",
                query_vector=Vector(vector),
                distance_measure=(
                    DistanceMeasure.COSINE
                ),
                limit=limit,
                distance_result_field=(
                    "vector_distance"
                ),
            )
        )

        snapshots = vector_query.stream()

        results: list[
            dict[str, Any]
        ] = []

        for snapshot in snapshots:

            data = (
                snapshot.to_dict()
                or {}
            )

            results.append(
                {
                    "id": data.get(
                        "id",
                        "",
                    ),
                    "text": data.get(
                        "text",
                        "",
                    ),
                    "knowledge_type": data.get(
                        "knowledge_type",
                        "",
                    ),
                    "metadata": data.get(
                        "metadata",
                        {},
                    ),
                    "distance": data.get(
                        "vector_distance",
                    ),
                }
            )

        return results

    def _validate_record(
        self,
        record: dict[str, Any],
    ) -> None:
        """
        Validate a vector record before storing it.
        """

        if not record.get(
            "id"
        ):
            raise ValueError(
                "Vector record id cannot be empty"
            )

        if not record.get(
            "text"
        ):
            raise ValueError(
                "Vector record text cannot be empty"
            )

        if not record.get(
            "knowledge_type"
        ):
            raise ValueError(
                "Vector record knowledge_type "
                "cannot be empty"
            )

        vector = record.get(
            "vector"
        )

        if not vector:
            raise ValueError(
                "Vector record vector "
                "cannot be empty"
            )

        metadata = record.get(
            "metadata"
        )

        if not isinstance(
            metadata,
            dict,
        ):
            raise ValueError(
                "Vector record metadata "
                "must be a dictionary"
            )

        document_id = metadata.get(
            "document_id"
        )

        if not document_id:
            raise ValueError(
                "Vector record metadata must "
                "contain document_id"
            )

    def _document_id(
        self,
        document_id: str,
        source_id: str,
    ) -> str:
        """
        Generate a deterministic Firestore document ID.

        The same Knowledge Factory source record always
        maps to the same Firestore vector document.
        """

        raw = (
            f"{document_id}:{source_id}"
        )

        digest = hashlib.sha256(
            raw.encode(
                "utf-8"
            )
        ).hexdigest()[:32]

        return (
            f"vec-{digest}"
        )