"""
Knowledge Factory

Visual Region Detector

Phase B - Step 2

Detects visually significant regions in source PDF pages.

This component operates on the original PDF and identifies
candidate visual regions using PDF-native information such as:

- embedded images
- vector drawings
- groups of nearby drawing objects
- repeated visual structures across pages

The detector does not discard repeated visual structures.

Instead, repeated structures are retained and explicitly marked
in metadata so later stages can distinguish them from localized
visual candidates.

It does not:

- classify figures
- infer mathematical meaning
- infer geometry
- extract labels
- determine educational relevance
- create Figure objects

Semantic interpretation belongs to later Phase B stages.

The detector is document-wide and has no chapter, subject, or
page-specific assumptions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator


@dataclass(slots=True)
class VisualRegion:
    """
    A provider-independent visual region detected on a PDF page.

    Coordinates use the source PDF page coordinate system.

    The bounding box is represented as:

        (x0, y0, x1, y1)
    """

    id: str
    page_number: int
    bbox: tuple[float, float, float, float]

    source_types: list[str] = field(default_factory=list)

    image_count: int = 0
    drawing_count: int = 0

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def width(self) -> float:
        """Return the region width."""
        return max(0.0, self.bbox[2] - self.bbox[0])

    @property
    def height(self) -> float:
        """Return the region height."""
        return max(0.0, self.bbox[3] - self.bbox[1])

    @property
    def area(self) -> float:
        """Return the region area."""
        return self.width * self.height


class VisualRegionDetector:
    """
    Detect visual regions from the complete source PDF.

    Phase B Step 2 performs structural detection only.

    Repeated visual structures are retained rather than discarded.
    They are marked with metadata["repeated"] = True.

    Localized visual candidates are marked with:

        metadata["repeated"] = False
        metadata["region_role"] = "localized_visual_candidate"

    Repeated structural regions are marked with:

        metadata["repeated"] = True
        metadata["region_role"] = "repeated_structural_region"

    This allows later figure-analysis stages to decide whether a
    region represents an actual educational figure.

    It does not:

    - classify figures
    - infer mathematical meaning
    - infer geometry
    - extract labels
    - determine educational relevance
    - create Figure objects
    """

    def __init__(
        self,
        *,
        min_width: float = 12.0,
        min_height: float = 12.0,
        merge_gap: float = 18.0,
        page_edge_tolerance: float = 4.0,
        page_coverage_threshold: float = 0.92,
        repeated_region_ratio: float = 0.50,
    ) -> None:
        if min_width <= 0:
            raise ValueError(
                "min_width must be greater than zero"
            )

        if min_height <= 0:
            raise ValueError(
                "min_height must be greater than zero"
            )

        if merge_gap < 0:
            raise ValueError(
                "merge_gap cannot be negative"
            )

        if page_edge_tolerance < 0:
            raise ValueError(
                "page_edge_tolerance cannot be negative"
            )

        if not 0 < page_coverage_threshold <= 1:
            raise ValueError(
                "page_coverage_threshold must be "
                "between 0 and 1"
            )

        if not 0 < repeated_region_ratio <= 1:
            raise ValueError(
                "repeated_region_ratio must be "
                "between 0 and 1"
            )

        self.min_width = min_width
        self.min_height = min_height
        self.merge_gap = merge_gap
        self.page_edge_tolerance = (
            page_edge_tolerance
        )
        self.page_coverage_threshold = (
            page_coverage_threshold
        )
        self.repeated_region_ratio = (
            repeated_region_ratio
        )

    def detect(
        self,
        pdf_path: str | Path,
    ) -> list[VisualRegion]:
        """
        Detect visual regions across the complete PDF.

        Every page is inspected.

        No visual region is discarded merely because it is repeated.
        Repeated structures are retained and explicitly marked in
        metadata.
        """
        path = Path(pdf_path)

        if not path.is_file():
            raise FileNotFoundError(
                f"Source PDF not found: {path}"
            )

        repeated_image_xrefs = (
            self._find_repeated_image_xrefs(path)
        )

        regions_by_page = self._iter_page_regions(
            path,
            repeated_image_xrefs,
        )

        repeated_signatures = (
            self._find_repeated_regions(
                regions_by_page
            )
        )

        results: list[VisualRegion] = []

        for page_regions in regions_by_page:
            for region in page_regions:

                repeated = (
                    bool(
                        region.metadata.get(
                            "repeated_image",
                            False,
                        )
                    )
                    or self._is_repeated_region(
                        region,
                        repeated_signatures,
                    )
                )

                region.metadata["repeated"] = (
                    repeated
                )

                if repeated:
                    region.metadata[
                        "region_role"
                    ] = "repeated_structural_region"
                else:
                    region.metadata[
                        "region_role"
                    ] = "localized_visual_candidate"

                results.append(region)

        return results

    def iter_regions(
        self,
        pdf_path: str | Path,
    ) -> Iterator[VisualRegion]:
        """
        Lazily expose detected visual regions.

        Cross-page repetition classification requires observing the
        complete document first, so this method yields the complete
        classified result set after document inspection.
        """
        yield from self.detect(pdf_path)

    def _iter_page_regions(
        self,
        path: Path,
        repeated_image_xrefs: set[int],
    ) -> list[list[VisualRegion]]:
        """
        Detect structural visual regions for every page.

        Repeated images are retained as primitives and marked so
        their structural role can be propagated into the resulting
        visual region.
        """
        try:
            import pymupdf
        except ImportError as exc:
            raise RuntimeError(
                "PyMuPDF is required for visual "
                "region detection."
            ) from exc

        pages: list[list[VisualRegion]] = []

        with pymupdf.open(path) as document:

            for page_index, page in enumerate(
                document
            ):
                page_number = page_index + 1

                page_width = float(
                    page.rect.width
                )
                page_height = float(
                    page.rect.height
                )

                primitives = (
                    self._collect_primitives(
                        page,
                        page_width,
                        page_height,
                        repeated_image_xrefs,
                    )
                )

                if not primitives:
                    pages.append([])
                    continue

                merged_regions = (
                    self._merge_primitives(
                        primitives
                    )
                )

                page_regions: list[VisualRegion] = []

                for region_index, region in enumerate(
                    merged_regions
                ):
                    page_regions.append(
                        VisualRegion(
                            id=(
                                f"visual-region-"
                                f"{page_number}-"
                                f"{region_index + 1}"
                            ),
                            page_number=page_number,
                            bbox=region["bbox"],
                            source_types=sorted(
                                region[
                                    "source_types"
                                ]
                            ),
                            image_count=region[
                                "image_count"
                            ],
                            drawing_count=region[
                                "drawing_count"
                            ],
                            metadata={
                                "detection_method": (
                                    "pdf_native_visual_objects"
                                ),
                                "page_width": (
                                    page_width
                                ),
                                "page_height": (
                                    page_height
                                ),
                                "repeated_image": (
                                    region[
                                        "repeated_image"
                                    ]
                                ),
                            },
                        )
                    )

                pages.append(page_regions)

        return pages

    def _find_repeated_image_xrefs(
        self,
        path: Path,
    ) -> set[int]:
        """
        Identify embedded images reused across a substantial
        portion of the complete PDF.

        Repeated images are NOT removed.

        Their XRefs are returned so the corresponding visual
        primitives can be marked as repeated structural content.
        """
        try:
            import pymupdf
        except ImportError as exc:
            raise RuntimeError(
                "PyMuPDF is required for visual "
                "region detection."
            ) from exc

        image_pages: dict[int, set[int]] = {}

        with pymupdf.open(path) as document:
            page_count = len(document)

            if page_count <= 1:
                return set()

            for page_index, page in enumerate(
                document
            ):
                page_number = page_index + 1

                for image in page.get_images(
                    full=True
                ):
                    xref = int(image[0])

                    image_pages.setdefault(
                        xref,
                        set(),
                    ).add(page_number)

        repeated: set[int] = set()

        for xref, pages in image_pages.items():
            occurrence_ratio = (
                len(pages) / page_count
            )

            if (
                occurrence_ratio
                >= self.repeated_region_ratio
            ):
                repeated.add(xref)

        return repeated

    def _collect_primitives(
        self,
        page: Any,
        page_width: float,
        page_height: float,
        repeated_image_xrefs: set[int],
    ) -> list[dict[str, Any]]:
        """
        Collect image and vector-drawing primitives.

        Page-spanning objects are excluded because they are normally
        page backgrounds, rendering artifacts, or full-page
        containers.

        Repeated embedded images are retained and marked.
        """
        primitives: list[dict[str, Any]] = []

        for image in page.get_images(
            full=True
        ):
            xref = int(image[0])

            is_repeated_image = (
                xref in repeated_image_xrefs
            )

            rects = page.get_image_rects(
                image
            )

            for rect in rects:
                bbox = self._normalise_bbox(
                    rect
                )

                if not self._is_candidate_bbox(
                    bbox,
                    page_width,
                    page_height,
                ):
                    continue

                primitives.append(
                    {
                        "bbox": bbox,
                        "source_types": {"image"},
                        "image_count": 1,
                        "drawing_count": 0,
                        "repeated_image": (
                            is_repeated_image
                        ),
                    }
                )

        for drawing in page.get_drawings():
            rect = drawing.get("rect")

            if rect is None:
                continue

            bbox = self._normalise_bbox(
                rect
            )

            if not self._is_candidate_bbox(
                bbox,
                page_width,
                page_height,
            ):
                continue

            primitives.append(
                {
                    "bbox": bbox,
                    "source_types": {"drawing"},
                    "image_count": 0,
                    "drawing_count": 1,
                    "repeated_image": False,
                }
            )

        return primitives

    def _is_candidate_bbox(
        self,
        bbox: tuple[
            float,
            float,
            float,
            float,
        ],
        page_width: float,
        page_height: float,
    ) -> bool:
        """
        Determine whether a native visual object can be considered
        a localized or structural visual candidate.

        Page-spanning objects are excluded.
        """
        x0, y0, x1, y1 = bbox

        width = x1 - x0
        height = y1 - y0

        if (
            width < self.min_width
            or height < self.min_height
        ):
            return False

        covered_width = min(
            width,
            page_width,
        )

        covered_height = min(
            height,
            page_height,
        )

        width_ratio = (
            covered_width / page_width
        )

        height_ratio = (
            covered_height / page_height
        )

        if (
            width_ratio
            >= self.page_coverage_threshold
            and height_ratio
            >= self.page_coverage_threshold
        ):
            return False

        if (
            x0 <= -self.page_edge_tolerance
            and y0 <= -self.page_edge_tolerance
            and x1 >= (
                page_width
                + self.page_edge_tolerance
            )
            and y1 >= (
                page_height
                + self.page_edge_tolerance
            )
        ):
            return False

        return True

    def _merge_primitives(
        self,
        primitives: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Merge nearby visual primitives into visual regions.

        Repeated-image state is propagated into the merged region.

        This allows a region containing a repeated image plus
        page-specific drawings to remain available while still
        being identifiable as structurally repeated.
        """
        regions: list[dict[str, Any]] = []

        for primitive in primitives:
            matching_regions = [
                region
                for region in regions
                if self._should_merge(
                    region["bbox"],
                    primitive["bbox"],
                )
            ]

            if not matching_regions:
                regions.append(
                    {
                        "bbox": primitive["bbox"],
                        "source_types": set(
                            primitive[
                                "source_types"
                            ]
                        ),
                        "image_count": primitive[
                            "image_count"
                        ],
                        "drawing_count": primitive[
                            "drawing_count"
                        ],
                        "repeated_image": bool(
                            primitive[
                                "repeated_image"
                            ]
                        ),
                    }
                )
                continue

            target = matching_regions[0]

            target["bbox"] = (
                self._union_bbox(
                    target["bbox"],
                    primitive["bbox"],
                )
            )

            target["source_types"].update(
                primitive["source_types"]
            )

            target["image_count"] += (
                primitive["image_count"]
            )

            target["drawing_count"] += (
                primitive["drawing_count"]
            )

            target["repeated_image"] = (
                target["repeated_image"]
                or bool(
                    primitive[
                        "repeated_image"
                    ]
                )
            )

            for other in matching_regions[1:]:
                target["bbox"] = (
                    self._union_bbox(
                        target["bbox"],
                        other["bbox"],
                    )
                )

                target["source_types"].update(
                    other["source_types"]
                )

                target["image_count"] += (
                    other["image_count"]
                )

                target["drawing_count"] += (
                    other["drawing_count"]
                )

                target["repeated_image"] = (
                    target["repeated_image"]
                    or other[
                        "repeated_image"
                    ]
                )

                regions.remove(other)

        return regions

    def _find_repeated_regions(
        self,
        regions_by_page: list[list[VisualRegion]],
    ) -> list[dict[str, Any]]:
        """
        Identify visual regions that recur across a substantial
        portion of the document.

        Repeated regions are retained. This method only identifies
        their structural signatures so the caller can annotate
        them.

        Large image-backed regions are compared primarily by their
        horizontal footprint because page-specific content can
        change their vertical extent from page to page.
        """
        signatures: list[dict[str, Any]] = []

        page_count = len(regions_by_page)

        if page_count <= 1:
            return signatures

        for page_regions in regions_by_page:
            for region in page_regions:

                if region.image_count <= 0:
                    continue

                matched = False

                for signature in signatures:

                    if not self._same_region_signature(
                        region,
                        signature,
                    ):
                        continue

                    signature[
                        "page_numbers"
                    ].add(
                        region.page_number
                    )

                    matched = True
                    break

                if not matched:
                    signatures.append(
                        {
                            "bbox": region.bbox,
                            "source_types": tuple(
                                region.source_types
                            ),
                            "image_count": (
                                region.image_count
                            ),
                            "page_width": float(
                                region.metadata[
                                    "page_width"
                                ]
                            ),
                            "page_height": float(
                                region.metadata[
                                    "page_height"
                                ]
                            ),
                            "page_numbers": {
                                region.page_number
                            },
                        }
                    )

        repeated: list[dict[str, Any]] = []

        for signature in signatures:
            occurrence_ratio = (
                len(
                    signature[
                        "page_numbers"
                    ]
                )
                / page_count
            )

            if (
                occurrence_ratio
                >= self.repeated_region_ratio
            ):
                signature[
                    "occurrence_ratio"
                ] = occurrence_ratio

                repeated.append(
                    signature
                )

        return repeated

    def _is_repeated_region(
        self,
        region: VisualRegion,
        repeated_signatures: list[dict[str, Any]],
    ) -> bool:
        """
        Return True when an image-backed region matches a
        cross-page repeated visual structure.

        Repeated-image primitives are also considered repeated.

        Drawing-only regions are not marked repeated by this
        structural image-based filter.
        """
        if bool(
            region.metadata.get(
                "repeated_image",
                False,
            )
        ):
            return True

        if region.image_count <= 0:
            return False

        for signature in repeated_signatures:
            if self._same_region_signature(
                region,
                signature,
            ):
                return True

        return False

    def _same_region_signature(
        self,
        region: VisualRegion,
        signature: dict[str, Any],
    ) -> bool:
        """
        Compare a detected region with a structural repeated-region
        signature.

        Large image-backed regions are compared primarily by their
        horizontal footprint because page-specific content can
        change their vertical extent from page to page.

        Localized drawing-only regions are intentionally excluded.
        """
        if region.image_count <= 0:
            return False

        if signature["image_count"] <= 0:
            return False

        if "image" not in region.source_types:
            return False

        if "image" not in signature["source_types"]:
            return False

        region_page_width = float(
            region.metadata.get(
                "page_width",
                0.0,
            )
        )

        region_page_height = float(
            region.metadata.get(
                "page_height",
                0.0,
            )
        )

        signature_page_width = float(
            signature.get(
                "page_width",
                0.0,
            )
        )

        signature_page_height = float(
            signature.get(
                "page_height",
                0.0,
            )
        )

        if (
            region_page_width <= 0
            or region_page_height <= 0
            or signature_page_width <= 0
            or signature_page_height <= 0
        ):
            return False

        region_normalized = (
            self._normalise_bbox_to_page(
                region.bbox,
                region_page_width,
                region_page_height,
            )
        )

        signature_normalized = (
            self._normalise_bbox_to_page(
                signature["bbox"],
                signature_page_width,
                signature_page_height,
            )
        )

        (
            region_x0,
            _region_y0,
            region_x1,
            _region_y1,
        ) = region_normalized

        (
            signature_x0,
            _signature_y0,
            signature_x1,
            _signature_y1,
        ) = signature_normalized

        region_width = (
            region_x1 - region_x0
        )

        signature_width = (
            signature_x1 - signature_x0
        )

        region_height = (
            region_normalized[3]
            - region_normalized[1]
        )

        signature_height = (
            signature_normalized[3]
            - signature_normalized[1]
        )

        if (
            region_width < 0.75
            or signature_width < 0.75
        ):
            return False

        horizontal_similarity = (
            abs(
                region_x0
                - signature_x0
            )
            <= 0.10
            and abs(
                region_x1
                - signature_x1
            )
            <= 0.10
        )

        if not horizontal_similarity:
            return False

        if (
            abs(
                region_width
                - signature_width
            )
            > 0.12
        ):
            return False

        if (
            abs(
                region_height
                - signature_height
            )
            > 0.30
        ):
            return False

        return True

    @staticmethod
    def _normalise_bbox_to_page(
        bbox: tuple[
            float,
            float,
            float,
            float,
        ],
        page_width: float,
        page_height: float,
    ) -> tuple[
        float,
        float,
        float,
        float,
    ]:
        """
        Convert PDF coordinates into page-relative coordinates.

        Each coordinate is represented as a fraction of the page
        dimensions.
        """
        return (
            bbox[0] / page_width,
            bbox[1] / page_height,
            bbox[2] / page_width,
            bbox[3] / page_height,
        )

    @staticmethod
    def _should_merge(
        first: tuple[
            float,
            float,
            float,
            float,
        ],
        second: tuple[
            float,
            float,
            float,
            float,
        ],
        merge_gap: float = 18.0,
    ) -> bool:
        """
        Return True when two visual primitives overlap or are
        sufficiently close to plausibly belong to one visual region.

        The default merge gap preserves the existing detector
        behavior.
        """
        expanded = VisualRegionDetector._expand_bbox(
            first,
            merge_gap,
        )

        return VisualRegionDetector._intersects(
            expanded,
            second,
        )

    @staticmethod
    def _normalise_bbox(
        rect: Any,
    ) -> tuple[
        float,
        float,
        float,
        float,
    ]:
        """Convert a PyMuPDF rectangle to a plain tuple."""
        return (
            float(rect.x0),
            float(rect.y0),
            float(rect.x1),
            float(rect.y1),
        )

    @staticmethod
    def _expand_bbox(
        bbox: tuple[
            float,
            float,
            float,
            float,
        ],
        amount: float,
    ) -> tuple[
        float,
        float,
        float,
        float,
    ]:
        """Expand a bounding box by the specified amount."""
        return (
            bbox[0] - amount,
            bbox[1] - amount,
            bbox[2] + amount,
            bbox[3] + amount,
        )

    @staticmethod
    def _intersects(
        first: tuple[
            float,
            float,
            float,
            float,
        ],
        second: tuple[
            float,
            float,
            float,
            float,
        ],
    ) -> bool:
        """Return True when two bounding boxes intersect."""
        return not (
            first[2] < second[0]
            or second[2] < first[0]
            or first[3] < second[1]
            or second[3] < first[1]
        )

    @staticmethod
    def _union_bbox(
        first: tuple[
            float,
            float,
            float,
            float,
        ],
        second: tuple[
            float,
            float,
            float,
            float,
        ],
    ) -> tuple[
        float,
        float,
        float,
        float,
    ]:
        """Return the union of two bounding boxes."""
        return (
            min(first[0], second[0]),
            min(first[1], second[1]),
            max(first[2], second[2]),
            max(first[3], second[3]),
        )