from types import SimpleNamespace

from functions.pdf_ingestion.document_processor import (
    DocumentProcessor,
)


class FakeLogger:

    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


def make_text_block(text, page):
    text_anchor = SimpleNamespace(
        text_segments=[
            SimpleNamespace(
                start_index=0,
                end_index=len(text),
            )
        ]
    )

    text_block = SimpleNamespace(
        type_="paragraph",
        text=text,
        text_anchor=text_anchor,
        layout=None,
    )

    return SimpleNamespace(
        text_block=text_block,
        page_span=SimpleNamespace(
            page_start=page,
            page_end=page,
        ),
        layout=None,
        confidence=0.99,
    )


def test_document_processor_extracts_blocks_from_document_layout():

    blocks = [
        make_text_block(
            "Page 1 content",
            1,
        ),
        make_text_block(
            "Page 2 content",
            2,
        ),
        make_text_block(
            "Page 3 content",
            3,
        ),
    ]

    document = SimpleNamespace(
        document_layout=SimpleNamespace(
            blocks=blocks
        )
    )

    processor = DocumentProcessor(
        FakeLogger()
    )

    result = processor.extract_layout(
        document
    )
    
    assert len(result) == 3

    assert result[0]["text"] == "Page 1 content"
    assert result[0]["page"] == 1

    assert result[1]["text"] == "Page 2 content"
    assert result[1]["page"] == 2

    assert result[2]["text"] == "Page 3 content"
    assert result[2]["page"] == 3
    
def test_document_processor_preserves_page_boundaries():

    blocks = [
        make_text_block("Page 1 content", 1),
        make_text_block("Page 2 content", 2),
        make_text_block("Page 3 content", 3),
        make_text_block("Page 4 content", 4),
    ]

    document = SimpleNamespace(
        document_layout=SimpleNamespace(
            blocks=blocks
        )
    )

    processor = DocumentProcessor(FakeLogger())

    result = processor.extract_layout(document)

    assert len(result) == 4

    assert [block["page"] for block in result] == [
        1,
        2,
        3,
        4,
    ]

    assert [block["text"] for block in result] == [
        "Page 1 content",
        "Page 2 content",
        "Page 3 content",
        "Page 4 content",
    ]