from __future__ import annotations

import sys
from pathlib import Path

from google import genai
from google.cloud import firestore


ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from infrastructure.scripts.smoke_test_real_knowledge_vector_search import (
    build_real_package,
)
from services.publishers.knowledge_vector_publisher import (
    KnowledgeVectorPublisher,
)
from services.vector.firestore_vector_index import (
    FirestoreVectorIndex,
)
from services.vector.gemini_embedding_provider import (
    GeminiEmbeddingProvider,
)
from services.vector.knowledge_chunk_builder import (
    KnowledgeChunkBuilder,
)
from services.vector.vector_indexing_service import (
    VectorIndexingService,
)


PROJECT_ID = "knowledge-factory-prod"

EMBEDDING_MODEL = "gemini-embedding-001"

EMBEDDING_DIMENSIONS = 768

COLLECTION_NAME = "knowledge_vectors"


def main():

    print(
        "1. Building real Matrices KnowledgePackage..."
    )

    package = build_real_package()

    print(
        f"   PASS: package built "
        f"document_id={package.document_id}"
    )

    print()
    print(
        "2. Creating Vertex AI GenAI client..."
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
        "3. Creating Firestore client..."
    )

    firestore_client = firestore.Client(
        project=PROJECT_ID
    )

    print(
        "   PASS: Firestore client created"
    )

    print()
    print(
        "4. Creating vector infrastructure..."
    )

    embedding_provider = (
        GeminiEmbeddingProvider(
            client=genai_client,
            embedding_model=EMBEDDING_MODEL,
            embedding_dimensions=(
                EMBEDDING_DIMENSIONS
            ),
        )
    )

    vector_index = (
        FirestoreVectorIndex(
            client=firestore_client,
            collection_name=COLLECTION_NAME,
        )
    )

    chunk_builder = (
        KnowledgeChunkBuilder()
    )

    vector_indexing_service = (
        VectorIndexingService(
            embedding_provider=(
                embedding_provider
            ),
            vector_index=vector_index,
            chunk_builder=chunk_builder,
        )
    )

    publisher = (
        KnowledgeVectorPublisher(
            vector_indexing_service=(
                vector_indexing_service
            )
        )
    )

    print(
        "   PASS: publisher created"
    )

    print()
    print(
        "5. Publishing Matrices vectors..."
    )

    indexed_count = publisher.publish(
        package
    )

    print(
        f"   PASS: "
        f"{indexed_count} vectors published "
        f"to Firestore"
    )

    print()
    print(
        "6. Verifying persistent vector documents..."
    )

    collection = firestore_client.collection(
        COLLECTION_NAME
    )

    snapshots = list(
        collection.stream()
    )

    matching_documents = []

    for snapshot in snapshots:

        data = snapshot.to_dict() or {}

        metadata = data.get(
            "metadata",
            {},
        )

        if (
            metadata.get("document_id")
            == package.document_id
        ):
            matching_documents.append(
                data
            )

    print(
        f"   PASS: "
        f"{len(matching_documents)} "
        f"vector documents found"
    )

    if not matching_documents:
        raise AssertionError(
            "No persistent vector documents "
            "were found."
        )

    for number, data in enumerate(
        matching_documents,
        start=1,
    ):

        metadata = data.get(
            "metadata",
            {},
        )

        print(
            f"--- Vector {number} ---"
        )

        print(
            f"id        : "
            f"{data.get('id')}"
        )

        print(
            f"type      : "
            f"{data.get('knowledge_type')}"
        )

        print(
            f"text      : "
            f"{data.get('text', '')[:120]}..."
        )

        print(
            f"document  : "
            f"{metadata.get('document_id')}"
        )

        embedding = data.get(
            "embedding"
        )

        if embedding is None:
            raise AssertionError(
                "Vector document is missing "
                "embedding."
            )

    print()
    print(
        "Persistent Matrices vector "
        "publication: PASS"
    )

    print()
    print(
        "IMPORTANT: vector documents "
        "were NOT deleted."
    )


if __name__ == "__main__":
    main()