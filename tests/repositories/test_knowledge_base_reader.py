from services.models.knowledge_package import KnowledgePackage
from services.repositories.knowledge_base_reader import (
    KnowledgeBaseReader,
)


class FakeKnowledgeBaseReader(
    KnowledgeBaseReader
):
    """
    Minimal test implementation of the
    KnowledgeBaseReader contract.
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


def test_knowledge_base_reader_returns_package():

    reader = FakeKnowledgeBaseReader()

    package = KnowledgePackage(
        schema_version="1.0",
        document_id="doc-001",
        metadata={
            "subject": "Mathematics",
            "grade": 10,
        },
    )

    reader.packages[
        "doc-001"
    ] = package

    result = reader.get_package(
        "doc-001"
    )

    assert result is not None
    assert result.document_id == "doc-001"
    assert result.schema_version == "1.0"
    assert result.metadata["subject"] == "Mathematics"
    assert result.metadata["grade"] == 10


def test_knowledge_base_reader_returns_none_for_missing_package():

    reader = FakeKnowledgeBaseReader()

    result = reader.get_package(
        "does-not-exist"
    )

    assert result is None