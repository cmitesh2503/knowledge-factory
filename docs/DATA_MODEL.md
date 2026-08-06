# DATA_MODEL.md

# Knowledge Factory Data Model

**Version:** 2.0  
**Status:** Draft  
**Owner:** Aastha Global IT Solutions

---

# 1. Purpose

This document defines the logical data model used throughout Knowledge Factory.

It describes the educational entities, their responsibilities, and the relationships between them.

This document is implementation-independent.

It does not define:

- JSON schema
- Firestore collections
- Python classes
- Database tables

Those are defined separately.

---

# 2. Design Principles

The data model follows these principles.

- Educational First
- Provider Independent
- Canonical Representation
- Stable Identity
- Relationship Driven
- Extensible

Every educational entity represents knowledge rather than document structure.

---

# 3. Top-Level Model

```
Knowledge Package
│
├── Document
├── Curriculum
├── Chapters
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

---

# 4. Entity Model

## 4.1 Document

Represents the original educational source.

Examples

- NCERT Book
- JEE Book
- Teacher Notes
- Previous Year Paper
- Sample Paper

Responsibilities

- Source information
- Provenance
- Version
- Language
- Document metadata

---

## 4.2 Curriculum

Represents the educational curriculum.

Examples

- CBSE
- ICSE
- JEE Main
- JEE Advanced

Contains

- Board
- Grade
- Subject
- Stream
- Academic Year

---

## 4.3 Chapter

Represents one logical chapter.

Examples

- Real Numbers
- Matrices
- Trigonometry

Contains

- Sections
- Learning Outcomes
- Prerequisites

---

## 4.4 Section

Logical subdivision of a chapter.

Contains

- Concepts
- Examples
- Formulae
- Exercises

---

## 4.5 Concept

Represents one educational concept.

Examples

- Matrix Multiplication
- Euclid's Division Lemma

Contains

- Description
- Related Formulae
- Related Examples
- Related Exercises

---

## 4.6 Definition

Formal educational definitions.

Example

Definition of Matrix.

---

## 4.7 Formula

Represents mathematical expressions.

Examples

- Quadratic Formula
- Matrix Multiplication Rule

Contains

- Mathematical notation
- Description
- Variables
- Related concepts

---

## 4.8 Theorem

Represents mathematical theorems.

Contains

- Statement
- Assumptions
- Related proof
- Related examples

---

## 4.9 Proof

Represents theorem proofs.

Contains

- Ordered proof steps
- Supporting diagrams
- References

---

## 4.10 Derivation

Represents mathematical derivations.

Contains

- Step-by-step derivation
- Formula transformations

---

## 4.11 Example

Represents worked textbook examples.

Contains

- Problem
- Solution
- Teaching explanation
- Difficulty

---

## 4.12 Exercise

Represents textbook exercises.

Contains

- Questions
- Expected learning outcome
- Difficulty
- Marks
- Related concepts

---

## 4.13 Figure

Represents educational diagrams.

Examples

- Geometry
- Graph
- Coordinate Plane
- Matrix Illustration

Contains

- Caption
- Description
- Related concepts

---

## 4.14 Table

Represents structured educational tables.

---

## 4.15 Relationship

Represents semantic links between entities.

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

---

## 4.16 Semantic Chunk

Represents the smallest educational retrieval unit.

Chunk types include

- Concept
- Formula
- Example
- Exercise
- Figure
- Teacher Explanation

---

## 4.17 Embedding

Represents vector representation of semantic chunks.

Embeddings are generated from semantic knowledge.

Never directly from raw PDF pages.

---

## 4.18 Metadata

Represents processing information.

Includes

- Version
- Source
- Processing status
- Provenance

Provider-specific metadata is excluded.

---

# 5. Relationship Model

```
Curriculum
      │
      ▼
Chapter
      │
      ▼
Section
      │
      ▼
Concept
      │
 ┌────┼─────┐
 ▼    ▼     ▼
Formula Example Definition
 │      │
 ▼      ▼
Exercise Figure
 │
 ▼
Semantic Chunk
 │
 ▼
Embedding
```

---

# 6. Cardinality

Document

↓

One or More Chapters

Chapter

↓

One or More Sections

Section

↓

One or More Concepts

Concept

↓

Zero or More

- Formulae
- Examples
- Exercises
- Figures

Exercise

↓

One or More Questions

---

# 7. Identity

Every entity has a globally unique identifier.

Identifiers remain stable across processing.

Relationships always reference entity identifiers.

---

# 8. Versioning

The data model evolves through versioned releases.

Breaking changes require

- Contract update
- Schema update
- Migration strategy

---

# 9. Future Extensions

The model is designed to support

- Physics
- Chemistry
- Biology
- Computer Science
- Interactive Content
- Multimedia Learning

without structural redesign.

---

# 10. Related Documents

- VISION.md
- SYSTEM_ARCHITECTURE.md
- KNOWLEDGE_CONTRACT.md
- PIPELINE.md
- CANONICAL_SCHEMA.md