from __future__ import annotations

from unittest.mock import Mock

from services.publishers.knowledge_vector_publisher import (
    KnowledgeVectorPublisher,
)


def create_package():
    package = Mock()
    package.document_id = "doc-001"
    return package


def test_publisher_accepts_any_knowledge_package():

    vector_index = Mock()

    publisher = KnowledgeVectorPublisher(
        firestore_client=Mock(),
        genai_client=Mock(),
    )

    # Replace the real index with our mock.
    publisher.vector_index = vector_index

    package = create_package()

    publisher.publish(package)

    vector_index.index.assert_called_once_with(
        package
    )


def test_publisher_rejects_empty_document_id():

    publisher = KnowledgeVectorPublisher(
        firestore_client=Mock(),
        genai_client=Mock(),
    )

    package = Mock()
    package.document_id = ""

    try:
        publisher.publish(package)
        assert False, (
            "Expected ValueError"
        )
    except ValueError as exc:
        assert (
            str(exc)
            == "KnowledgePackage.document_id "
            "cannot be empty"
        )


def test_publisher_does_not_know_document_type():

    vector_index = Mock()

    publisher = KnowledgeVectorPublisher(
        firestore_client=Mock(),
        genai_client=Mock(),
    )

    publisher.vector_index = vector_index

    package = Mock()

    package.document_id = (
        "doc-polynomials"
    )

    publisher.publish(package)

    vector_index.index.assert_called_once_with(
        package
    )