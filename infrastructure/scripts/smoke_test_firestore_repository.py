import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from services.models.knowledge_package import (
    KnowledgePackage,
)
from services.repositories.firestore_knowledge_package_repository import (
    FirestoreKnowledgePackageRepository,
)


TEST_DOCUMENT_ID = "smoke-test-kf-001"


def main() -> None:
    repository = (
        FirestoreKnowledgePackageRepository()
    )

    package = KnowledgePackage(
        schema_version="1.0",
        document_id=TEST_DOCUMENT_ID,
        metadata={
            "test": True,
            "source": "firestore-smoke-test",
        },
    )

    print("1. Saving test package...")
    repository.save(package)

    print("2. Reading test package...")
    restored = repository.get(
        TEST_DOCUMENT_ID
    )

    assert restored is not None
    assert restored.document_id == TEST_DOCUMENT_ID
    assert restored.schema_version == "1.0"
    assert restored.metadata["test"] is True

    print("   PASS: save/get")

    print("3. Deleting test document...")
    repository.collection.document(
        TEST_DOCUMENT_ID
    ).delete()

    print("4. Verifying cleanup...")
    deleted = repository.get(
        TEST_DOCUMENT_ID
    )

    assert deleted is None

    print("   PASS: cleanup")
    print()
    print("Firestore smoke test: PASS")


if __name__ == "__main__":
    main()