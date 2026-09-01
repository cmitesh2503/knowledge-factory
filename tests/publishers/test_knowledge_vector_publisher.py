from __future__ import annotations

from unittest.mock import Mock

from services.publishers.knowledge_vector_publisher import (
    KnowledgeVectorPublisher,
)


def create_package():

    package = Mock()

    package.document_id = "doc-001"

    return package


def test_publisher_indexes_any_knowledge_package():

    vector_indexing_service = Mock()

    vector_indexing_service.index.return_value = 3

    publisher = (
        KnowledgeVectorPublisher(
            vector_indexing_service=(
                vector_indexing_service
            )
        )
    )

    package = create_package()

    result = publisher.publish(
        package
    )

    vector_indexing_service.index.assert_called_once_with(
        package
    )

    assert result == 3


def test_publisher_rejects_empty_document_id():

    vector_indexing_service = Mock()

    publisher = (
        KnowledgeVectorPublisher(
            vector_indexing_service=(
                vector_indexing_service
            )
        )
    )

    package = Mock()

    package.document_id = ""

    try:

        publisher.publish(
            package
        )

        assert False, (
            "Expected ValueError"
        )

    except ValueError as exc:

        assert (
            str(exc)
            == "KnowledgePackage.document_id "
            "cannot be empty"
        )

    vector_indexing_service.index.assert_not_called()


def test_publisher_does_not_know_document_type():

    vector_indexing_service = Mock()

    vector_indexing_service.index.return_value = 5

    publisher = (
        KnowledgeVectorPublisher(
            vector_indexing_service=(
                vector_indexing_service
            )
        )
    )

    package = Mock()

    package.document_id = (
        "doc-polynomials"
    )

    result = publisher.publish(
        package
    )

    vector_indexing_service.index.assert_called_once_with(
        package
    )

    assert result == 5