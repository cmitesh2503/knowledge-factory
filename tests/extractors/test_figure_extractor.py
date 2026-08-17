from services.extractors.figure_extractor import FigureExtractor


def test_figure_extractor_extracts_figures():

    canonical_document = {
        "pages": [
            {
                "page_number": 1,
                "blocks": [
                    {
                        "id": "block-000080",
                        "type": "figure",
                        "text": "",
                        "page": 1,
                        "metadata": {
                            "source": "azure_document_intelligence",
                            "figure_id": "1.1",
                            "elements": [
                                "/paragraphs/0",
                                "/paragraphs/1",
                            ],
                        },
                    }
                ],
            },
            {
                "page_number": 2,
                "blocks": [
                    {
                        "id": "block-000081",
                        "type": "figure",
                        "text": "",
                        "page": 2,
                        "metadata": {
                            "source": "azure_document_intelligence",
                            "figure_id": "2.1",
                            "elements": [
                                "/paragraphs/45",
                                "/paragraphs/46",
                            ],
                        },
                    }
                ],
            },
        ]
    }

    figures = FigureExtractor().extract(
        canonical_document
    )

    assert len(figures) == 2

    assert figures[0].id == "block-000080"
    assert figures[0].metadata["figure_id"] == "1.1"
    assert figures[0].metadata["page"] == 1

    assert figures[1].id == "block-000081"
    assert figures[1].metadata["figure_id"] == "2.1"
    assert figures[1].metadata["page"] == 2