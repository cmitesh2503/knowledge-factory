"""
Google Cloud Storage service.
"""

from pathlib import Path
#from venv import logger

from google.cloud import storage


class StorageService:
    """Wrapper around Google Cloud Storage."""

    def __init__(self,logger) -> None:
        self.client = storage.Client()
        self.logger = logger
        
    def blob_exists(
        self,
        bucket_name: str,
        blob_name: str,
        generation: int | None = None,
    ) -> bool:
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name,
        generation=generation,)
        return blob.exists(self.client)

    def download_blob(
        self,
        bucket_name: str,
        blob_name: str,
        generation: int,
        destination_file: str,
    ) -> int | None:
        """
        Download a blob.

        Returns
        -------
        int
            Downloaded file size in bytes.
        """

        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name,
                           generation=generation,)

        if not blob.exists(self.client):
            self.logger.warning(
                "Blob no longer exists: gs://%s/%s",
                bucket_name,
                blob_name,
            )
            return None

        Path(destination_file).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        blob.download_to_filename(destination_file)

        return Path(destination_file).stat().st_size
    
    
    def upload_blob(
        self,
        bucket_name: str,
        source_file: str,
        blob_name: str,
        content_type: str = "application/json",
    ) -> None:

        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        blob.upload_from_filename(
            source_file,
            content_type=content_type,
        )