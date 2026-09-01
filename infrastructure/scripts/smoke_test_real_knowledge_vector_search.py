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

from services.vector.gemini_embedding_provider import (
    GeminiEmbeddingProvider,
)
from services.vector.knowledge_chunk_builder import (
    KnowledgeChunkBuilder,
)
from services.vector.knowledge_search_service import (
    KnowledgeSearchService,
)
from services.vector.vector_indexing_service import (
    VectorIndexingService,
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

    print(
        "1. Loading real Matrices fixture..."
    )

    with FIXTURE_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:

        azure_document = json.load(
            file
        )

    print(
        "   PASS: fixture loaded"
    )

    print(
        "2. Building canonical blocks..."
    )

    blocks = (
        AzureProcessor().process(
            azure_document
        )
    )

    print(
        f"   PASS: {len(blocks)} "
        "canonical blocks"
    )

    print(
        "3. Building Canonical Document..."
    )

    analyze_result = (
        azure_document.get(
            "analyzeResult",
            {},
        )
    )

    pages = (
        analyze_result.get(
            "pages",
            [],
        )
    )

    canonical_document = (
        CanonicalDocumentBuilder().build(
            blocks=blocks,
            page_count=len(pages),
            filename=(
                "Matrices-1-10.pdf"
            ),
            raw_bucket=(
                "knowledge-factory"
            ),
            raw_object=(
                "Matrices-1-10.pdf"
            ),
            generation="1",
        )
    )

    print(
        "   PASS: canonical document built"
    )

    print(
        "4. Building KnowledgePackage..."
    )

    package = (
        KnowledgePackageBuilder().build(
            canonical_document
        )
    )

    print(
        f"   PASS: "
        f"{len(package.concepts)} "
        "concepts"
    )

    return package


def main():

    package = build_real_package()

    print()

    print(
        "5. Creating Vertex AI "
        "GenAI client..."
    )

    genai_client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="global",
    )

    print(
        "   PASS: GenAI client created"
    )

    print()

    print(
        "6. Creating Firestore client..."
    )

    firestore_client = firestore.Client(
        project=PROJECT_ID
    )

    print(
        "   PASS: Firestore client created"
    )

    print()

    print(
        "7. Creating embedding provider..."
    )

    embedding_provider = (
        GeminiEmbeddingProvider(
            client=genai_client,
            embedding_model=(
                EMBEDDING_MODEL
            ),
            embedding_dimensions=(
                EMBEDDING_DIMENSIONS
            ),
        )
    )

    print(
        "   PASS: embedding provider created"
    )

    print()

    print(
        "8. Creating Firestore "
        "vector index..."
    )

    vector_index = (
        FirestoreVectorIndex(
            client=firestore_client,
            collection_name=(
                COLLECTION_NAME
            ),
        )
    )

    print(
        "   PASS: vector index created"
    )

    print()

    print(
        "9. Creating vector "
        "indexing service..."
    )

    chunk_builder = (
        KnowledgeChunkBuilder()
    )

    indexing_service = (
        VectorIndexingService(
            embedding_provider=(
                embedding_provider
            ),
            vector_index=(
                vector_index
            ),
            chunk_builder=(
                chunk_builder
            ),
        )
    )

    print(
        "   PASS: indexing service created"
    )

    print()

    print(
        "10. Building semantic "
        "search chunks..."
    )

    chunks = (
        chunk_builder.build(
            package
        )
    )

    print(
        f"   PASS: "
        f"{len(chunks)} chunks built"
    )

    assert chunks

    print()

    print(
        "11. Indexing real "
        "Matrices knowledge..."
    )

    indexed_count = (
        indexing_service.index(
            package
        )
    )

    assert (
        indexed_count
        == len(chunks)
    )

    print(
        f"   PASS: "
        f"{indexed_count} chunks indexed"
    )

    print()

    print(
        "12. Creating knowledge "
        "search service..."
    )

    search_service = (
        KnowledgeSearchService(
            embedding_provider=(
                embedding_provider
            ),
            vector_index=(
                vector_index
            ),
        )
    )

    print(
        "   PASS: knowledge "
        "search service created"
    )

    print()

    print(
        "13. Running real "
        "vector search..."
    )

    query = (
        "What is a matrix?"
    )

    print(
        f"   query: {query!r}"
    )

    results = (
        search_service.search(
            query=query,
            limit=3,
        )
    )

    print(
        f"   PASS: "
        f"{len(results)} "
        "results returned"
    )

    if not results:

        raise AssertionError(
            "Firestore Vector Search "
            "returned no results."
        )

    print()

    print(
        "14. Inspecting search "
        "results..."
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
            f"{result.document_id}"
        )

        print(
            f"source_id   : "
            f"{result.source_id}"
        )

        print(
            f"type        : "
            f"{result.knowledge_type}"
        )

        print(
            f"distance    : "
            f"{result.distance}"
        )

        print(
            f"text        : "
            f"{result.text}"
        )

        print()

    print(
        "15. Verifying result "
        "relevance..."
    )

    top_result = results[0]

    assert (
        top_result.document_id
        == package.document_id
    )

    assert (
        top_result.knowledge_type
        == "concept"
    )

    assert top_result.text

    print(
        "   PASS: top result "
        "belongs to the Matrices "
        "KnowledgePackage"
    )

    print()

    print(
        "16. Cleaning up vector "
        "documents..."
    )

    collection = (
        firestore_client.collection(
            COLLECTION_NAME
        )
    )

    indexed_documents = []

    for chunk in chunks:

        vector_document_id = (
            vector_index._document_id(
                document_id=(
                    package.document_id
                ),
                source_id=(
                    chunk["id"]
                ),
            )
        )

        collection.document(
            vector_document_id
        ).delete()

        indexed_documents.append(
            vector_document_id
        )

    print(
        "   PASS: vector "
        "documents deleted"
    )

    print()

    print(
        "17. Verifying cleanup..."
    )

    for document_id in indexed_documents:

        snapshot = (
            collection
            .document(
                document_id
            )
            .get()
        )

        assert (
            not snapshot.exists
        )

    print(
        "   PASS: cleanup verified"
    )

    print()

    print(
        "Real Firestore Vector "
        "Search smoke test: PASS"
    )


if __name__ == "__main__":

    main()