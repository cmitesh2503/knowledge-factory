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


def _require_env(name: str) -> str:
    """
    Return an environment variable.

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
        firestore_database=_require_env("FIRESTORE_DATABASE"),

        document_ai_location=_require_env("DOCUMENT_AI_LOCATION"),
        document_ai_processor=_require_env("DOCUMENT_AI_PROCESSOR"),
    )
