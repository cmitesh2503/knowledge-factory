from __future__ import annotations

from abc import ABC, abstractmethod

from services.models.knowledge_package import (
    KnowledgePackage,
)


class KnowledgeBaseQuery(ABC):
    """
    Provider-independent query boundary for the
    Knowledge Factory knowledge base.

    Consumers such as MathVerse should depend on
    this interface rather than Firestore directly.
    """

    @abstractmethod
    def get_package(
        self,
        document_id: str,
    ) -> KnowledgePackage | None:
        """
        Retrieve a complete KnowledgePackage by
        document ID.
        """
        raise NotImplementedError

    @abstractmethod
    def list_packages(
        self,
    ) -> list[KnowledgePackage]:
        """
        Retrieve available KnowledgePackages.
        """
        raise NotImplementedError