# KNOWLEDGE_CONTRACT.md

# Knowledge Contract

**Version:** 2.0  
**Status:** Draft  
**Owner:** Aastha Global IT Solutions

---

# 1. Purpose

The Knowledge Contract defines the canonical educational knowledge model produced by Knowledge Factory.

It is the single source of truth shared between:

- Knowledge Factory
- MathVerse
- Future AI educational products

The contract guarantees that every consumer receives the same logical knowledge representation regardless of:

- OCR provider
- AI provider
- Storage implementation
- Document source
- Programming language

---

# 2. Objectives

The contract exists to ensure:

- Provider independence
- Stable interfaces
- Consistent knowledge representation
- Modular architecture
- Long-term maintainability

---

# 3. Ownership

## Knowledge Factory owns

Knowledge generation.

Knowledge Factory is responsible for producing:

- Canonical Document
- Educational Knowledge
- Knowledge Graph
- Semantic Chunks
- Embeddings
- Processing Metadata

Knowledge Factory never teaches students.

---

## MathVerse owns

Knowledge consumption.

MathVerse is responsible for:

- Teaching
- Voice conversations
- Whiteboard
- Image solving
- Mock tests
- Student memory
- Progress tracking
- Personalization

MathVerse never performs document extraction.

---

# 4. Canonical Knowledge Package

Every ingestion pipeline must produce exactly one Knowledge Package.

```

Knowledge Package

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
└── Metadata

```

Every consumer must rely only on this package.

---

# 5. Canonical Entities

The Knowledge Package consists of canonical entities.

## Document

Represents the original educational source.

Examples:

- NCERT textbook
- JEE book
- Teacher notes
- Sample paper
- Previous year paper

---

## Curriculum

Defines:

- Board
- Grade
- Subject
- Stream
- Academic Year

Examples:

- CBSE Grade 10 Mathematics
- JEE Main Mathematics

---

## Chapter

Represents a logical chapter.

Examples:

- Real Numbers
- Matrices
- Trigonometry

---

## Section

Represents a section inside a chapter.

---

## Concept

Represents an educational concept.

Examples:

- Matrix Addition
- Matrix Multiplication
- Euclid's Division Lemma

---

## Definition

Represents formal definitions.

---

## Formula

Represents mathematical formulae.

---

## Theorem

Represents mathematical theorems.

---

## Proof

Represents theorem proofs.

---

## Derivation

Represents mathematical derivations.

---

## Example

Represents worked textbook examples.

---

## Exercise

Represents textbook exercises.

---

## Figure

Represents educational diagrams.

Examples:

- Geometry
- Graphs
- Coordinate systems
- Flow diagrams

---

## Table

Represents educational tables.

---

## Relationship

Represents semantic relationships.

Examples:

Exercise

↓

Concept

↓

Formula

↓

Theorem

↓

Figure

---

# 6. Entity Relationships

Knowledge Factory must establish relationships between entities.

Examples:

Concept

↓

Formula

↓

Example

↓

Exercise

↓

Solution

Another example:

Theorem

↓

Proof

↓

Example

↓

Exam Questions

These relationships form the Knowledge Graph.

---

# 7. Semantic Chunks

Chunks are not page fragments.

Chunks are educational units.

Examples:

Concept Chunk

Formula Chunk

Theorem Chunk

Example Chunk

Exercise Chunk

Figure Chunk

Teacher Chunk

Chunk boundaries are determined by meaning rather than page size.

---

# 8. Embeddings

Embeddings are generated from semantic chunks.

Embeddings must never be generated directly from arbitrary PDF pages.

---

# 9. Provider Independence

Consumers must never depend on:

- Google Document AI
- Azure Document Intelligence
- OCR coordinates
- Provider metadata
- Storage provider

Provider-specific information remains internal to Knowledge Factory.

---

# 10. Canonical Rules

Every canonical entity must satisfy the following rules.

Identifiers are stable.

Relationships are explicit.

Provider metadata is excluded.

Educational meaning is preserved.

Schema evolution must remain backward compatible.

---

# 11. Responsibilities

Knowledge Factory is responsible for:

✓ Ingestion

✓ Normalization

✓ Knowledge Extraction

✓ Validation

✓ Knowledge Graph

✓ Chunking

✓ Embeddings

✓ Storage

MathVerse is responsible for:

✓ Retrieval

✓ Reasoning

✓ Teaching

✓ Voice

✓ Whiteboard

✓ Mock Tests

✓ Student Memory

---

# 12. Versioning

The Knowledge Contract is versioned.

Breaking changes require:

- Architecture review
- Version increment
- Migration strategy

---

# 13. Future Extensions

The contract is designed to support future educational domains.

Examples:

- Science
- Physics
- Chemistry
- Biology
- Computer Science

without redesigning the architecture.

---

# 14. Compliance

Every module in Knowledge Factory must comply with this contract.

Every consumer of Knowledge Factory must consume only the Knowledge Package defined here.

No module may introduce provider-specific behavior into the canonical knowledge model.

---

# 15. Source of Truth

This document is the authoritative contract shared by:

- Knowledge Factory
- MathVerse
- Future educational platforms

Any implementation that conflicts with this contract must be revised before implementation.