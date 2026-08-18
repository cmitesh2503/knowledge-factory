from services.models.knowledge_package import (
    KnowledgePackage,
)
from services.repositories.knowledge_package_repository import (
    KnowledgePackageRepository,
)


class InMemoryKnowledgePackageRepository(
    KnowledgePackageRepository
):
    """
    Test-only repository implementation.

    This verifies the repository contract without
    introducing Firestore into unit tests.
    """

    def __init__(self) -> None:
        self._packages: dict[
            str,
            KnowledgePackage,
        ] = {}

    def save(
        self,
        package: KnowledgePackage,
    ) -> None:
        self._packages[
            package.document_id
        ] = package

    def get(
        self,
        document_id: str,
    ) -> KnowledgePackage | None:
        return self._packages.get(
            document_id
        )


def test_repository_saves_and_retrieves_package():

    repository = (
        InMemoryKnowledgePackageRepository()
    )

    package = KnowledgePackage(
        schema_version="1.0",
        document_id="doc-matrices-001",
    )

    repository.save(package)

    result = repository.get(
        "doc-matrices-001"
    )

    assert result is not None
    assert result.document_id == (
        "doc-matrices-001"
    )
    assert result.schema_version == "1.0"


def test_repository_returns_none_for_missing_package():

    repository = (
        InMemoryKnowledgePackageRepository()
    )

    result = repository.get(
        "does-not-exist"
    )

    assert result is None