from google.cloud.firestore_v1.vector import (
    Vector,
)

from services.vector.firestore_vector_index import (
    FirestoreVectorIndex,
)


class FakeDocumentReference:

    def __init__(
        self,
        document_id: str,
        storage: dict,
    ) -> None:

        self.document_id = (
            document_id
        )

        self.storage = storage

    def set(
        self,
        data: dict,
    ) -> None:

        self.storage[
            self.document_id
        ] = data


class FakeSnapshot:

    def __init__(
        self,
        document_id: str,
        data: dict,
    ) -> None:

        self.id = document_id
        self._data = data

    def to_dict(
        self,
    ) -> dict:

        return self._data


class FakeVectorQuery:

    def __init__(
        self,
        documents: list[
            FakeSnapshot
        ],
    ) -> None:

        self.documents = documents
        self.stream_called = False

    def stream(
        self,
    ):

        self.stream_called = True

        return iter(
            self.documents
        )


class FakeCollection:

    def __init__(
        self,
    ) -> None:

        self.documents = {}

        self.find_nearest_called = False

        self.last_query_vector = None

        self.last_limit = None

        self.vector_query = None

    def document(
        self,
        document_id: str,
    ) -> FakeDocumentReference:

        return FakeDocumentReference(
            document_id,
            self.documents,
        )

    def find_nearest(
        self,
        *,
        vector_field: str,
        query_vector,
        distance_measure,
        limit: int,
        distance_result_field: str,
    ) -> FakeVectorQuery:

        self.find_nearest_called = True

        self.last_query_vector = (
            query_vector
        )

        self.last_limit = limit

        assert (
            vector_field
            == "embedding"
        )

        assert (
            distance_result_field
            == "vector_distance"
        )

        self.vector_query = (
            FakeVectorQuery(
                [
                    FakeSnapshot(
                        "vec-result-001",
                        {
                            "id": (
                                "concept-001"
                            ),
                            "text": (
                                "A matrix is a "
                                "rectangular array."
                            ),
                            "knowledge_type": (
                                "concept"
                            ),
                            "metadata": {
                                "document_id": (
                                    "document-001"
                                ),
                                "page": 10,
                            },
                            "vector_distance": (
                                0.12
                            ),
                        },
                    )
                ]
            )
        )

        return (
            self.vector_query
        )


class FakeFirestoreClient:

    def __init__(
        self,
    ) -> None:

        self.collections = {}

    def collection(
        self,
        name: str,
    ) -> FakeCollection:

        if (
            name
            not in self.collections
        ):

            self.collections[
                name
            ] = (
                FakeCollection()
            )

        return self.collections[
            name
        ]


def create_index():

    client = (
        FakeFirestoreClient()
    )

    index = (
        FirestoreVectorIndex(
            client=client,
        )
    )

    return (
        index,
        client,
    )


def test_firestore_vector_index_upserts_record():

    index, client = (
        create_index()
    )

    index.upsert(
        [
            {
                "id": (
                    "concept-001"
                ),
                "vector": [
                    0.1,
                    0.2,
                    0.3,
                ],
                "text": (
                    "A matrix is a "
                    "rectangular array."
                ),
                "knowledge_type": (
                    "concept"
                ),
                "metadata": {
                    "document_id": (
                        "document-001"
                    ),
                    "page": 10,
                },
            }
        ]
    )

    collection = (
        client.collections[
            "knowledge_vectors"
        ]
    )

    assert (
        len(
            collection.documents
        )
        == 1
    )

    stored_document = next(
        iter(
            collection.documents.values()
        )
    )

    assert (
        stored_document["id"]
        == "concept-001"
    )

    assert (
        stored_document[
            "text"
        ]
        == (
            "A matrix is a "
            "rectangular array."
        )
    )

    assert (
        stored_document[
            "knowledge_type"
        ]
        == "concept"
    )

    assert (
        stored_document[
            "metadata"
        ]["document_id"]
        == "document-001"
    )

    assert isinstance(
        stored_document[
            "embedding"
        ],
        Vector,
    )


def test_firestore_vector_index_searches():

    index, client = (
        create_index()
    )

    results = index.search(
        vector=[
            0.1,
            0.2,
            0.3,
        ],
        limit=5,
    )

    collection = (
        client.collections[
            "knowledge_vectors"
        ]
    )

    assert (
        collection.find_nearest_called
    )

    assert (
        collection.last_limit
        == 5
    )

    assert (
        collection.vector_query
        is not None
    )

    assert (
        collection.vector_query
        .stream_called
    )

    assert (
        len(results)
        == 1
    )

    result = results[0]

    assert (
        result["id"]
        == "concept-001"
    )

    assert (
        result["knowledge_type"]
        == "concept"
    )

    assert (
        result["text"]
        == (
            "A matrix is a "
            "rectangular array."
        )
    )

    assert (
        result["distance"]
        == 0.12
    )

    assert (
        result["metadata"][
            "document_id"
        ]
        == "document-001"
    )


def test_firestore_vector_index_rejects_invalid_record():

    index, _ = (
        create_index()
    )

    try:

        index.upsert(
            [
                {
                    "id": (
                        "concept-001"
                    ),
                    "vector": [
                        0.1,
                    ],
                    "text": (
                        "Matrix"
                    ),
                    "knowledge_type": (
                        "concept"
                    ),
                    "metadata": {},
                }
            ]
        )

        assert False, (
            "Expected ValueError"
        )

    except ValueError as exc:

        assert (
            "document_id"
            in str(exc)
        )


def test_firestore_vector_index_rejects_empty_search_vector():

    index, _ = (
        create_index()
    )

    try:

        index.search(
            vector=[],
        )

        assert False, (
            "Expected ValueError"
        )

    except ValueError as exc:

        assert (
            "vector"
            in str(exc).lower()
        )


def test_firestore_vector_index_rejects_invalid_limit():

    index, _ = (
        create_index()
    )

    try:

        index.search(
            vector=[
                0.1,
            ],
            limit=0,
        )

        assert False, (
            "Expected ValueError"
        )

    except ValueError as exc:

        assert (
            "limit"
            in str(exc)
        )