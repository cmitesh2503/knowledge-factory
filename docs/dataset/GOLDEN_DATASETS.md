# REFERENCE_DATASET.md

# Knowledge Factory Reference Dataset

**Version:** 1.0  
**Status:** Active  
**Owner:** Aastha Global IT Solutions

---

# 1. Purpose

This document defines the official reference datasets used for the design, implementation, testing, and validation of Knowledge Factory.

Every new feature, extractor, validator, and pipeline stage must be verified against these datasets before being considered complete.

The reference datasets serve as the benchmark for ensuring consistent behavior across all versions of Knowledge Factory.

---

# 2. Objectives

The reference datasets ensure:

- Consistent development
- Repeatable testing
- Regression testing
- Quality validation
- Architecture verification
- AI extraction benchmarking

---

# 3. Dataset Categories

Knowledge Factory maintains reference datasets for different educational content.

## 3.1 Textbooks

Examples

- NCERT Mathematics
- NCERT Science
- NCERT Physics
- NCERT Chemistry

Purpose

Validate:

- Chapter extraction
- Section extraction
- Concept extraction
- Formula extraction
- Figures
- Tables

---

## 3.2 Question Banks

Examples

- NCERT Exercises
- JEE Main
- JEE Advanced
- Previous Year Questions

Purpose

Validate:

- Exercise extraction
- Solution extraction
- Difficulty classification
- Concept mapping

---

## 3.3 Teacher Content

Examples

- Teacher Notes
- Coaching Material
- Revision Notes

Purpose

Validate:

- Teaching explanations
- Common mistakes
- Exam tips
- Learning objectives

---

## 3.4 Diagrams

Examples

- Geometry
- Coordinate Geometry
- Graphs
- Flow Diagrams

Purpose

Validate:

- Figure extraction
- Diagram metadata
- Whiteboard support

---

# 4. Current Golden Dataset

The following dataset is used during the initial implementation.

Dataset Name

NCERT Mathematics

Board

CBSE

Grade

10

Subject

Mathematics

Reference Chapter

Matrices

Reason

Contains:

- Headings
- Sections
- Formulae
- Worked examples
- Exercises
- Mathematical notation
- Multi-page content

This chapter is used as the primary benchmark during development.

---

# 5. Validation Matrix

Every module must be validated using the reference dataset.

| Module | Validation |
|----------|------------|
| PDF Ingestion | ✅ |
| Document Processing | ✅ |
| Canonical Document | ✅ |
| Chapter Extraction | ✅ |
| Concept Extraction | ✅ |
| Formula Extraction | ✅ |
| Exercise Extraction | ✅ |
| Figure Extraction | ✅ |
| Knowledge Graph | ✅ |
| Semantic Chunking | ✅ |
| Embeddings | ✅ |

---

# 6. Acceptance Criteria

A dataset is considered fully supported when:

- Canonical document is generated.
- Educational entities are extracted.
- Relationships are generated.
- Semantic chunks are created.
- Embeddings are generated.
- Validation passes without critical errors.

---

# 7. Future Datasets

The reference library will expand to include:

- CBSE (Grades 6–12)
- ICSE
- State Boards
- JEE Main
- JEE Advanced
- NEET
- Physics
- Chemistry
- Biology
- Computer Science

Each dataset will have its own validation report.

---

# 8. Versioning

Reference datasets are versioned.

Changes to a dataset require:

- Dataset version increment
- Validation rerun
- Regression testing

---

# 9. Related Documents

- VISION.md
- KNOWLEDGE_CONTRACT.md
- DATA_MODEL.md
- CANONICAL_SCHEMA.md
- IMPLEMENTATION_PLAN.md