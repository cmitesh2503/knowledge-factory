"""
Common utility functions for Knowledge Factory Ingestion.
"""

import os
import tempfile


def get_temp_file_path(file_name: str) -> str:
    """
    Return the full temporary file path.
    """
    return os.path.join(
        tempfile.gettempdir(),
        os.path.basename(file_name),
    )


def delete_file(file_path: str) -> None:
    """
    Delete a temporary file if it exists.
    """
    if file_path and os.path.exists(file_path):
        os.remove(file_path)


def get_file_size(file_path: str) -> int:
    """
    Return file size in bytes.
    """
    return os.path.getsize(file_path)