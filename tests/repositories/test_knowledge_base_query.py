from services.models.knowledge_package import (
    KnowledgePackage,
)
from services.repositories.knowledge_base_query import (
    KnowledgeBaseQuery,
)


class FakeKnowledgeBaseQuery(
    KnowledgeBaseQuery
):
    """
    Test-only implementation of the query contract.
    """

    def __init__(self) -> None:
        self.packages: dict[
            str,
            KnowledgePackage,
        ] = {}

    def get_package(
        self,
        document_id: str,
    ) -> KnowledgePackage | None:
        return self.packages.get(
            document_id
        )

    def list_packages(
        self,
    ) -> list[KnowledgePackage]:
        return list(
            self.packages.values()
        )


def test_query_returns_package():

    query = FakeKnowledgeBaseQuery()

    package = KnowledgePackage(
        schema_version="1.0",
        document_id="doc-001",
    )

    query.packages["doc-001"] = package

    result = query.get_package(
        "doc-001"
    )

    assert result is not None
    assert result.document_id == "doc-001"


def test_query_returns_none_for_missing_package():

    query = FakeKnowledgeBaseQuery()

    result = query.get_package(
        "does-not-exist"
    )

    assert result is None


def test_query_lists_packages():

    query = FakeKnowledgeBaseQuery()

    package1 = KnowledgePackage(
        schema_version="1.0",
        document_id="doc-001",
    )

    package2 = KnowledgePackage(
        schema_version="1.0",
        document_id="doc-002",
    )

    query.packages["doc-001"] = package1
    query.packages["doc-002"] = package2

    result = query.list_packages()

    assert len(result) == 2

    document_ids = {
        package.document_id
        for package in result
    }

    assert document_ids == {
        "doc-001",
        "doc-002",
    }