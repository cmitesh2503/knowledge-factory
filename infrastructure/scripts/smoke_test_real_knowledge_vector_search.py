from __future__ import annotations

import json
import sys
from pathlib import Path

from google import genai
from google.cloud import firestore


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


PROJECT_ID = "knowledge-factory-prod"

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768

COLLECTION_NAME = "knowledge_vectors"

FIXTURE_PATH = (
    ROOT_DIR
    / "tests"
    / "fixtures"
    / "Matrices-1-10.pdf.json"
)


def build_real_package():

    print("1. Loading real Matrices fixture...")

    with FIXTURE_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        azure_document = json.load(file)

    print("   PASS: fixture loaded")

    print("2. Building canonical blocks...")

    blocks = AzureProcessor().process(
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

    return package


def main():

    package = build_real_package()

    print()
    print(
        "5. Building semantic search chunks..."
    )

    chunks = KnowledgeChunkBuilder().build(
        package
    )

    print(
        f"   PASS: {len(chunks)} chunks"
    )

    print()
    print(
        "6. Creating Vertex AI GenAI client..."
    )

    genai_client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="global",
    )

    print("   PASS: GenAI client created")

    print()
    print(
        "7. Creating Firestore client..."
    )

    firestore_client = firestore.Client(
        project=PROJECT_ID
    )

    print("   PASS: Firestore client created")

    vector_index = (
        FirestoreKnowledgeVectorIndex(
            client=firestore_client,
            genai_client=genai_client,
            embedding_model=EMBEDDING_MODEL,
            embedding_dimensions=(
                EMBEDDING_DIMENSIONS
            ),
        )
    )

    print()
    print(
        "8. Indexing real Matrices knowledge..."
    )

    vector_index.index(package)

    print(
        "   PASS: vector indexing completed"
    )

    print()
    print(
        "9. Running real vector search..."
    )

    query = "What is a matrix?"

    print(
        f"   query: {query!r}"
    )

    results = vector_index.search(
        query,
        top_k=3,
    )

    print(
        f"   PASS: {len(results)} results returned"
    )

    if not results:
        raise AssertionError(
            "Firestore Vector Search returned "
            "no results."
        )

    print()
    print(
        "10. Inspecting search results..."
    )

    for number, result in enumerate(
        results,
        start=1,
    ):

        print(
            f"--- Result {number} ---"
        )

        print(
            f"document_id : "
            f"{result['document_id']}"
        )

        print(
            f"source_id   : "
            f"{result['source_id']}"
        )

        print(
            f"type        : "
            f"{result['knowledge_type']}"
        )

        print(
            f"distance    : "
            f"{result['distance']}"
        )

        print(
            f"text        : "
            f"{result['text']}"
        )

        print()

    print(
        "11. Verifying result relevance..."
    )

    top_result = results[0]

    assert (
        top_result["document_id"]
        == package.document_id
    )

    assert (
        top_result["knowledge_type"]
        == "concept"
    )

    assert top_result["text"]

    print(
        "   PASS: top result belongs to "
        "the Matrices KnowledgePackage"
    )

    print()
    print(
        "12. Cleaning up vector documents..."
    )

    collection = firestore_client.collection(
        COLLECTION_NAME
    )

    for chunk in chunks:

        vector_document_id = (
            vector_index._vector_document_id(
                package.document_id,
                chunk["id"],
            )
        )

        collection.document(
            vector_document_id
        ).delete()

    print(
        "   PASS: vector documents deleted"
    )

    print()
    print(
        "13. Verifying cleanup..."
    )

    for chunk in chunks:

        vector_document_id = (
            vector_index._vector_document_id(
                package.document_id,
                chunk["id"],
            )
        )

        snapshot = (
            collection
            .document(vector_document_id)
            .get()
        )

        assert not snapshot.exists

    print(
        "   PASS: cleanup verified"
    )

    print()
    print(
        "Real Firestore Vector Search smoke test: PASS"
    )


if __name__ == "__main__":
    main()