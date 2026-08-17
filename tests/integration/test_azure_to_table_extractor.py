import json

from functions.pdf_ingestion.azure_processor import AzureProcessor
from functions.pdf_ingestion.canonical_document_builder import (
    CanonicalDocumentBuilder,
)
from services.extractors.table_extractor import TableExtractor


def test_azure_to_table_extractor():

    with open(
        "tests/fixtures/Matrices-1-10.pdf.json",
        encoding="utf-8",
    ) as f:
        azure_document = json.load(f)

    blocks = AzureProcessor().process(
        azure_document
    )

    table_blocks = [
        block
        for block in blocks
        if block["type"] == "table"
    ]

    assert len(table_blocks) == 2

    canonical_document = (
        CanonicalDocumentBuilder().build(
            blocks=blocks,
            page_count=len(
                azure_document[
                    "analyzeResult"
                ]["pages"]
            ),
            filename="Matrices-1-10.pdf",
            raw_bucket="test-bucket",
            raw_object="test/Matrices-1-10.pdf",
            generation="1",
        )
    )

    tables = TableExtractor().extract(
        canonical_document
    )

    assert len(tables) == 2

    assert tables[0].rows == 3
    assert tables[0].columns == 6
    assert len(tables[0].cells) == 18
    assert tables[0].cells[0]["content"] == "Radha"

    assert tables[1].rows == 4
    assert tables[1].columns == 3
    assert len(tables[1].cells) == 12

    header_cells = [
        cell
        for cell in tables[1].cells
        if cell["kind"] == "columnHeader"
    ]

    assert len(header_cells) == 3