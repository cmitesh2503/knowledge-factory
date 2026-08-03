"""
Firestore metadata service.

Writes processing metadata for canonical documents. The canonical JSON
itself remains in Cloud Storage.
"""

from google.cloud import firestore


class FirestoreMetadataService:
    """Wrapper around Firestore document metadata writes."""

    COLLECTION_NAME = "documents"

    def __init__(
        self,
        *,
        logger,
        project_id: str,
        database_name: str,
    ) -> None:
        self.logger = logger
        self.client = firestore.Client(
            project=project_id,
            database=database_name,
        )

    def write_processing_metadata(self, metadata: dict) -> str:
        """
        Write processing metadata and return the Firestore document path.
        """

        document_id = metadata["document_id"]
        document_ref = (
            self.client
            .collection(self.COLLECTION_NAME)
            .document(document_id)
        )

        document_ref.set(metadata)

        return f"{self.COLLECTION_NAME}/{document_id}"
