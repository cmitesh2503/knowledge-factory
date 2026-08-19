from __future__ import annotations

import json
import sys
from pathlib import Path


# ------------------------------------------------------------------
# Make repository root importable when script is executed as:
#
# python infrastructure/scripts/publish_matrices_knowledge_package.py
# ------------------------------------------------------------------

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


# ------------------------------------------------------------------
# Real source fixture
# ------------------------------------------------------------------

FIXTURE_PATH = (
    ROOT_DIR
    / "tests"
    / "fixtures"
    / "Matrices-1-10.pdf.json"
)


def main() -> None:

    # ==============================================================
    # 1. Load real Matrices fixture
    # ==============================================================

    print("1. Loading real Matrices fixture...")

    if not FIXTURE_PATH.exists():
        raise FileNotFoundError(
            f"Fixture not found: {FIXTURE_PATH}"
        )

    with FIXTURE_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        azure_document = json.load(file)

    print("   PASS: fixture loaded")

    # ==============================================================
    # 2. Build canonical blocks
    # ==============================================================

    print("2. Building canonical blocks...")

    processor = AzureProcessor()

    blocks = processor.process(
        azure_document
    )

    if not blocks:
        raise RuntimeError(
            "No canonical blocks were produced."
        )

    print(
        f"   PASS: {len(blocks)} canonical blocks"
    )

    # ==============================================================
    # 3. Build Canonical Document
    # ==============================================================

    print("3. Building Canonical Document...")

    canonical_builder = (
        CanonicalDocumentBuilder()
    )

    analyze_result = azure_document.get(
        "analyzeResult",
        {},
    )

    pages = analyze_result.get(
        "pages",
        [],
    )

    canonical_document = (
        canonical_builder.build(
            blocks=blocks,
            page_count=len(pages),
            filename="Matrices-1-10.pdf",
            raw_bucket="knowledge-factory",
            raw_object="Matrices-1-10.pdf",
            generation="1",
        )
    )

    document_id = (
        canonical_document[
            "document"
        ]["document_id"]
    )

    if not document_id:
        raise RuntimeError(
            "Canonical Document has no document_id."
        )

    print(
        f"   PASS: document_id={document_id}"
    )

    # ==============================================================
    # 4. Build KnowledgePackage
    # ==============================================================

    print(
        "4. Building KnowledgePackage..."
    )

    package_builder = (
        KnowledgePackageBuilder()
    )

    package = package_builder.build(
        canonical_document
    )

    if package.document_id != document_id:
        raise RuntimeError(
            "KnowledgePackage document_id does not "
            "match Canonical Document document_id."
        )

    print("   PASS: package built")

    # ==============================================================
    # 5. Show knowledge summary
    # ==============================================================

    print(
        "5. KnowledgePackage summary..."
    )

    print(
        f"   document_id: {package.document_id}"
    )
    print(
        f"   chapters   : {len(package.chapters)}"
    )
    print(
        f"   sections   : {len(package.sections)}"
    )
    print(
        f"   concepts   : {len(package.concepts)}"
    )
    print(
        f"   formulas   : {len(package.formulas)}"
    )
    print(
        f"   examples   : {len(package.examples)}"
    )
    print(
        f"   exercises  : {len(package.exercises)}"
    )
    print(
        f"   figures    : {len(package.figures)}"
    )

    # ==============================================================
    # 6. Publish permanently to Firestore
    # ==============================================================

    print()
    print(
        "6. Publishing KnowledgePackage to Firestore..."
    )

    repository = (
        FirestoreKnowledgePackageRepository()
    )

    repository.save(package)

    print(
        "   PASS: KnowledgePackage published"
    )

    # ==============================================================
    # 7. Read back and verify
    # ==============================================================

    print(
        "7. Verifying published KnowledgePackage..."
    )

    published_package = repository.get(
        package.document_id
    )

    if published_package is None:
        raise RuntimeError(
            "Published KnowledgePackage could not "
            "be read back from Firestore."
        )

    if (
        published_package.document_id
        != package.document_id
    ):
        raise RuntimeError(
            "Firestore document_id mismatch."
        )

    if (
        len(published_package.chapters)
        != len(package.chapters)
    ):
        raise RuntimeError(
            "Chapter count mismatch."
        )

    if (
        len(published_package.sections)
        != len(package.sections)
    ):
        raise RuntimeError(
            "Section count mismatch."
        )

    if (
        len(published_package.concepts)
        != len(package.concepts)
    ):
        raise RuntimeError(
            "Concept count mismatch."
        )

    print(
        "   PASS: Firestore verification"
    )

    # ==============================================================
    # IMPORTANT:
    #
    # There is intentionally NO DELETE here.
    #
    # This package is being permanently published for
    # MathVerse consumption.
    # ==============================================================

    print()
    print(
        "=================================================="
    )
    print(
        "Knowledge Factory publish: PASS"
    )
    print(
        "=================================================="
    )
    print()
    print(
        "Published document:"
    )
    print(
        f"  {package.document_id}"
    )
    print()
    print(
        "The Firestore document was intentionally NOT deleted."
    )
    print(
        "It is now available for MathVerse consumption."
    )


if __name__ == "__main__":
    main()