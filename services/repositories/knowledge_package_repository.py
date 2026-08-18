"""
Knowledge Factory

Knowledge Package Repository

Defines the provider-independent persistence contract
for KnowledgePackage objects.

This module must not contain Firestore, GCP, or any
other persistence-provider implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from services.models.knowledge_package import KnowledgePackage


class KnowledgePackageRepository(ABC):
    """
    Persistence boundary for KnowledgePackage.

    Implementations may use Firestore, another database,
    or an alternative persistence mechanism.

    The Knowledge Factory core must depend only on this
    interface, not on the persistence provider.
    """

    @abstractmethod
    def save(
        self,
        package: KnowledgePackage,
    ) -> None:
        """
        Persist a KnowledgePackage.

        Implementations must use package.document_id
        as the stable document identity.
        """
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        document_id: str,
    ) -> KnowledgePackage | None:
        """
        Retrieve a KnowledgePackage by document ID.

        Returns None when the package does not exist.
        """
        raise NotImplementedError