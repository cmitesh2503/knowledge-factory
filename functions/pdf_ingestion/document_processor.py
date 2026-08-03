class DocumentProcessor:
    """
    Processes the Document AI response.

    Extracts layout blocks for downstream canonical JSON generation.
    """

    def __init__(self, logger):
        self.logger = logger

    def process(self, document, result):
        """
        Process the Document AI response.

        Returns extracted layout blocks for canonical processing.
        """

        self.logger.info("========== STEP 7 ==========")

        blocks = self.extract_layout(document)

        self.logger.info(
            f"Extracted {len(blocks)} layout block(s)."
        )

        self.logger.info("========== STEP 7 COMPLETE ==========")

        return blocks
        
    def extract_layout(self, document):
        """
        Extract information from the Document AI Layout Parser.
        """
        blocks = []

        self.logger.info("========== LAYOUT VALIDATION ==========")

        if not hasattr(document, "document_layout"):
            self.logger.warning("Document has no 'document_layout' attribute.")
            return blocks

        layout = document.document_layout

        self.logger.info(
            f"Layout contains {len(layout.blocks)} block(s)."
        )

        for index, block in enumerate(layout.blocks):
            blocks.append(block)

            text_block = getattr(block, "text_block", None)
            page_span = getattr(block, "page_span", None)
            block_type = getattr(text_block, "type_", None)
            text = getattr(text_block, "text", "") or ""
            page_start = getattr(page_span, "page_start", None)
            page_end = getattr(page_span, "page_end", None)

            self.logger.info(
                "Block #%d: type=%s page_start=%s page_end=%s text_length=%d",
                index + 1,
                block_type,
                page_start,
                page_end,
                len(text),
            )

        return blocks
