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
        "4. Creating generic KnowledgeVectorPublisher..."
    )

    publisher = KnowledgeVectorPublisher(
        firestore_client=firestore_client,
        genai_client=genai_client,
        embedding_model=EMBEDDING_MODEL,
        embedding_dimensions=EMBEDDING_DIMENSIONS,
    )

    print(
        "   PASS: publisher created"
    )

    print()
    print(
        "5. Publishing Matrices vectors..."
    )

    publisher.publish(package)

    print(
        "   PASS: vectors published to Firestore"
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

        if (
            data.get("document_id")
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

        print(
            f"--- Vector {number} ---"
        )

        print(
            f"source_id : "
            f"{data.get('source_id')}"
        )

        print(
            f"type      : "
            f"{data.get('knowledge_type')}"
        )

        print(
            f"text      : "
            f"{data.get('text', '')[:120]}..."
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