from __future__ import annotations

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
from services.repositories.firestore_knowledge_vector_index import (
    FirestoreKnowledgeVectorIndex,
)
from services.vector.knowledge_chunk_builder import (
    KnowledgeChunkBuilder,
)


FIXTURE_PATH = (
    ROOT_DIR
    / "tests"
    / "fixtures"
    / "Matrices-1-10.pdf.json"
)


def main() -> None:

    print("1. Loading real Matrices fixture...")

    with FIXTURE_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        azure_document = json.load(file)

    print("   PASS: fixture loaded")

    print("2. Building canonical blocks...")

    processor = AzureProcessor()

    blocks = processor.process(
        azure_document
    )

    print(
        f"   PASS: {len(blocks)} canonical blocks"
    )

    print("3. Building Canonical Document...")

    analyze_result = azure_document.get(
        "analyzeResult",
        {},
    )

    pages = analyze_result.get(
        "pages",
        [],
    )

    canonical_document = (
        CanonicalDocumentBuilder().build(
            blocks=blocks,
            page_count=len(pages),
            filename="Matrices-1-10.pdf",
            raw_bucket="knowledge-factory",
            raw_object="Matrices-1-10.pdf",
            generation="1",
        )
    )

    print("   PASS: canonical document built")

    print("4. Building KnowledgePackage...")

    package = KnowledgePackageBuilder().build(
        canonical_document
    )

    print(
        f"   PASS: {len(package.concepts)} concepts"
    )

    print()
    print(
        "5. Inspecting vector-search documents..."
    )

    builder = KnowledgeChunkBuilder()

    documents = builder.build(
        package
    )

    print(
        f"   searchable documents: {len(documents)}"
    )

    if not documents:
        raise RuntimeError(
            "No searchable documents were produced."
        )

    print()

    for number, document in enumerate(
        documents,
        start=1,
    ):

        print(
            f"--- Document {number} ---"
        )

        print(
            f"type       : "
            f"{document['knowledge_type']}"
        )

        print(
            f"source_id  : "
            f"{document['id']}"
        )

        print(
            f"text       : "
            f"{document['text']!r}"
        )

        print(
            f"metadata   : "
            f"{document['metadata']}"
        )

        print()

    print(
        "2G.2.2 searchable-text inspection: PASS"
    )


if __name__ == "__main__":
    main()