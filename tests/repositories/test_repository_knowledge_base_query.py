from services.models.knowledge_package import (
    KnowledgePackage,
)
from services.repositories.knowledge_base_query import (
    KnowledgeBaseQuery,
)
from services.repositories.knowledge_package_repository import (
    KnowledgePackageRepository,
)
from services.repositories.repository_knowledge_base_query import (
    RepositoryKnowledgeBaseQuery,
)


class FakeKnowledgePackageRepository(
    KnowledgePackageRepository
):
    """
    Test-only repository implementation.
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


def test_query_returns_package_from_repository():

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

    query = RepositoryKnowledgeBaseQuery(
        repository
    )

    assert isinstance(
        query,
        KnowledgeBaseQuery,
    )

    result = query.get_package(
        "doc-001"
    )

    assert result is not None
    assert result.document_id == "doc-001"
    assert result.schema_version == "1.0"
    assert result.metadata["subject"] == "Mathematics"
    assert result.metadata["grade"] == 10


def test_query_returns_none_for_missing_package():

    repository = (
        FakeKnowledgePackageRepository()
    )

    query = RepositoryKnowledgeBaseQuery(
        repository
    )

    result = query.get_package(
        "does-not-exist"
    )

    assert result is None


def test_list_packages_is_not_supported_yet():

    repository = (
        FakeKnowledgePackageRepository()
    )

    query = RepositoryKnowledgeBaseQuery(
        repository
    )

    try:
        query.list_packages()
    except NotImplementedError as exc:
        assert (
            "list_packages is not supported"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Expected NotImplementedError"
        )