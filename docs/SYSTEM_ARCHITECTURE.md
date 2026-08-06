# SYSTEM_ARCHITECTURE.md

# Knowledge Factory System Architecture

**Version:** 2.0  
**Status:** Draft  
**Owner:** Aastha Global IT Solutions

---

# 1. Overview

Knowledge Factory is a provider-independent educational knowledge engineering platform.

It transforms educational content into a structured, canonical knowledge model that can be consumed by AI-powered educational applications such as MathVerse.

The platform separates knowledge generation from knowledge consumption.

---

# 2. High-Level Architecture

```
                    Educational Sources
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  NCERT Books                                                │
│  CBSE Books                                                 │
│  JEE Books                                                  │
│  Teacher Notes                                              │
│  Previous Year Papers                                       │
│  Sample Papers                                              │
│  Revision Notes                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                  Knowledge Factory
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Document Ingestion                                         │
│          │                                                  │
│          ▼                                                  │
│  Document Processing                                        │
│          │                                                  │
│          ▼                                                  │
│  Canonical Document                                         │
│          │                                                  │
│          ▼                                                  │
│  Knowledge Extraction                                       │
│          │                                                  │
│          ▼                                                  │
│  Knowledge Graph                                            │
│          │                                                  │
│          ▼                                                  │
│  Semantic Chunking                                          │
│          │                                                  │
│          ▼                                                  │
│  Embedding Generation                                       │
│          │                                                  │
│          ▼                                                  │
│  Knowledge Storage                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                  Knowledge Package
                            │
                            ▼
                  MathVerse AI Tutor
```

---

# 3. Architectural Principles

The system is designed around the following principles.

## Provider Independent

Knowledge Factory must not depend on a specific OCR or AI provider.

Supported providers may include:

- Google Document AI
- Azure Document Intelligence
- AWS Textract
- Open Source OCR

Every provider must produce the same canonical output.

---

## Canonical First

Every downstream component consumes the canonical knowledge model.

No downstream component should understand provider-specific formats.

---

## Modular Design

Every stage has one responsibility.

```
Ingestion

↓

Processing

↓

Canonicalization

↓

Knowledge Extraction

↓

Validation

↓

Knowledge Graph

↓

Chunking

↓

Embeddings

↓

Storage
```

---

## AI-Assisted Understanding

Artificial Intelligence is introduced only after deterministic document processing.

AI is responsible for:

- Educational understanding
- Knowledge extraction
- Relationship generation
- Semantic enrichment

AI is **not** responsible for document normalization.

---

# 4. Repository Responsibilities

## Knowledge Factory

Knowledge Factory owns:

- Document ingestion
- OCR integration
- Canonical document generation
- Educational knowledge extraction
- Knowledge graph generation
- Chunk generation
- Embedding generation
- Storage
- Knowledge APIs

Knowledge Factory never teaches students.

---

## MathVerse

MathVerse owns:

- Teacher Engine
- Student interactions
- Voice tutoring
- Whiteboard teaching
- Diagram rendering
- Image question solving
- Mock tests
- Adaptive learning
- Student memory
- Progress tracking

MathVerse never performs document ingestion.

---

# 5. Processing Pipeline

The platform processes every document through the following stages.

## Stage 1

Document Ingestion

Input:

- PDF
- Images
- Educational Documents

Output:

Raw document.

---

## Stage 2

Document Processing

Responsibilities:

- OCR
- Reading order
- Layout detection
- Basic metadata

Output:

Normalized document structure.

---

## Stage 3

Canonical Document Generation

Responsibilities:

- Provider-independent representation
- Canonical metadata
- Canonical pages
- Canonical blocks

Output:

Canonical Document.

---

## Stage 4

Knowledge Extraction

Responsibilities:

Extract educational entities.

Examples:

- Chapters
- Sections
- Concepts
- Definitions
- Formulae
- Theorems
- Proofs
- Examples
- Exercises
- Figures
- Tables

Output:

Structured educational knowledge.

---

## Stage 5

Knowledge Graph

Responsibilities:

Build relationships.

Example:

```
Exercise

↓

Concept

↓

Formula

↓

Theorem

↓

Figure
```

---

## Stage 6

Semantic Chunking

Chunk educational knowledge into reusable learning units.

Examples:

- Concept Chunk
- Formula Chunk
- Example Chunk
- Exercise Chunk
- Figure Chunk
- Teacher Chunk

---

## Stage 7

Embedding Generation

Generate semantic embeddings for retrieval.

Embeddings are created from semantic chunks rather than arbitrary pages.

---

## Stage 8

Knowledge Storage

Persist:

- Canonical Document
- Knowledge Graph
- Semantic Chunks
- Embeddings
- Processing Metadata

---

# 6. Knowledge Package

Knowledge Factory produces a Knowledge Package.

The package contains:

- Canonical Document
- Educational Knowledge
- Knowledge Graph
- Semantic Chunks
- Embeddings
- Processing Metadata

The Knowledge Package is the only interface exposed to consumer applications.

---

# 7. Integration with MathVerse

MathVerse interacts only with the Knowledge Package.

MathVerse does not access:

- PDFs
- OCR
- Provider metadata
- Processing pipeline

Knowledge Factory completely abstracts document processing.

---

# 8. Scalability

The architecture is designed to support:

- Multiple educational boards
- Multiple subjects
- Multiple languages
- Multiple AI providers
- Multiple OCR providers
- Multiple downstream AI applications

without redesigning the system.

---

# 9. Source of Truth

This document defines the system architecture.

Detailed specifications are defined in:

- KNOWLEDGE_CONTRACT.md
- PIPELINE.md
- CANONICAL_SCHEMA.md
- DATA_MODEL.md