"""
Utilities for persisting Google Document AI responses
as reusable JSON test artifacts.
"""

import json
from pathlib import Path

from google.protobuf.json_format import MessageToDict


def save_document_ai_response(
    response,
    output_file: str | Path,
) -> Path:
    """
    Save a Google Document AI ProcessResponse as JSON.

    The saved JSON is a replay/test artifact so that
    downstream processing can be tested without calling
    Document AI again.
    """

    output_path = Path(output_file)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    response_dict = MessageToDict(
        response._pb,
        preserving_proto_field_name=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            response_dict,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return output_path