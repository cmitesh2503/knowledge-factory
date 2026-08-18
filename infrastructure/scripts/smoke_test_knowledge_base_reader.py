import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from services.models.knowledge_package import KnowledgePackage
from services.repositories.firestore_knowledge_package_repository import (
    FirestoreKnowledgePackageRepository,
)
from services.repositories.repository_knowledge_base_reader import (
    RepositoryKnowledgeBaseReader,
)


TEST_DOCUMENT_ID = "smoke-test-knowledge-base-reader"


def main() -> None:
    repository = FirestoreKnowledgePackageRepository()

    reader = RepositoryKnowledgeBaseReader(
        repository
    )

    package = KnowledgePackage(
        schema_version="1.0",
        document_id=TEST_DOCUMENT_ID,
        metadata={
            "source": "knowledge_base_reader_smoke_test",
            "subject": "Mathematics",
            "grade": 10,
        },
    )

    print("1. Saving test package...")
    repository.save(package)

    print("2. Reading through KnowledgeBaseReader...")
    result = reader.get_package(
        TEST_DOCUMENT_ID
    )

    assert result is not None
    assert result.document_id == TEST_DOCUMENT_ID
    assert result.schema_version == "1.0"
    assert result.metadata["subject"] == "Mathematics"
    assert result.metadata["grade"] == 10

    print("   PASS: reader/get")

    print("3. Deleting test document...")
    repository.collection.document(
        TEST_DOCUMENT_ID
    ).delete()

    print("4. Verifying cleanup...")

    result = reader.get_package(
        TEST_DOCUMENT_ID
    )

    assert result is None

    print("   PASS: cleanup")
    print()
    print("Knowledge Base reader smoke test: PASS")


if __name__ == "__main__":
    main()