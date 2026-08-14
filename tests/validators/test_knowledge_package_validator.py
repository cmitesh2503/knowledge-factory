import json

from services.integration.knowledge_package_builder import (
    KnowledgePackageBuilder,
)

from services.validators.knowledge_package_validator import (
    KnowledgePackageValidator,
)
from services.models import Concept

def test_knowledge_package_validator():

    with open(
        "tests/fixtures/matrices_1_10_canonical.json",
        encoding="utf-8",
    ) as f:

        canonical = json.load(f)

    package = KnowledgePackageBuilder().build(
        canonical
    )

    validator = KnowledgePackageValidator()

    errors = validator.validate(package)

    assert errors == []
    
def test_knowledge_package_validator_detects_invalid_concept_section():

    with open(
        "tests/fixtures/matrices_1_10_canonical.json",
        encoding="utf-8",
    ) as f:

        canonical = json.load(f)

    package = KnowledgePackageBuilder().build(
        canonical
    )

    package.concepts.append(
        Concept(
            id="concept-test",
            name="Invalid concept",
            section_number="99.99",
            page=1,
            block_id="test-block",
        )
    )

    validator = KnowledgePackageValidator()

    errors = validator.validate(package)

    assert (
        "Concept concept-test references "
        "unknown section 99.99."
        in errors
    )