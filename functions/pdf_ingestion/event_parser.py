"""
Cloud Storage Event parser.

Responsible for:
- Parsing CloudEvent
- Validating required fields
- Returning a strongly typed event object
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class StorageEvent:
    bucket: str
    object_name: str
    generation: str | None


def parse_storage_event(cloud_event) -> StorageEvent:
    """
    Parse and validate a Cloud Storage finalized event.
    """

    data = cloud_event.data

    bucket = data.get("bucket")
    object_name = data.get("name")
    generation = data.get("generation")

    if not bucket:
        raise ValueError("Missing bucket in CloudEvent.")

    if not object_name:
        raise ValueError("Missing object name in CloudEvent.")

    return StorageEvent(
        bucket=bucket,
        object_name=object_name,
        generation=generation,
    )