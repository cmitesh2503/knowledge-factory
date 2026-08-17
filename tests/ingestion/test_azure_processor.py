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
    
def test_azure_processor_extracts_figures():

    with open(
        "tests/fixtures/Matrices-1-10.pdf.json",
        encoding="utf-8",
    ) as f:
        document = json.load(f)

    processor = AzureProcessor()

    blocks = processor.process(document)

    figure_blocks = [
        block
        for block in blocks
        if block["type"] == "figure"
    ]

    assert len(figure_blocks) == 2

    first = figure_blocks[0]

    assert first["metadata"]["figure_id"] == "1.1"
    assert first["page"] == 1
    assert first["metadata"]["elements"]

    second = figure_blocks[1]

    assert second["metadata"]["figure_id"] == "2.1"
    assert second["page"] == 2
    assert second["metadata"]["elements"]
    
def test_azure_processor_extracts_tables():

    with open(
        "tests/fixtures/Matrices-1-10.pdf.json",
        encoding="utf-8",
    ) as f:
        document = json.load(f)

    processor = AzureProcessor()

    blocks = processor.process(document)

    table_blocks = [
        block
        for block in blocks
        if block["type"] == "table"
    ]

    assert len(table_blocks) == 2

    first = table_blocks[0]

    assert first["page"] == 2
    assert first["metadata"]["row_count"] == 3
    assert first["metadata"]["column_count"] == 6
    assert len(first["metadata"]["cells"]) == 18

    assert (
        first["metadata"]["cells"][0]["content"]
        == "Radha"
    )

    second = table_blocks[1]

    assert second["page"] == 2
    assert second["metadata"]["row_count"] == 4
    assert second["metadata"]["column_count"] == 3
    assert len(second["metadata"]["cells"]) == 12

    header_cells = [
        cell
        for cell in second["metadata"]["cells"]
        if cell["kind"] == "columnHeader"
    ]

    assert len(header_cells) == 3