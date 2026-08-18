"""
Firestore implementation of the KnowledgePackage repository.

Firestore is an implementation detail of the persistence boundary.
"""

from __future__ import annotations

from typing import Any

from google.cloud import firestore

from services.models.knowledge_package import (
    KnowledgePackage,
)
from services.repositories.knowledge_package_repository import (
    KnowledgePackageRepository,
)


class FirestoreKnowledgePackageRepository(
    KnowledgePackageRepository
):
    """
    Persists KnowledgePackage objects in Firestore.

    Collection:
        knowledge_packages

    Document ID:
        KnowledgePackage.document_id
    """

    COLLECTION_NAME = "knowledge_packages"

    def __init__(
        self,
        client: firestore.Client | None = None,
    ) -> None:

        self.client = (
            client
            if client is not None
            else firestore.Client()
        )

        self.collection = self.client.collection(
            self.COLLECTION_NAME
        )

    def save(
        self,
        package: KnowledgePackage,
    ) -> None:

        if not package.document_id:
            raise ValueError(
                "KnowledgePackage.document_id "
                "cannot be empty"
            )

        self.collection.document(
            package.document_id
        ).set(
            package.to_dict()
        )

    def get(
        self,
        document_id: str,
    ) -> KnowledgePackage | None:

        if not document_id:
            raise ValueError(
                "document_id cannot be empty"
            )

        snapshot = (
            self.collection
            .document(document_id)
            .get()
        )

        if not snapshot.exists:
            return None

        data: dict[str, Any] = (
            snapshot.to_dict() or {}
        )

        return self._from_dict(data)

    def _from_dict(
        self,
        data: dict[str, Any],
    ) -> KnowledgePackage:
        """
        Reconstruct a KnowledgePackage from its
        provider-independent serialized representation.
        """

        return KnowledgePackage.from_dict(data)