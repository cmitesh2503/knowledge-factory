class DocumentProcessor:
    """
    Processes the Document AI response.

    Extracts provider-independent layout blocks for downstream canonical
    JSON generation.
    """

    def __init__(self, logger):
        self.logger = logger

    def process(self, document, result):
        """
        Process the Document AI response.

        Returns provider-independent layout blocks for canonical processing.
        """

        self.logger.info("========== STEP 7 ==========")

        blocks = self.extract_layout(document)

        self.logger.info(
            f"Extracted {len(blocks)} layout block(s)."
        )

        self.logger.info("========== STEP 7 COMPLETE ==========")

        return blocks

    def page_count(self, document) -> int:
        """Return the source document page count."""

        return len(getattr(document, "pages", []) or [])

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
            text_block = getattr(block, "text_block", None)
            page_span = getattr(block, "page_span", None)
            block_type = getattr(text_block, "type_", None)
            text = getattr(text_block, "text", "") or ""
            page_start = getattr(page_span, "page_start", None)
            page_end = getattr(page_span, "page_end", None)

            blocks.append(self._build_block(block))

            self.logger.info(
                "Block #%d: type=%s page_start=%s page_end=%s text_length=%d",
                index + 1,
                block_type,
                page_start,
                page_end,
                len(text),
            )

        return blocks

    def _build_block(self, block) -> dict:
        text_block = getattr(block, "text_block", None)
        page_start, page_end = self._page_span(block)

        metadata = {}
        if page_start and page_end and page_start != page_end:
            metadata["page_span"] = {
                "start": page_start,
                "end": page_end,
            }

        return {
            "type": self._block_type(text_block),
            "text": self._block_text(text_block),
            "page": page_start or 1,
            "confidence": self._confidence(block),
            "bbox": self._bbox(block),
            "metadata": metadata,
        }

    def _page_span(self, block) -> tuple[int | None, int | None]:
        page_span = getattr(block, "page_span", None)
        if not page_span:
            return None, None

        page_start = getattr(page_span, "page_start", None)
        page_end = getattr(page_span, "page_end", None)

        return self._positive_int(page_start), self._positive_int(page_end)

    def _block_type(self, text_block) -> str:
        if not text_block:
            return "text"

        block_type = getattr(text_block, "type_", None)
        if not block_type:
            return "text"

        return str(block_type).strip().lower() or "text"

    def _block_text(self, text_block) -> str:
        if not text_block:
            return ""

        text = getattr(text_block, "text", "")
        return str(text or "")

    def _confidence(self, block) -> float | None:
        confidence = getattr(block, "confidence", None)
        if confidence is None:
            return None

        try:
            return float(confidence)
        except (TypeError, ValueError):
            return None

    def _bbox(self, block) -> dict:
        layout = getattr(block, "layout", None)
        bounding_polys = []

        if layout:
            bounding_polys.append(getattr(layout, "bounding_poly", None))

        bounding_polys.append(getattr(block, "bounding_poly", None))
        bounding_polys.append(getattr(block, "bounding_box", None))

        for bounding_poly in bounding_polys:
            points = self._points_from_bounding_poly(bounding_poly)
            if points:
                return {
                    "vertices": points,
                }

        return {}

    def _points_from_bounding_poly(self, bounding_poly) -> list[dict]:
        if not bounding_poly:
            return []

        vertices = (
            getattr(bounding_poly, "normalized_vertices", None)
            or getattr(bounding_poly, "vertices", None)
            or []
        )

        points = []
        for vertex in vertices:
            point = {}
            x = getattr(vertex, "x", None)
            y = getattr(vertex, "y", None)

            if x is not None:
                point["x"] = float(x)
            if y is not None:
                point["y"] = float(y)

            if point:
                points.append(point)

        return points

    def _positive_int(self, value) -> int | None:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return None

        if parsed < 1:
            return None

        return parsed
