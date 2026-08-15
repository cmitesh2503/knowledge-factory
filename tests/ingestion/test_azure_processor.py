import json

from functions.pdf_ingestion.azure_processor import (
    AzureProcessor,
)


def test_azure_processor_extracts_paragraphs():

    with open(
        "tests/fixtures/Matrices-1-10.pdf.json",
        encoding="utf-8",
    ) as f:
        document = json.load(f)

    processor = AzureProcessor()

    blocks = processor.process(document)

    assert len(blocks) > 0

    assert blocks[0]["type"] in {
        "paragraph",
        "heading",
        "text",
    }

    assert blocks[0]["text"]

    assert blocks[0]["page"] >= 1