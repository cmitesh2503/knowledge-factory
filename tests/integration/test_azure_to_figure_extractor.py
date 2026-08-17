import json

from functions.pdf_ingestion.azure_processor import AzureProcessor
from functions.pdf_ingestion.canonical_document_builder import (
    CanonicalDocumentBuilder,
)
from services.extractors.figure_extractor import FigureExtractor


def test_azure_to_figure_extractor():

    with open(
        "tests/fixtures/Matrices-1-10.pdf.json",
        encoding="utf-8",
    ) as f:
        azure_document = json.load(f)

    # Azure JSON → canonical blocks
    blocks = AzureProcessor().process(
        azure_document
    )

    assert len(
        [
            block
            for block in blocks
            if block["type"] == "figure"
        ]
    ) == 2

    # Canonical blocks → canonical document
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

    # Canonical document → figures
    figures = FigureExtractor().extract(
        canonical_document
    )

    assert len(figures) == 2

    assert figures[0].metadata[
        "figure_id"
    ] == "1.1"

    assert figures[0].metadata[
        "page"
    ] == 1

    assert figures[1].metadata[
        "figure_id"
    ] == "2.1"

    assert figures[1].metadata[
        "page"
    ] == 2