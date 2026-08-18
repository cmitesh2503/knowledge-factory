from services.models.knowledge_package import (
    KnowledgePackage,
)

from services.repositories.firestore_knowledge_package_repository import (
    FirestoreKnowledgePackageRepository,
)


class FakeSnapshot:

    def __init__(
        self,
        data: dict | None,
    ) -> None:
        self._data = data

    @property
    def exists(self) -> bool:
        return self._data is not None

    def to_dict(self) -> dict | None:
        return self._data


class FakeDocument:

    def __init__(
        self,
        storage: dict,
        document_id: str,
    ) -> None:
        self.storage = storage
        self.document_id = document_id

    def set(
        self,
        data: dict,
    ) -> None:
        self.storage[
            self.document_id
        ] = data

    def get(self) -> FakeSnapshot:
        return FakeSnapshot(
            self.storage.get(
                self.document_id
            )
        )


class FakeCollection:

    def __init__(
        self,
        storage: dict,
    ) -> None:
        self.storage = storage

    def document(
        self,
        document_id: str,
    ) -> FakeDocument:
        return FakeDocument(
            self.storage,
            document_id,
        )


class FakeFirestoreClient:

    def __init__(self) -> None:
        self.storage: dict[str, dict] = {}

    def collection(
        self,
        name: str,
    ) -> FakeCollection:
        return FakeCollection(
            self.storage.setdefault(
                name,
                {},
            )
        )


def test_firestore_repository_saves_package():

    client = FakeFirestoreClient()

    repository = (
        FirestoreKnowledgePackageRepository(
            client=client
        )
    )

    package = KnowledgePackage(
        schema_version="1.0",
        document_id="doc-matrices-001",
        metadata={
            "filename": "Matrices-1-10.pdf",
        },
    )

    repository.save(package)

    stored = client.storage[
        "knowledge_packages"
    ]["doc-matrices-001"]

    assert stored["document_id"] == (
        "doc-matrices-001"
    )

    assert stored["schema_version"] == "1.0"

    assert stored["metadata"]["filename"] == (
        "Matrices-1-10.pdf"
    )


def test_firestore_repository_get_missing_package():

    client = FakeFirestoreClient()

    repository = (
        FirestoreKnowledgePackageRepository(
            client=client
        )
    )

    result = repository.get(
        "does-not-exist"
    )

    assert result is None


def test_firestore_repository_get_package():

    client = FakeFirestoreClient()

    repository = (
        FirestoreKnowledgePackageRepository(
            client=client
        )
    )

    package = KnowledgePackage(
        schema_version="1.0",
        document_id="doc-matrices-001",
        metadata={
            "filename": "Matrices-1-10.pdf",
        },
    )

    repository.save(package)

    result = repository.get(
        "doc-matrices-001"
    )

    assert result is not None
    assert result.document_id == (
        "doc-matrices-001"
    )
    assert result.schema_version == "1.0"
    assert result.metadata["filename"] == (
        "Matrices-1-10.pdf"
    )
    
from services.models.chapter import Chapter
from services.models.concept import Concept
from services.models.example import Example
from services.models.exercise import (
    Exercise,
    ExerciseQuestion,
)
from services.models.figure import Figure
from services.models.formula import Formula
from services.models.knowledge_package import (
    KnowledgePackage,
)
from services.models.section import Section


def test_firestore_repository_round_trip_preserves_entities():

    client = FakeFirestoreClient()

    repository = (
        FirestoreKnowledgePackageRepository(
            client=client
        )
    )

    package = KnowledgePackage(
        schema_version="1.0",
        document_id="doc-roundtrip-001",

        chapters=[
            Chapter(
                id="chapter-1",
                number=3,
                title="Matrices",
                start_page=1,
                end_page=10,
                block_ids=["block-1"],
            )
        ],

        sections=[
            Section(
                id="section-1",
                number="3.1",
                title="Introduction",
                level=2,
                parent_number=None,
                page=1,
                block_id="block-2",
            )
        ],

        concepts=[
            Concept(
                id="concept-1",
                name="Matrix",
                section_number="3.2",
                page=2,
                block_id="block-3",
            )
        ],

        formulas=[
            Formula(
                id="formula-1",
                expression="A + B",
                section_number="3.4",
                page=5,
                block_id="block-4",
            )
        ],

        examples=[
            Example(
                id="example-1",
                number="3.1",
                title="Matrix Example",
                content=[
                    "Let A be a matrix."
                ],
                section_number="3.2",
                page=3,
                block_id="block-5",
            )
        ],

        exercises=[
            Exercise(
                id="exercise-1",
                number="3.1",
                section_number="3.2",
                page=8,
                block_id="block-6",
                questions=[
                    ExerciseQuestion(
                        number="1",
                        question="Find the order.",
                        block_id="block-7",
                        page=8,
                    )
                ],
            )
        ],

        figures=[
            Figure(
                id="figure-1",
                caption="Matrix illustration",
                description="Illustration of a matrix.",
                related_concepts=[
                    "concept-1"
                ],
            )
        ],

        metadata={
            "filename": "Matrices-1-10.pdf"
        },
    )

    repository.save(package)

    restored = repository.get(
        "doc-roundtrip-001"
    )

    assert restored is not None

    assert restored.to_dict() == (
        package.to_dict()
    )
    assert restored.to_dict() == package.to_dict()