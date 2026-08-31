from __future__ import annotations

from services.extractors.chapter_extractor import (
    ChapterExtractor,
)
from services.extractors.section_extractor import (
    SectionExtractor,
)
from services.extractors.concept_extractor import (
    ConceptExtractor,
)
from services.extractors.formula_extractor import (
    FormulaExtractor,
)
from services.extractors.example_extractor import (
    ExampleExtractor,
)
from services.extractors.exercise_extractor import (
    ExerciseExtractor,
)
from services.extractors.figure_extractor import (
    FigureExtractor,
)
from services.models import KnowledgePackage
from services.extractors.table_extractor import (
    TableExtractor,
)


class KnowledgePackageBuilder:
    """
    Orchestrates the extraction layer and assembles
    one KnowledgePackage.

    Document AI is NOT called here.
    """

    def __init__(self) -> None:

        self.chapter_extractor = ChapterExtractor()
        self.section_extractor = SectionExtractor()
        self.concept_extractor = ConceptExtractor()
        self.formula_extractor = FormulaExtractor()
        self.example_extractor = ExampleExtractor()
        self.exercise_extractor = ExerciseExtractor()
        self.figure_extractor  = FigureExtractor()
        self.table_extractor  = TableExtractor()

    def build(
        self,
        canonical_document: dict,
    ) -> KnowledgePackage:

        document = canonical_document.get(
            "document",
            {},
        )
        
        return KnowledgePackage(
            schema_version=canonical_document.get(
                "schema_version",
                "1.0",
            ),
            document_id=document.get(
                "document_id",
                "",
            ),
            chapters=self.chapter_extractor.extract(
                canonical_document
            ).items,
            sections=self.section_extractor.extract(
                canonical_document
            ),
            concepts=self.concept_extractor.extract(
                canonical_document
            ),
            formulas=self.formula_extractor.extract(
                canonical_document
            ),
            examples=self.example_extractor.extract(
                canonical_document
            ),
            exercises=self.exercise_extractor.extract(
                canonical_document
            ),
            figures=self.figure_extractor.extract(
                canonical_document
            ),
            tables=self.table_extractor.extract(
                canonical_document
            ),
            
        )