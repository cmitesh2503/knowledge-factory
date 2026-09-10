"""
Semantic analysis of visual figure candidates.

Phase B - Step 4.

This module converts contextual visual evidence into a provider-independent
FigureCandidate.

The implementation establishes the semantic-analysis boundary without
coupling Knowledge Factory to a particular vision or generative-AI provider.

Current implementation:
    - preserves contextual evidence,
    - derives conservative semantic hints from explicit textual evidence,
    - detects common figure terminology using whole-word matching,
    - extracts labels only when supported by explicit figure-like wording,
    - preserves provenance,
    - produces FigureCandidate objects.

It does NOT:
    - perform image understanding,
    - call an external AI provider,
    - infer geometry from pixels,
    - invent labels,
    - determine exact mathematical relationships,
    - render figures,
    - discard candidates.

A future vision/model-backed analyzer can implement the same interface
and provide richer semantic information without changing FigureCandidate
or downstream canonical models.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Protocol, Sequence

from services.models.figure_candidate import FigureCandidate


class VisualSemanticAnalyzer(Protocol):
    """Interface for provider-independent visual semantic analysis."""

    def analyze(
        self,
        context: Any,
        visual_input: Any | None = None,
    ) -> FigureCandidate:
        """Analyze one contextual visual candidate."""
        ...


@dataclass(slots=True)
class SemanticAnalysisResult:
    """
    Provider-independent semantic analysis result.

    This remains separate from FigureCandidate so that semantic analysis
    can be tested independently from the domain model.
    """

    figure_type: str | None = None
    description: str | None = None

    labels: list[str] | None = None
    related_concepts: list[str] | None = None

    geometry: dict[str, Any] | None = None
    educational: dict[str, Any] | None = None
    interaction: dict[str, Any] | None = None

    is_educationally_relevant: bool | None = None
    confidence: float | None = None

    evidence: dict[str, Any] | None = None


class RuleBasedVisualSemanticAnalyzer:
    """
    Conservative semantic analyzer based on explicit document text.

    This is a baseline implementation.

    Semantic conclusions are based only on textual evidence surrounding
    the visual candidate. The analyzer does not claim to understand the
    visual pixels themselves.
    """

    # ------------------------------------------------------------------
    # Figure-type terminology.
    #
    # Terms are matched as complete words/phrases. This prevents false
    # positives such as:
    #
    #     "particular" -> "arc"
    #
    # or:
    #
    #     "rectangle..." -> accidental substring matches.
    # ------------------------------------------------------------------
    _FIGURE_TYPE_PATTERNS: tuple[
        tuple[str, tuple[str, ...]]
    ] = (
        (
            "triangle",
            (
                "triangle",
                "triangular",
            ),
        ),
        (
            "circle",
            (
                "circle",
                "circular",
            ),
        ),
        (
            "rectangle",
            (
                "rectangle",
                "rectangular",
            ),
        ),
        (
            "square",
            (
                "square",
            ),
        ),
        (
            "quadrilateral",
            (
                "quadrilateral",
            ),
        ),
        (
            "parallelogram",
            (
                "parallelogram",
            ),
        ),
        (
            "trapezium",
            (
                "trapezium",
                "trapezoid",
            ),
        ),
        (
            "rhombus",
            (
                "rhombus",
            ),
        ),
        (
            "ellipse",
            (
                "ellipse",
                "elliptical",
            ),
        ),
        (
            "arc",
            (
                "arc",
            ),
        ),
        (
            "sector",
            (
                "sector",
            ),
        ),
        (
            "number_line",
            (
                "number line",
            ),
        ),
        (
            "coordinate_plot",
            (
                "coordinate plane",
                "coordinate graph",
                "coordinate plot",
            ),
        ),
        (
            "function_graph",
            (
                "function graph",
                "graph of the function",
            ),
        ),
        (
            "line_segment",
            (
                "line segment",
            ),
        ),
        (
            "ray",
            (
                "ray",
            ),
        ),
        (
            "vector",
            (
                "vector",
            ),
        ),
    )

    # ------------------------------------------------------------------
    # Concepts.
    #
    # These are contextual concepts only. They do NOT by themselves prove
    # that the visual region represents a figure of that type.
    # ------------------------------------------------------------------
    _CONCEPT_TERMS: tuple[str, ...] = (
        "angle",
        "angles",
        "triangle",
        "triangles",
        "circle",
        "circles",
        "geometry",
        "coordinate geometry",
        "coordinate plane",
        "trigonometry",
        "sine",
        "cosine",
        "tangent",
        "vector",
        "vectors",
        "line",
        "lines",
        "point",
        "points",
        "quadrilateral",
        "parallelogram",
        "rectangle",
        "square",
        "rhombus",
        "trapezium",
        "trapezoid",
        "polygon",
        "graph",
        "graphs",
        "function",
        "functions",
    )

    # ------------------------------------------------------------------
    # Strong figure-reference patterns.
    #
    # These are deliberately narrower than generic mathematical language.
    # ------------------------------------------------------------------
    _FIGURE_REFERENCE_PATTERN = re.compile(
        r"\b(?:"
        r"figure|fig\.?|diagram|illustration|"
        r"shown|shown\s+below|shown\s+above|"
        r"as\s+shown|given\s+figure|given\s+diagram"
        r")\b",
        flags=re.IGNORECASE,
    )

    # Explicit compact point names:
    #
    #     triangle ABC
    #     quadrilateral ABCD
    #
    # This is evaluated only when figure context is present.
    _COMPACT_LABEL_PATTERN = re.compile(
        r"\b([A-Z]{2,6})\b"
    )

    # Explicit single point labels in mathematical structures:
    #
    #     point A
    #     points A and B
    #     vertex A
    #     vertices A, B and C
    #
    _EXPLICIT_LABEL_PATTERN = re.compile(
        r"\b(?:point|points|vertex|vertices)"
        r"\s+"
        r"([A-Z])\b",
        flags=re.IGNORECASE,
    )

    # Coordinate labels:
    #
    #     A(2, 3)
    #     B(-1, 4)
    #
    _COORDINATE_LABEL_PATTERN = re.compile(
        r"\b([A-Z])\s*\("
        r"\s*-?\d+(?:\.\d+)?\s*,"
        r"\s*-?\d+(?:\.\d+)?\s*\)"
    )

    _COMMON_NON_LABEL_UPPERCASE = {
        "AI",
        "AM",
        "AN",
        "AND",
        "ARE",
        "AS",
        "AT",
        "BE",
        "BY",
        "CAN",
        "DO",
        "FOR",
        "FROM",
        "HAS",
        "HE",
        "IF",
        "IN",
        "IS",
        "IT",
        "ITS",
        "LET",
        "MAY",
        "NOT",
        "OF",
        "ON",
        "OR",
        "THE",
        "THIS",
        "TO",
        "USE",
        "WAS",
        "WE",
        "WITH",
        "YOU",
    }

    def analyze(
        self,
        context: Any,
        visual_input: Any | None = None,
    ) -> FigureCandidate:
        """
        Analyze a VisualCandidateContext.

        ``visual_input`` is accepted to establish the future vision-model
        boundary but is intentionally unused by this baseline analyzer.
        """

        del visual_input

        text = self._combined_text(context)

        figure_type = self._infer_figure_type(text)
        concepts = self._infer_concepts(text)
        labels = self._infer_labels(
            text=text,
            figure_type=figure_type,
        )

        description = self._build_description(
            figure_type=figure_type,
            labels=labels,
        )

        educational_relevance = self._infer_educational_relevance(
            context=context,
            text=text,
            figure_type=figure_type,
            concepts=concepts,
        )

        confidence = self._calculate_confidence(
            context=context,
            figure_type=figure_type,
            labels=labels,
            concepts=concepts,
        )

        geometry = self._build_geometry_hint(
            figure_type=figure_type,
        )

        educational = {
            "purpose": None,
            "learning_objectives": [],
            "explanation_strategy": None,
            "importance": (
                "potentially_relevant"
                if educational_relevance is True
                else None
            ),
        }

        interaction = {
            "modifiable": True,
            "can_add_elements": True,
            "can_remove_elements": True,
            "can_update_labels": True,
            "can_animate": True,
            "can_highlight": True,
            "can_transform": True,
            "allowed_operations": [
                "add",
                "remove",
                "update_label",
                "highlight",
                "animate",
                "transform",
            ],
        }

        evidence = {
            "analysis_method": "rule_based_text_evidence",
            "visual_input_used": False,
            "figure_type_explicit_in_text": figure_type is not None,
            "labels_detected_from_text": bool(labels),
            "concepts_detected_from_text": bool(concepts),
            "strong_figure_context": self._has_strong_figure_context(
                text
            ),
        }

        provenance = dict(
            getattr(context, "provenance", {}) or {}
        )

        provenance["semantic_analysis"] = (
            "rule_based_text_evidence"
        )

        metadata = {
            "semantic_analysis": {
                "method": "rule_based_text_evidence",
                "evidence": evidence,
            },
            "context": {
                "visual_region_id": getattr(
                    context,
                    "id",
                    None,
                ),
                "region_role": getattr(
                    context,
                    "region_role",
                    None,
                ),
                "repeated": bool(
                    getattr(
                        context,
                        "repeated",
                        False,
                    )
                ),
            },
        }

        return FigureCandidate(
            id=str(context.id),
            page=int(context.page_number),
            source_block_id=self._primary_source_block_id(
                context
            ),
            caption=getattr(
                context,
                "caption",
                None,
            ),
            description=description,
            figure_type=figure_type,
            labels=labels,
            geometry=geometry,
            rendering={},
            educational=educational,
            interaction=interaction,
            related_concepts=concepts,
            is_educationally_relevant=educational_relevance,
            confidence=confidence,
            provenance=provenance,
            metadata=metadata,
        )

    def analyze_many(
        self,
        contexts: Sequence[Any],
        visual_inputs: Sequence[Any] | None = None,
    ) -> list[FigureCandidate]:
        """Analyze multiple contextual candidates in order."""

        if visual_inputs is not None and len(visual_inputs) != len(
            contexts
        ):
            raise ValueError(
                "visual_inputs must have the same length as contexts"
            )

        results: list[FigureCandidate] = []

        for index, context in enumerate(contexts):
            visual_input = (
                visual_inputs[index]
                if visual_inputs is not None
                else None
            )

            results.append(
                self.analyze(
                    context,
                    visual_input,
                )
            )

        return results

    @staticmethod
    def _combined_text(context: Any) -> str:
        """Combine caption and nearby textual context."""

        values: list[str] = []

        caption = getattr(
            context,
            "caption",
            None,
        )

        if isinstance(caption, str) and caption.strip():
            values.append(caption)

        preceding = getattr(
            context,
            "preceding_text",
            None,
        )

        if isinstance(preceding, str) and preceding.strip():
            values.append(preceding)

        following = getattr(
            context,
            "following_text",
            None,
        )

        if isinstance(following, str) and following.strip():
            values.append(following)

        nearby = getattr(
            context,
            "nearby_text",
            [],
        )

        if isinstance(nearby, Sequence):
            values.extend(
                item
                for item in nearby
                if isinstance(item, str)
                and item.strip()
            )

        return " ".join(
            " ".join(values).split()
        )

    @classmethod
    def _infer_figure_type(
        cls,
        text: str,
    ) -> str | None:
        """
        Infer a figure type using whole-word/phrase matching.

        Generic terms such as ``function`` and ``graph`` do not imply
        a figure type unless they form an explicit ``function graph``
        or equivalent phrase.
        """

        normalized = " ".join(
            text.lower().split()
        )

        matches: list[tuple[int, str]] = []

        for figure_type, terms in cls._FIGURE_TYPE_PATTERNS:
            for term in terms:
                pattern = re.compile(
                    rf"(?<![a-z]){re.escape(term)}(?![a-z])",
                    flags=re.IGNORECASE,
                )

                match = pattern.search(normalized)

                if match:
                    matches.append(
                        (
                            match.start(),
                            figure_type,
                        )
                    )

        if not matches:
            return None

        matches.sort(
            key=lambda item: item[0]
        )

        return matches[0][1]

    @classmethod
    def _infer_concepts(
        cls,
        text: str,
    ) -> list[str]:
        """Extract explicitly mentioned mathematical concepts."""

        normalized = " ".join(
            text.lower().split()
        )

        concepts: list[str] = []

        for term in cls._CONCEPT_TERMS:
            pattern = re.compile(
                rf"(?<![a-z]){re.escape(term)}(?![a-z])",
                flags=re.IGNORECASE,
            )

            if pattern.search(normalized):
                canonical = cls._canonical_concept(term)

                if canonical not in concepts:
                    concepts.append(canonical)

        return concepts

    @staticmethod
    def _canonical_concept(term: str) -> str:
        """Normalize concept terminology."""

        mapping = {
            "angles": "angle",
            "triangles": "triangle",
            "circles": "circle",
            "vectors": "vector",
            "lines": "line",
            "points": "point",
            "graphs": "graph",
            "functions": "function",
            "trapezoid": "trapezium",
        }

        return mapping.get(
            term,
            term,
        )

    @classmethod
    def _infer_labels(
        cls,
        *,
        text: str,
        figure_type: str | None,
    ) -> list[str]:
        """
        Extract labels only when there is explicit figure-like evidence.

        We intentionally avoid interpreting arbitrary uppercase letters
        from ordinary prose as visual labels.

        Strong examples:

            triangle ABC
            quadrilateral ABCD
            point A
            vertices A, B and C
            A(2, 3), B(4, 5)
        """

        labels: list[str] = []

        def add_label(label: str) -> None:
            if label in cls._COMMON_NON_LABEL_UPPERCASE:
                return

            if label not in labels:
                labels.append(label)

        has_figure_context = (
            figure_type is not None
            or cls._has_strong_figure_context(text)
        )

        if not has_figure_context:
            return labels

        # Explicit point/vertex references.
        for match in cls._EXPLICIT_LABEL_PATTERN.finditer(text):
            add_label(
                match.group(1).upper()
            )

        # Coordinate points.
        for match in cls._COORDINATE_LABEL_PATTERN.finditer(text):
            add_label(
                match.group(1)
            )

        # Compact figure labels, e.g. ABC in "triangle ABC".
        if figure_type is not None:
            for match in cls._COMPACT_LABEL_PATTERN.finditer(text):
                sequence = match.group(1)

                if sequence in cls._COMMON_NON_LABEL_UPPERCASE:
                    continue

                # Avoid treating ordinary long acronyms as point sequences.
                if 2 <= len(sequence) <= 6:
                    for character in sequence:
                        add_label(character)

        return labels

    @classmethod
    def _has_strong_figure_context(
        cls,
        text: str,
    ) -> bool:
        """Return whether text explicitly refers to a visual/figure."""

        return bool(
            cls._FIGURE_REFERENCE_PATTERN.search(text)
        )

    @staticmethod
    def _build_description(
        *,
        figure_type: str | None,
        labels: Sequence[str],
    ) -> str | None:
        """Create a conservative description from explicit evidence."""

        if figure_type is None:
            return None

        description = (
            f"Visual candidate identified as a "
            f"{figure_type}"
        )

        if labels:
            description += (
                " with explicit labels "
                + ", ".join(labels)
            )

        return description + "."

    @staticmethod
    def _build_geometry_hint(
        *,
        figure_type: str | None,
    ) -> dict[str, Any]:
        """
        Build only a semantic geometry type hint.

        No coordinates or geometric relationships are invented.
        """

        if figure_type is None:
            return {}

        return {
            "type": figure_type,
            "elements": [],
            "source": "textual_semantic_hint",
        }

    @classmethod
    def _infer_educational_relevance(
        cls,
        *,
        context: Any,
        text: str,
        figure_type: str | None,
        concepts: Sequence[str],
    ) -> bool | None:
        """
        Infer educational relevance conservatively.

        Strong figure evidence:
            True

        Generic mathematical context only:
            None

        Empty context:
            None

        Repeated structural regions require explicit figure evidence
        before being marked educationally relevant.
        """

        del concepts

        repeated = bool(
            getattr(
                context,
                "repeated",
                False,
            )
        )

        strong_figure_context = cls._has_strong_figure_context(
            text
        )

        if figure_type is not None:
            return True

        if strong_figure_context and text.strip():
            return True

        if repeated:
            return None

        return None

    @classmethod
    def _calculate_confidence(
        cls,
        *,
        context: Any,
        figure_type: str | None,
        labels: Sequence[str],
        concepts: Sequence[str],
    ) -> float | None:
        """
        Calculate confidence in semantic interpretation.

        This confidence represents textual evidence only.

        Generic concepts receive very little confidence and cannot,
        by themselves, establish that the visual is a figure.
        """

        score = 0.0

        if figure_type is not None:
            score += 0.55

        if labels:
            score += 0.10

        if getattr(context, "caption", None):
            score += 0.10

        if cls._has_strong_figure_context(
            cls._combined_text(context)
        ):
            score += 0.15

        if concepts:
            score += 0.05

        if getattr(context, "nearby_text", None):
            score += 0.05

        if score == 0.0:
            return None

        return round(
            min(score, 1.0),
            3,
        )

    @staticmethod
    def _primary_source_block_id(
        context: Any,
    ) -> str | None:
        """Return the strongest available source-block reference."""

        block_ids = getattr(
            context,
            "source_block_ids",
            [],
        )

        if not block_ids:
            return None

        return str(block_ids[0])