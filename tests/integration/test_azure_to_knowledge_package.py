import json

from functions.pdf_ingestion.azure_processor import AzureProcessor
from functions.pdf_ingestion.canonical_document_builder import (
    CanonicalDocumentBuilder,
)
from services.integration.knowledge_package_builder import (
    KnowledgePackageBuilder,
)


def test_azure_to_knowledge_package():
    # 1. Load Azure Document Intelligence output
    with open(
        "tests/fixtures/Matrices-1-10.pdf.json",
        encoding="utf-8",
    ) as f:
        azure_document = json.load(f)

    # 2. Azure JSON → provider-independent canonical blocks
    processor = AzureProcessor()

    blocks = processor.process(azure_document)

    assert len(blocks) > 0

    # 3. Canonical blocks → Canonical Document
    builder = CanonicalDocumentBuilder()

    canonical_document = builder.build(
        blocks=blocks,
        page_count=len(
            azure_document["analyzeResult"]["pages"]
        ),
        filename="Matrices-1-10.pdf",
        raw_bucket="test-bucket",
        raw_object="test/Matrices-1-10.pdf",
        generation="1",
    )

    # 4. Canonical Document → Knowledge Package
    package_builder = KnowledgePackageBuilder()

    package = package_builder.build(
        canonical_document
    )

    # 5. Validate package identity
    assert package.schema_version == "1.0"
    assert package.document_id == (
        canonical_document["document"]["document_id"]
    )

    # 6. Validate chapter extraction
    assert len(package.chapters) == 1

    chapter = package.chapters[0]

    assert chapter.number == 3
    assert chapter.title == "Matrices"
    assert chapter.start_page == 1
    assert chapter.end_page == 2

    # 7. Validate section extraction
    section_numbers = [
        section.number
        for section in package.sections
    ]

    assert "3.1" in section_numbers
    assert "3.2" in section_numbers

    # At minimum, the first two pages contain
    # these two sections.
    assert len(package.sections) >= 2