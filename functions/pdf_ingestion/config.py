"""
Configuration module for Knowledge Factory Ingestion Cloud Function.

Responsibilities
----------------
- Read environment variables
- Validate required configuration
- Expose configuration through a strongly typed object

This module should NOT contain any business logic.
"""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    """Application configuration."""

    project_id: str
    region: str

    raw_bucket: str
    processed_bucket: str
    firestore_database: str

    document_ai_location: str
    document_ai_processor: str

    max_chunk_pages: int


def _require_env(name: str) -> str:
    """
    Return a required environment variable.

    Raises:
        RuntimeError:
            If the environment variable is missing.
    """

    value = os.getenv(name)

    if value is None or value.strip() == "":
        raise RuntimeError(
            f"Required environment variable '{name}' is missing."
        )

    return value.strip()


def _optional_positive_int(
    name: str,
    default: int,
) -> int:
    """
    Read an optional positive integer environment variable.

    Uses the supplied default when the variable is not set.

    Raises:
        RuntimeError:
            If the value is not a valid positive integer.
    """

    value = os.getenv(name)

    if value is None or value.strip() == "":
        return default

    try:
        parsed = int(value.strip())
    except ValueError as exc:
        raise RuntimeError(
            f"Environment variable '{name}' "
            "must be a positive integer."
        ) from exc

    if parsed < 1:
        raise RuntimeError(
            f"Environment variable '{name}' "
            "must be greater than zero."
        )

    return parsed


def load_settings() -> Settings:
    """
    Load and validate application settings.

    Returns
    -------
    Settings
        Immutable application configuration.
    """

    return Settings(
        project_id=_require_env("PROJECT_ID"),
        region=_require_env("REGION"),

        raw_bucket=_require_env("RAW_BUCKET"),
        processed_bucket=_require_env("PROCESSED_BUCKET"),
        firestore_database=_require_env(
            "FIRESTORE_DATABASE"
        ),

        document_ai_location=_require_env(
            "DOCUMENT_AI_LOCATION"
        ),
        document_ai_processor=_require_env(
            "DOCUMENT_AI_PROCESSOR"
        ),

        max_chunk_pages=_optional_positive_int(
            "MAX_CHUNK_PAGES",
            25,
        ),
    )
