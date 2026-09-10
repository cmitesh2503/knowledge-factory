"""
Visual candidate contextual enrichment.

Phase B - Step 3.

This module enriches VisualRegion objects with surrounding canonical
document context.

Responsibilities:
    - Preserve visual-region identity and provenance.
    - Collect nearby text from the same canonical page.
    - Prefer spatial proximity when text block geometry is available.
    - Fall back to canonical document order when geometry is unavailable.
    - Detect conservative, likely figure captions.
    - Preserve repeated/localized region classification.
    - Produce an intermediate VisualCandidateContext.

This module intentionally does NOT:
    - recognize mathematical figure types,
    - infer geometry,
    - determine educational relevance,
    - create Figure objects,
    - create FigureCandidate objects,
    - depend on Google Document AI or Azure Document Intelligence,
    - discard repeated structural regions.

The output is an intermediate contextual representation for later
semantic figure analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence


@dataclass(slots=True)
class VisualCandidateContext:
    """
    Context-enriched representation of a visual region.

    This is an intermediate representation between visual-region
    detection and semantic figure analysis.
    """

    id: str
    page_number: int
    bbox: tuple[float, float, float, float]

    region_role: str | None = None
    repeated: bool = False

    source_types: list[str] = field(default_factory=list)

    nearby_text: list[str] = field(default_factory=list)

    preceding_text: str | None = None
    following_text: str | None = None

    caption: str | None = None

    source_block_ids: list[str] = field(default_factory=list)

    evidence: dict[str, Any] = field(default_factory=dict)

    provenance: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the context object into a JSON-compatible dictionary."""

        return {
            "id": self.id,
            "page_number": self.page_number,
            "bbox": list(self.bbox),
            "region_role": self.region_role,
            "repeated": self.repeated,
            "source_types": list(self.source_types),
            "nearby_text": list(self.nearby_text),
            "preceding_text": self.preceding_text,
            "following_text": self.following_text,
            "caption": self.caption,
            "source_block_ids": list(self.source_block_ids),
            "evidence": dict(self.evidence),
            "provenance": dict(self.provenance),
            "metadata": dict(self.metadata),
        }


