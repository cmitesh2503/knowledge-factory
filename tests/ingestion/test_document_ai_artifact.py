from google.cloud import documentai

from functions.pdf_ingestion.document_ai_artifact import (
    save_document_ai_response,
)


def test_document_ai_response_is_saved_as_json(
    tmp_path,
):

    response = documentai.ProcessResponse()

    output_file = (
        tmp_path
        / "document_ai.json"
    )

    result = save_document_ai_response(
        response=response,
        output_file=output_file,
    )

    assert result == output_file

    assert output_file.exists()

    assert output_file.stat().st_size > 0