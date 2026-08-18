from services.models.knowledge_package import (
    KnowledgePackage,
)
from services.repositories.knowledge_base_reader import (
    KnowledgeBaseReader,
)
from services.repositories.repository_knowledge_base_reader import (
    RepositoryKnowledgeBaseReader,
)
from services.repositories.knowledge_package_repository import (
    KnowledgePackageRepository,
)


class FakeKnowledgePackageRepository(
    KnowledgePackageRepository
):
    """
    Test-only implementation of the repository contract.
    """

    def __init__(self) -> None:
        self.packages: dict[
            str,
            KnowledgePackage,
        ] = {}

    def save(
        self,
        package: KnowledgePackage,
    ) -> None:
        self.packages[
            package.document_id
        ] = package

    def get(
        self,
        document_id: str,
    ) -> KnowledgePackage | None:
        return self.packages.get(
            document_id
        )


def test_reader_returns_package_from_repository():

    repository = (
        FakeKnowledgePackageRepository()
    )

    package = KnowledgePackage(
        schema_version="1.0",
        document_id="doc-001",
        metadata={
            "subject": "Mathematics",
            "grade": 10,
        },
    )

    repository.save(package)

    reader = RepositoryKnowledgeBaseReader(
        repository
    )

    assert isinstance(
        reader,
        KnowledgeBaseReader,
    )

    result = reader.get_package(
        "doc-001"
    )

    assert result is not None
    assert result.document_id == "doc-001"
    assert result.schema_version == "1.0"
    assert result.metadata["subject"] == "Mathematics"
    assert result.metadata["grade"] == 10


def test_reader_returns_none_for_missing_package():

    repository = (
        FakeKnowledgePackageRepository()
    )

    reader = RepositoryKnowledgeBaseReader(
        repository
    )

    result = reader.get_package(
        "does-not-exist"
    )

    assert result is None