# CANONICAL_SCHEMA.md

# Knowledge Factory Canonical Schema

**Version:** 2.0  
**Status:** Draft  
**Owner:** Aastha Global IT Solutions

---

# 1. Purpose

This document defines the canonical schema produced by Knowledge Factory.

The canonical schema is the provider-independent representation of educational knowledge.

Every ingestion pipeline must produce this schema.

Every downstream application must consume this schema.

No downstream application should consume provider-specific formats.

---

# 2. Design Principles

The canonical schema must be:

- Provider Independent
- Educational First
- Stable
- Extensible
- Versioned
- Backward Compatible

---

# 3. Canonical Processing Flow

```
Educational Source
        │
        ▼
Document Processing
        │
        ▼
Canonical Document
        │
        ▼
Knowledge Extraction
        │
        ▼
Knowledge Package
```

The Canonical Document is an intermediate artifact.

The Knowledge Package is the final artifact.

---

# 4. Canonical Artifacts

Knowledge Factory produces two canonical artifacts.

## 4.1 Canonical Document

Purpose

Represents the normalized document.

Responsibilities

- Provider-independent
- Reading order
- Page structure
- Block structure
- Provenance

This artifact is used internally.

---

## 4.2 Knowledge Package

Purpose

Represents structured educational knowledge.

This is the only artifact exposed to external consumers.

---

# 5. Knowledge Package Structure

```
Knowledge Package

├── Metadata
├── Document
├── Curriculum
├── Chapters
├── Sections
├── Concepts
├── Definitions
├── Formulae
├── Theorems
├── Proofs
├── Derivations
├── Examples
├── Exercises
├── Figures
├── Tables
├── Relationships
├── Semantic Chunks
├── Embeddings
└── Processing Metadata
```

---

# 6. Canonical Entity Rules

Every entity must:

- Have a stable identifier
- Be provider independent
- Preserve educational meaning
- Support provenance
- Support future versioning

---

# 7. Metadata

Metadata describes the Knowledge Package itself.

Examples

- schema_version
- package_version
- language
- creation_timestamp
- source_identifier

Metadata never contains provider-specific information.

---

# 8. Document

Represents the original educational source.

Contains

- document identifier
- title
- source
- language
- edition
- publication
- provenance

---

# 9. Curriculum

Represents the educational curriculum.

Contains

- Board
- Grade
- Subject
- Stream
- Academic Year

Examples

CBSE Grade 10 Mathematics

JEE Main Mathematics

---

# 10. Educational Entities

Knowledge Factory extracts the following educational entities.

- Chapter
- Section
- Concept
- Definition
- Formula
- Theorem
- Proof
- Derivation
- Example
- Exercise
- Figure
- Table

These entities represent educational knowledge rather than document layout.

---

# 11. Relationships

Relationships describe educational meaning.

Examples

Concept

↓

Formula

↓

Example

↓

Exercise

Another example

Theorem

↓

Proof

↓

Example

Relationships must always reference canonical identifiers.

---

# 12. Semantic Chunks

Chunks represent educational learning units.

Chunk types include

- Concept
- Formula
- Theorem
- Example
- Exercise
- Figure
- Teacher Explanation

Chunks are independent of PDF pages.

---

# 13. Embeddings

Embeddings are generated only from semantic chunks.

Embeddings must never be generated directly from raw PDF pages.

---

# 14. Processing Metadata

Processing metadata is stored separately from educational knowledge.

Examples

- processing status
- processing duration
- processing version
- pipeline version

Processing metadata is not educational knowledge.

---

# 15. Provider Metadata

Provider metadata is never part of the canonical schema.

Examples

Google Document AI

Azure Document Intelligence

OCR confidence models

Bounding polygon formats

Storage provider metadata

These remain internal to Knowledge Factory.

---

# 16. Canonical Rules

Every Knowledge Package must satisfy the following.

✓ Stable identifiers

✓ Provider independence

✓ Educational semantics

✓ Relationship integrity

✓ Version compatibility

✓ Schema validation

---

# 17. Versioning

The canonical schema is versioned.

Breaking changes require

- Contract update
- Migration plan
- Version increment

---

# 18. Future Extensions

The schema is designed to support

- Multi-language
- Multi-board
- Multi-subject
- Interactive content
- Video lessons
- Teacher annotations

without redesigning the schema.

---

# 19. Related Documents

- VISION.md
- SYSTEM_ARCHITECTURE.md
- KNOWLEDGE_CONTRACT.md
- PIPELINE.md
- DATA_MODEL.md
- STORAGE_MODEL.md