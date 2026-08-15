import json

from functions.pdf_ingestion.azure_processor import AzureProcessor
from functions.pdf_ingestion.canonical_document_builder import (
    CanonicalDocumentBuilder,
)
from services.extractors.chapter_extractor import ChapterExtractor


def test_azure_to_chapter_extractor():

    # 1. Load Azure Document Intelligence fixture
    with open(
        "tests/fixtures/Matrices-1-10.pdf.json",
        encoding="utf-8",
    ) as f:
        azure_document = json.load(f)

    # 2. Azure provider response → canonical blocks
    processor = AzureProcessor()
    blocks = processor.process(azure_document)

    assert len(blocks) > 0

    # 3. Canonical blocks → Canonical Document
    builder = CanonicalDocumentBuilder()

    canonical_document = builder.build(
        blocks=blocks,
        page_count=len(azure_document["analyzeResult"]["pages"]),
        filename="Matrices-1-10.pdf",
        raw_bucket="test-bucket",
        raw_object="test/Matrices-1-10.pdf",
        generation="1",
    )

    # 4. Canonical Document → Chapter
    extractor = ChapterExtractor()
    result = extractor.extract(canonical_document)

    # 5. Validate chapter
    assert len(result.items) == 1

    chapter = result.items[0]

    assert chapter.number == 3
    assert chapter.title == "Matrices"
    assert chapter.start_page == 1
    assert chapter.end_page == 2