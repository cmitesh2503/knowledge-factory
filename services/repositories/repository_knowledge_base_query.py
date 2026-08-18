from __future__ import annotations

from services.models.knowledge_package import (
    KnowledgePackage,
)
from services.repositories.knowledge_base_query import (
    KnowledgeBaseQuery,
)
from services.repositories.knowledge_package_repository import (
    KnowledgePackageRepository,
)


class RepositoryKnowledgeBaseQuery(
    KnowledgeBaseQuery
):
    """
    KnowledgeBaseQuery implementation backed by
    a KnowledgePackageRepository.

    This keeps query consumers independent of the
    underlying persistence provider.
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

    def list_packages(
        self,
    ) -> list[KnowledgePackage]:
        """
        Listing is not supported by the current
        KnowledgePackageRepository contract.

        This will be implemented only after a
        provider-independent list operation is
        deliberately added to the persistence boundary.
        """

        raise NotImplementedError(
            "list_packages is not supported by "
            "the current KnowledgePackageRepository "
            "contract"
        )