from __future__ import annotations

from services.models.knowledge_package import KnowledgePackage
from services.repositories.knowledge_base_reader import (
    KnowledgeBaseReader,
)
from services.repositories.knowledge_package_repository import (
    KnowledgePackageRepository,
)


class RepositoryKnowledgeBaseReader(
    KnowledgeBaseReader
):
    """
    KnowledgeBaseReader implementation backed by
    a KnowledgePackageRepository.

    This keeps the Knowledge Base read boundary
    independent of the underlying persistence provider.
    """

    def __init__(
        self,
        repository: KnowledgePackageRepository,
    ) -> None:
        self.repository = repository

    def get_package(
        self,
        document_id: str,
    ) -> KnowledgePackage | None:
        """
        Retrieve a KnowledgePackage through the
        repository abstraction.
        """

        return self.repository.get(
            document_id
        )