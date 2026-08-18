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
from services.repositories.repository_knowledge_base_query import (
    RepositoryKnowledgeBaseQuery,
)


FIXTURE_PATH = (
    ROOT_DIR
    / "tests"
    / "fixtures"
    / "Matrices-1-10.pdf.json"
)


def main() -> None:
    # ---------------------------------------------------------
    # 1. Load actual Matrices fixture
    # ---------------------------------------------------------

    print("1. Loading real Matrices fixture...")

    with open(
        FIXTURE_PATH,
        encoding="utf-8",
    ) as file:
        azure_document = json.load(file)

    print("   PASS: fixture loaded")

    # ---------------------------------------------------------
    # 2. Azure fixture -> canonical blocks
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
            raw_object="test/Matrices-1-10.pdf",
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

    print("   PASS: package built")

    # ---------------------------------------------------------
    # 5. Save actual package to Firestore
    # ---------------------------------------------------------

    print(
        "5. Saving real KnowledgePackage to Firestore..."
    )

    repository = (
        FirestoreKnowledgePackageRepository()
    )

    query = RepositoryKnowledgeBaseQuery(
        repository
    )

    repository.save(package)

    print("   PASS: Firestore save")

    # ---------------------------------------------------------
    # 6. Query through KnowledgeBaseQuery
    # ---------------------------------------------------------

    print(
        "6. Querying through KnowledgeBaseQuery..."
    )

    result = query.get_package(
        document_id
    )

    assert result is not None

    print("   PASS: package retrieved")

    # ---------------------------------------------------------
    # 7. Verify actual knowledge content
    # ---------------------------------------------------------

    print(
        "7. Verifying actual knowledge..."
    )

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

    assert len(result.figures) == (
        len(package.figures)
    )

    print(
        f"   chapters : {len(result.chapters)}"
    )
    print(
        f"   sections : {len(result.sections)}"
    )
    print(
        f"   concepts : {len(result.concepts)}"
    )
    print(
        f"   formulas : {len(result.formulas)}"
    )
    print(
        f"   examples : {len(result.examples)}"
    )
    print(
        f"   exercises: {len(result.exercises)}"
    )
    print(
        f"   figures  : {len(result.figures)}"
    )

    assert len(result.chapters) >= 1
    assert len(result.sections) >= 1
    assert len(result.concepts) >= 1

    print(
        "   PASS: actual knowledge verified"
    )

    # ---------------------------------------------------------
    # 8. Cleanup
    # ---------------------------------------------------------

    print(
        "8. Cleaning up Firestore document..."
    )

    repository.collection.document(
        document_id
    ).delete()

    print("   PASS: document deleted")

    # ---------------------------------------------------------
    # 9. Verify cleanup
    # ---------------------------------------------------------

    print(
        "9. Verifying cleanup..."
    )

    result = query.get_package(
        document_id
    )

    assert result is None

    print("   PASS: cleanup verified")

    print()
    print(
        "Real Knowledge Base query smoke test: PASS"
    )


if __name__ == "__main__":
    main()