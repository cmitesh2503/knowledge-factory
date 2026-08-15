
class AzureProcessor:
    """
    Converts Azure Document Intelligence JSON into
    provider-independent canonical blocks.

    This class does not call Azure and does not build
    the final canonical document. It only normalizes
    the Azure response into canonical blocks.
    """

    BLOCK_TYPE_MAP = {
        "paragraph": "paragraph",
        "sectionHeading": "heading",
        "title": "heading",
        "pageHeader": "text",
        "pageFooter": "text",
        "pageNumber": "text",
        "formulaBlock": "formula",
    }

    def process(self, document: dict) -> list[dict]:
        """
        Convert Azure Document Intelligence JSON into
        canonical blocks.
        """

        blocks: list[dict] = []

        analyze_result = document.get("analyzeResult", {})

        for index, paragraph in enumerate(
            analyze_result.get("paragraphs", [])
        ):
            block = self._paragraph_to_block(
                paragraph=paragraph,
                index=index,
            )

            if block["text"]:
                blocks.append(block)

        return blocks

    def _paragraph_to_block(
        self,
        paragraph: dict,
        index: int,
    ) -> dict:

        text = (
            paragraph.get("content")
            or ""
        ).strip()

        role = paragraph.get(
            "role",
            "paragraph",
        )

        page = self._page_number(
            paragraph
        )

        return {
            "type": self._normalize_type(role),
            "text": text,
            "page": page,
            "confidence": None,
            "geometry": self._geometry(
                paragraph
            ),
            "metadata": {
                "source": "azure_document_intelligence",
                "role": role,
            },
        }

    def _normalize_type(
        self,
        role: str | None,
    ) -> str:

        role = str(
            role or "paragraph"
        ).strip()

        return self.BLOCK_TYPE_MAP.get(
            role,
            "paragraph",
        )

    def _page_number(
        self,
        element: dict,
    ) -> int:

        regions = element.get(
            "boundingRegions",
            [],
        )

        if not regions:
            return 1

        page_number = regions[0].get(
            "pageNumber"
        )

        try:
            page_number = int(
                page_number
            )
        except (
            TypeError,
            ValueError,
        ):
            return 1

        return (
            page_number
            if page_number >= 1
            else 1
        )

    def _geometry(
        self,
        element: dict,
    ) -> dict:

        regions = element.get(
            "boundingRegions",
            [],
        )

        if not regions:
            return {
                "polygon": [],
                "bounding_box": {},
                "coordinate_type": None,
                "reading_order": None,
                "rotation": None,
                "parent": None,
                "children": [],
                "overlaps": [],
            }

        polygon = regions[0].get(
            "polygon",
            [],
        )

        points = []

        for index in range(
            0,
            len(polygon),
            2,
        ):
            if index + 1 >= len(
                polygon
            ):
                break

            points.append(
                {
                    "x": float(
                        polygon[index]
                    ),
                    "y": float(
                        polygon[index + 1]
                    ),
                }
            )

        if not points:
            return {
                "polygon": [],
                "bounding_box": {},
                "coordinate_type": None,
                "reading_order": None,
                "rotation": None,
                "parent": None,
                "children": [],
                "overlaps": [],
            }

        xs = [
            point["x"]
            for point in points
        ]

        ys = [
            point["y"]
            for point in points
        ]

        left = min(xs)
        right = max(xs)
        top = min(ys)
        bottom = max(ys)

        return {
            "polygon": points,
            "bounding_box": {
                "left": left,
                "top": top,
                "right": right,
                "bottom": bottom,
                "width": right - left,
                "height": bottom - top,
                "center_x": (
                    left + right
                ) / 2,
                "center_y": (
                    top + bottom
                ) / 2,
            },
            "coordinate_type": "pixel",
            "reading_order": None,
            "rotation": None,
            "parent": None,
            "children": [],
            "overlaps": [],
        }