class VisualCandidateContextBuilder:
    """
    Enrich VisualRegion objects with canonical document context.

    The builder accepts canonical document data as a plain mapping so
    that it remains independent of the concrete Knowledge Factory
    model implementation.
    """

    def __init__(
        self,
        *,
        max_nearby_blocks: int = 6,
        max_vertical_distance_ratio: float = 0.35,
        caption_max_distance_ratio: float = 0.25,
    ) -> None:
        if max_nearby_blocks < 1:
            raise ValueError("max_nearby_blocks must be >= 1")

        if max_vertical_distance_ratio < 0:
            raise ValueError("max_vertical_distance_ratio must be >= 0")

        if caption_max_distance_ratio < 0:
            raise ValueError("caption_max_distance_ratio must be >= 0")

        self.max_nearby_blocks = max_nearby_blocks
        self.max_vertical_distance_ratio = max_vertical_distance_ratio
        self.caption_max_distance_ratio = caption_max_distance_ratio

    def build(
        self,
        regions: Iterable[Any],
        canonical_document: Mapping[str, Any],
    ) -> list[VisualCandidateContext]:
        """
        Build contextual candidates for all supplied visual regions.

        Args:
            regions:
                Iterable of VisualRegion-like objects.

            canonical_document:
                Canonical document mapping containing a ``pages`` list.

        Returns:
            List of VisualCandidateContext objects in the same order
            as the supplied regions.
        """

        pages = self._index_pages(canonical_document)

        results: list[VisualCandidateContext] = []

        for region in regions:
            page_number = int(region.page_number)

            page = pages.get(page_number)

            if page is None:
                results.append(
                    self._build_without_page_context(region)
                )
                continue

            blocks = self._extract_text_blocks(page)

            results.append(
                self._build_for_region(
                    region,
                    page,
                    blocks,
                )
            )

        return results

    def build_one(
        self,
        region: Any,
        canonical_document: Mapping[str, Any],
    ) -> VisualCandidateContext:
        """Build context for one VisualRegion."""

        return self.build([region], canonical_document)[0]

    def _build_for_region(
        self,
        region: Any,
        page: Mapping[str, Any],
        blocks: Sequence[dict[str, Any]],
    ) -> VisualCandidateContext:
        page_width, page_height = self._page_dimensions(page)

        region_bbox = self._normalise_bbox(region.bbox)

        spatial_blocks = self._rank_spatial_blocks(
            region_bbox=region_bbox,
            blocks=blocks,
            page_width=page_width,
            page_height=page_height,
        )

        ordered_blocks = self._select_context_blocks(
            region_bbox=region_bbox,
            blocks=blocks,
            spatial_blocks=spatial_blocks,
        )

        nearby_text = [
            block["text"]
            for block in ordered_blocks
            if block.get("text")
        ]

        source_block_ids = [
            block["id"]
            for block in ordered_blocks
            if block.get("id")
        ]

        preceding_block, following_block = self._find_preceding_following(
            region_bbox=region_bbox,
            blocks=blocks,
            ordered_blocks=ordered_blocks,
        )

        preceding_text = (
            preceding_block.get("text")
            if preceding_block is not None
            else None
        )

        following_text = (
            following_block.get("text")
            if following_block is not None
            else None
        )

        caption = self._find_caption(
            region_bbox=region_bbox,
            blocks=blocks,
            page_width=page_width,
            page_height=page_height,
        )

        metadata = dict(getattr(region, "metadata", {}) or {})

        repeated = bool(
            metadata.get("repeated", False)
        )

        region_role = metadata.get("region_role")

        evidence = {
            "has_nearby_text": bool(nearby_text),
            "has_caption": caption is not None,
            "has_preceding_text": preceding_text is not None,
            "has_following_text": following_text is not None,
            "has_spatial_context": any(
                block.get("_has_bbox", False)
                for block in ordered_blocks
            ),
            "is_repeated": repeated,
            "is_localized": region_role == "localized_visual_candidate",
        }

        provenance = {
            "source": "pdf",
            "page": int(region.page_number),
            "visual_region_id": region.id,
        }

        return VisualCandidateContext(
            id=region.id,
            page_number=int(region.page_number),
            bbox=region_bbox,
            region_role=region_role,
            repeated=repeated,
            source_types=list(
                getattr(region, "source_types", []) or []
            ),
            nearby_text=nearby_text,
            preceding_text=preceding_text,
            following_text=following_text,
            caption=caption,
            source_block_ids=source_block_ids,
            evidence=evidence,
            provenance=provenance,
            metadata=metadata,
        )

    def _build_without_page_context(
        self,
        region: Any,
    ) -> VisualCandidateContext:
        """Build a candidate when canonical page context is unavailable."""

        metadata = dict(getattr(region, "metadata", {}) or {})

        repeated = bool(metadata.get("repeated", False))
        region_role = metadata.get("region_role")

        return VisualCandidateContext(
            id=region.id,
            page_number=int(region.page_number),
            bbox=self._normalise_bbox(region.bbox),
            region_role=region_role,
            repeated=repeated,
            source_types=list(
                getattr(region, "source_types", []) or []
            ),
            evidence={
                "has_nearby_text": False,
                "has_caption": False,
                "has_preceding_text": False,
                "has_following_text": False,
                "has_spatial_context": False,
                "is_repeated": repeated,
                "is_localized": (
                    region_role == "localized_visual_candidate"
                ),
                "page_context_available": False,
            },
            provenance={
                "source": "pdf",
                "page": int(region.page_number),
                "visual_region_id": region.id,
            },
            metadata=metadata,
        )

    @staticmethod
    def _index_pages(
        canonical_document: Mapping[str, Any],
    ) -> dict[int, Mapping[str, Any]]:
        """Index canonical pages by page number."""

        pages = canonical_document.get("pages", [])

        if not isinstance(pages, Sequence):
            return {}

        indexed: dict[int, Mapping[str, Any]] = {}

        for page in pages:
            if not isinstance(page, Mapping):
                continue

            page_number = page.get("page_number")

            if page_number is None:
                page_number = page.get("page")

            if page_number is None:
                continue

            try:
                indexed[int(page_number)] = page
            except (TypeError, ValueError):
                continue

        return indexed

    @staticmethod
    def _extract_text_blocks(
        page: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Extract usable text blocks from one canonical page.

        Non-text blocks and empty text are ignored.
        Original ordering is retained.
        """

        raw_blocks = page.get("blocks", [])

        if not isinstance(raw_blocks, Sequence):
            return []

        result: list[dict[str, Any]] = []

        for index, raw_block in enumerate(raw_blocks):
            if not isinstance(raw_block, Mapping):
                continue

            text = raw_block.get("text")

            if not isinstance(text, str):
                continue

            text = " ".join(text.split())

            if not text:
                continue

            block_type = raw_block.get("type")

            # Canonical text blocks normally have type "text".
            # We also allow missing type so this remains tolerant
            # of older canonical documents.
            if block_type not in (None, "text", "paragraph", "heading"):
                continue

            block_id = raw_block.get("id")

            if block_id is None:
                block_id = f"page-block-{index}"

            bbox = VisualCandidateContextBuilder._extract_bbox(
                raw_block
            )

            result.append(
                {
                    "id": str(block_id),
                    "text": text,
                    "bbox": bbox,
                    "index": index,
                    "_has_bbox": bbox is not None,
                }
            )

        return result

    @staticmethod
    def _extract_bbox(
        block: Mapping[str, Any],
    ) -> tuple[float, float, float, float] | None:
        """
        Extract a block bounding box from common canonical representations.

        Supported forms:

            "bbox": [x0, y0, x1, y1]

        or:

            "bounding_box": [x0, y0, x1, y1]

        or:

            "bbox": {
                "x0": ...,
                "y0": ...,
                "x1": ...,
                "y1": ...
            }
        """

        value = block.get("bbox")

        if value is None:
            value = block.get("bounding_box")

        if isinstance(value, Mapping):
            try:
                return (
                    float(value["x0"]),
                    float(value["y0"]),
                    float(value["x1"]),
                    float(value["y1"]),
                )
            except (KeyError, TypeError, ValueError):
                return None

        if isinstance(value, Sequence) and not isinstance(
            value,
            (str, bytes),
        ):
            if len(value) != 4:
                return None

            try:
                return tuple(float(item) for item in value)  # type: ignore[return-value]
            except (TypeError, ValueError):
                return None

        return None

    @staticmethod
    def _page_dimensions(
        page: Mapping[str, Any],
    ) -> tuple[float | None, float | None]:
        """Extract page dimensions when available."""

        width = page.get("width")
        height = page.get("height")

        try:
            width_value = float(width) if width is not None else None
        except (TypeError, ValueError):
            width_value = None

        try:
            height_value = float(height) if height is not None else None
        except (TypeError, ValueError):
            height_value = None

        return width_value, height_value

    def _rank_spatial_blocks(
        self,
        *,
        region_bbox: tuple[float, float, float, float],
        blocks: Sequence[dict[str, Any]],
        page_width: float | None,
        page_height: float | None,
    ) -> list[dict[str, Any]]:
        """
        Rank text blocks by spatial proximity to a visual region.

        Blocks without geometry are intentionally excluded here and
        handled by document-order fallback.
        """

        result: list[dict[str, Any]] = []

        for block in blocks:
            bbox = block.get("bbox")

            if bbox is None:
                continue

            distance = self._bbox_distance(
                region_bbox,
                bbox,
            )

            enriched = dict(block)
            enriched["_distance"] = distance

            if self._is_spatially_near(
                region_bbox,
                bbox,
                page_width,
                page_height,
            ):
                result.append(enriched)

        result.sort(
            key=lambda item: (
                float(item.get("_distance", float("inf"))),
                int(item.get("index", 0)),
            )
        )

        return result

    def _select_context_blocks(
        self,
        *,
        region_bbox: tuple[float, float, float, float],
        blocks: Sequence[dict[str, Any]],
        spatial_blocks: Sequence[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Select nearby context blocks.

        Spatially ranked blocks are preferred whenever geometry exists.

        If no spatial candidates exist, use the nearest blocks in
        canonical document order.
        """

        if spatial_blocks:
            selected = list(
                spatial_blocks[: self.max_nearby_blocks]
            )

            selected.sort(
                key=lambda item: int(item.get("index", 0))
            )

            return selected

        if not blocks:
            return []

        region_center_y = (
            region_bbox[1] + region_bbox[3]
        ) / 2.0

        ranked = sorted(
            blocks,
            key=lambda block: abs(
                self._document_order_position(
                    block,
                    blocks,
                    region_center_y,
                )
            ),
        )

        return list(
            sorted(
                ranked[: self.max_nearby_blocks],
                key=lambda item: int(item.get("index", 0)),
            )
        )

    @staticmethod
    def _document_order_position(
        block: Mapping[str, Any],
        blocks: Sequence[Mapping[str, Any]],
        region_center_y: float,
    ) -> float:
        """
        Produce a stable fallback ordering score.

        When no text geometry exists, canonical block order is the
        strongest available signal.
        """

        if block.get("index") is not None:
            return float(block["index"])

        return region_center_y

    def _find_preceding_following(
        self,
        *,
        region_bbox: tuple[float, float, float, float],
        blocks: Sequence[dict[str, Any]],
        ordered_blocks: Sequence[dict[str, Any]],
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        """
        Determine the closest preceding and following text blocks.
        """

        if not ordered_blocks:
            return None, None

        blocks_with_bbox = [
            block
            for block in blocks
            if block.get("bbox") is not None
        ]

        if blocks_with_bbox:
            preceding = [
                block
                for block in blocks_with_bbox
                if block["bbox"][3] <= region_bbox[1]
            ]

            following = [
                block
                for block in blocks_with_bbox
                if block["bbox"][1] >= region_bbox[3]
            ]

            preceding.sort(
                key=lambda block: (
                    region_bbox[1] - block["bbox"][3],
                    -int(block.get("index", 0)),
                )
            )

            following.sort(
                key=lambda block: (
                    block["bbox"][1] - region_bbox[3],
                    int(block.get("index", 0)),
                )
            )

            return (
                preceding[0] if preceding else None,
                following[0] if following else None,
            )

        ordered = sorted(
            ordered_blocks,
            key=lambda item: int(item.get("index", 0)),
        )

        if len(ordered) == 1:
            return ordered[0], None

        return ordered[0], ordered[-1]

    def _find_caption(
        self,
        *,
        region_bbox: tuple[float, float, float, float],
        blocks: Sequence[dict[str, Any]],
        page_width: float | None,
        page_height: float | None,
    ) -> str | None:
        """
        Find a conservative likely figure caption.

        Caption recognition is intentionally pattern-based and
        conservative. It does not infer that arbitrary nearby text
        is a caption.
        """

        candidates: list[tuple[float, str]] = []

        for block in blocks:
            text = block.get("text")

            if not text or not self._looks_like_caption(text):
                continue

            bbox = block.get("bbox")

            if bbox is None:
                continue

            distance = self._bbox_distance(
                region_bbox,
                bbox,
            )

            max_distance = self._caption_distance_limit(
                region_bbox,
                page_width,
                page_height,
            )

            if distance <= max_distance:
                candidates.append(
                    (distance, text)
                )

        if not candidates:
            return None

        candidates.sort(key=lambda item: item[0])

        return candidates[0][1]

    @staticmethod
    def _looks_like_caption(text: str) -> bool:
        """Return True for conservative figure-caption patterns."""

        normalized = " ".join(text.strip().split())

        if not normalized:
            return False

        lower = normalized.lower()

        prefixes = (
            "figure ",
            "fig. ",
            "fig ",
            "figure:",
            "fig.:",
            "fig:",
        )

        return lower.startswith(prefixes)

    def _caption_distance_limit(
        self,
        region_bbox: tuple[float, float, float, float],
        page_width: float | None,
        page_height: float | None,
    ) -> float:
        """Calculate maximum distance allowed for caption matching."""

        region_height = max(
            1.0,
            region_bbox[3] - region_bbox[1],
        )

        if page_height is not None:
            return max(
                region_height * self.caption_max_distance_ratio,
                page_height * 0.08,
            )

        return region_height * self.caption_max_distance_ratio

    def _is_spatially_near(
        self,
        region_bbox: tuple[float, float, float, float],
        block_bbox: tuple[float, float, float, float],
        page_width: float | None,
        page_height: float | None,
    ) -> bool:
        """
        Determine whether a text block is sufficiently close to a region.
        """

        distance = self._bbox_distance(
            region_bbox,
            block_bbox,
        )

        region_height = max(
            1.0,
            region_bbox[3] - region_bbox[1],
        )

        if page_height is not None:
            max_distance = max(
                region_height * self.max_vertical_distance_ratio,
                page_height * 0.20,
            )
        else:
            max_distance = region_height * (
                self.max_vertical_distance_ratio + 1.0
            )

        return distance <= max_distance

    @staticmethod
    def _bbox_distance(
        first: tuple[float, float, float, float],
        second: tuple[float, float, float, float],
    ) -> float:
        """
        Calculate Euclidean distance between two axis-aligned rectangles.

        Distance is zero when rectangles overlap or touch.
        """

        first_x0, first_y0, first_x1, first_y1 = first
        second_x0, second_y0, second_x1, second_y1 = second

        horizontal = max(
            second_x0 - first_x1,
            first_x0 - second_x1,
            0.0,
        )

        vertical = max(
            second_y0 - first_y1,
            first_y0 - second_y1,
            0.0,
        )

        return (
            horizontal**2 + vertical**2
        ) ** 0.5

    @staticmethod
    def _normalise_bbox(
        bbox: Sequence[float],
    ) -> tuple[float, float, float, float]:
        """Normalize a bounding box to four floating-point coordinates."""

        if len(bbox) != 4:
            raise ValueError(
                "Visual region bbox must contain exactly four values"
            )

        x0, y0, x1, y1 = (
            float(value)
            for value in bbox
        )

        return (
            min(x0, x1),
            min(y0, y1),
            max(x0, x1),
            max(y0, y1),
        )