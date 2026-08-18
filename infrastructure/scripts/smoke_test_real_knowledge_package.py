import json
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from functions.pdf_ingestion.azure_processor import (
    AzureProcessor,
)
from functions.pdf_ingestion.canonical_document_builder import (
    CanonicalDocumentBuilder,
)
from services.integration.knowledge_package_builder import (
    KnowledgePackageBuilder,
)
from services.repositories.firestore_knowledge_package_repository import (
    FirestoreKnowledgePackageRepository,
)
from services.repositories.repository_knowledge_base_reader import (
    RepositoryKnowledgeBaseReader,
)


FIXTURE_PATH = (
    ROOT_DIR
    / "tests"
    / "fixtures"
    / "Matrices-1-10.pdf.json"
)


def main() -> None:
    # ---------------------------------------------------------
    # 1. Load real Azure Document Intelligence fixture
    # ---------------------------------------------------------

    print("1. Loading real Matrices fixture...")

    with open(
        FIXTURE_PATH,
        encoding="utf-8",
    ) as f:
        azure_document = json.load(f)

    print("   PASS: fixture loaded")

    # ---------------------------------------------------------
    # 2. Azure JSON -> canonical blocks
    # ---------------------------------------------------------

    print("2. Building canonical blocks...")

    processor = AzureProcessor()

    blocks = processor.process(
        azure_document
    )

    assert blocks

    print(
        f"   PASS: {len(blocks)} canonical blocks"
    )

    # ---------------------------------------------------------
    # 3. Canonical blocks -> Canonical Document
    # ---------------------------------------------------------

    print("3. Building Canonical Document...")

    canonical_builder = (
        CanonicalDocumentBuilder()
    )

    canonical_document = (
        canonical_builder.build(
            blocks=blocks,
            page_count=len(
                azure_document[
                    "analyzeResult"
                ]["pages"]
            ),
            filename="Matrices-1-10.pdf",
            raw_bucket="test-bucket",
            raw_object=(
                "test/Matrices-1-10.pdf"
            ),
            generation="1",
        )
    )

    document_id = (
        canonical_document[
            "document"
        ]["document_id"]
    )

    assert document_id

    print(
        f"   PASS: document_id={document_id}"
    )

    # ---------------------------------------------------------
    # 4. Canonical Document -> KnowledgePackage
    # ---------------------------------------------------------

    print(
        "4. Building real KnowledgePackage..."
    )

    package_builder = (
        KnowledgePackageBuilder()
    )

    package = package_builder.build(
        canonical_document
    )

    assert package.document_id == document_id
    assert package.schema_version == "1.0"

    print("   PASS: package built")

    # ---------------------------------------------------------
    # 5. Verify real extracted knowledge
    # ---------------------------------------------------------

    print(
        "5. Verifying extracted knowledge..."
    )

    print(
        f"   chapters : {len(package.chapters)}"
    )
    print(
        f"   sections : {len(package.sections)}"
    )
    print(
        f"   concepts : {len(package.concepts)}"
    )
    print(
        f"   formulas : {len(package.formulas)}"
    )
    print(
        f"   examples : {len(package.examples)}"
    )
    print(
        f"   exercises: {len(package.exercises)}"
    )

    assert len(package.chapters) >= 1
    assert len(package.sections) >= 2

    chapter = package.chapters[0]

    assert chapter.number == 3
    assert chapter.title == "Matrices"
    assert chapter.start_page == 1
    assert chapter.end_page == 2

    section_numbers = [
        section.number
        for section in package.sections
    ]

    assert "3.1" in section_numbers
    assert "3.2" in section_numbers

    print(
        "   PASS: real knowledge verified"
    )

    # ---------------------------------------------------------
    # 6. Save REAL KnowledgePackage to Firestore
    # ---------------------------------------------------------

    print(
        "6. Saving real KnowledgePackage to Firestore..."
    )

    repository = (
        FirestoreKnowledgePackageRepository()
    )

    reader = (
        RepositoryKnowledgeBaseReader(
            repository
        )
    )

    repository.save(package)

    print("   PASS: Firestore save")

    # ---------------------------------------------------------
    # 7. Read REAL KnowledgePackage through
    #    KnowledgeBaseReader
    # ---------------------------------------------------------

    print(
        "7. Reading real package through KnowledgeBaseReader..."
    )

    result = reader.get_package(
        document_id
    )

    assert result is not None

    assert result.document_id == (
        package.document_id
    )

    assert result.schema_version == (
        package.schema_version
    )

    assert len(result.chapters) == (
        len(package.chapters)
    )

    assert len(result.sections) == (
        len(package.sections)
    )

    assert len(result.concepts) == (
        len(package.concepts)
    )

    assert len(result.formulas) == (
        len(package.formulas)
    )

    assert len(result.examples) == (
        len(package.examples)
    )

    assert len(result.exercises) == (
        len(package.exercises)
    )

    print(
        "   PASS: real package read"
    )

    # ---------------------------------------------------------
    # 8. Cleanup
    # ---------------------------------------------------------

    print(
        "8. Cleaning up Firestore test document..."
    )

    repository.collection.document(
        document_id
    ).delete()

    print("   PASS: document deleted")

    # ---------------------------------------------------------
    # 9. Verify cleanup
    # ---------------------------------------------------------

    print(
        "9. Verifying Firestore cleanup..."
    )

    result = reader.get_package(
        document_id
    )

    assert result is None

    print("   PASS: cleanup verified")

    print()
    print(
        "Real KnowledgePackage Firestore smoke test: PASS"
    )


if __name__ == "__main__":
    main()