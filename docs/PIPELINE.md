# PIPELINE.md

# Knowledge Factory Processing Pipeline

**Version:** 2.0  
**Status:** Draft  
**Owner:** Aastha Global IT Solutions

---

# 1. Purpose

The Knowledge Factory Pipeline defines the end-to-end process for transforming educational content into a structured, AI-ready Knowledge Package.

The pipeline is designed to be:

- Provider Independent
- Modular
- Scalable
- Deterministic where possible
- AI-assisted where educational understanding is required

The output of this pipeline is consumed by MathVerse and other educational AI systems.

---

# 2. End-to-End Pipeline

```
Educational Sources
        │
        ▼
Document Ingestion
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
Knowledge Validation
        │
        ▼
Knowledge Graph
        │
        ▼
Semantic Chunking
        │
        ▼
Embedding Generation
        │
        ▼
Knowledge Storage
        │
        ▼
Knowledge Package
        │
        ▼
MathVerse AI Tutor
```

---

# 3. Pipeline Stages

## Stage 1 – Document Ingestion

### Purpose

Acquire educational content from supported sources.

### Inputs

- PDF
- Images
- Teacher Notes
- Previous Year Papers
- Sample Papers
- Question Banks
- Revision Notes

### Outputs

Raw educational document.

---

## Stage 2 – Document Processing

### Purpose

Convert the raw document into a normalized document representation.

### Responsibilities

- OCR
- Reading Order
- Layout Detection
- Page Detection
- Basic Metadata
- Figure Detection (when available)
- Table Detection (when available)

### Outputs

Normalized document.

No educational understanding is performed in this stage.

---

## Stage 3 – Canonical Document Generation

### Purpose

Convert provider-specific output into the provider-independent Canonical Document.

### Responsibilities

- Normalize pages
- Normalize blocks
- Normalize metadata
- Normalize document identifiers
- Preserve provenance
- Remove provider-specific structures

### Output

Canonical Document

This is the first provider-independent artifact in the pipeline.

---

## Stage 4 – Knowledge Extraction

### Purpose

Transform document content into structured educational knowledge.

### Responsibilities

Extract:

- Curriculum
- Chapters
- Sections
- Concepts
- Definitions
- Formulae
- Theorems
- Proofs
- Derivations
- Examples
- Exercises
- Figures
- Tables
- Learning Objectives
- Prerequisites
- Common Mistakes
- Exam Tips

This stage may use AI models where semantic understanding is required.

### Output

Educational Knowledge Model

---

## Stage 5 – Knowledge Validation

### Purpose

Validate the extracted knowledge before storage.

### Validation Includes

- Missing entities
- Broken relationships
- Duplicate identifiers
- Invalid references
- Schema validation
- Mandatory field validation

Only validated knowledge proceeds further.

---

## Stage 6 – Knowledge Graph Generation

### Purpose

Build relationships between educational entities.

Examples

Exercise

↓

Concept

↓

Formula

↓

Theorem

↓

Example

↓

Figure

The Knowledge Graph enables intelligent retrieval by educational meaning rather than document location.

---

## Stage 7 – Semantic Chunking

### Purpose

Divide knowledge into educational learning units.

Chunk Types

- Concept Chunk
- Definition Chunk
- Formula Chunk
- Theorem Chunk
- Proof Chunk
- Example Chunk
- Exercise Chunk
- Figure Chunk
- Teacher Chunk

Chunks are determined by educational semantics, not page size.

---

## Stage 8 – Embedding Generation

### Purpose

Generate semantic embeddings for retrieval.

Embeddings are created from semantic chunks.

Embeddings are never created directly from raw PDF pages.

---

## Stage 9 – Knowledge Storage

### Purpose

Persist all reusable knowledge.

Storage includes:

- Canonical Document
- Knowledge Graph
- Semantic Chunks
- Embeddings
- Processing Metadata

Storage technology is implementation-specific and outside the scope of this document.

---

## Stage 10 – Knowledge Package

### Purpose

Assemble the final output produced by Knowledge Factory.

The Knowledge Package contains:

- Canonical Document
- Educational Knowledge
- Knowledge Graph
- Semantic Chunks
- Embeddings
- Metadata

The Knowledge Package is the only supported interface for downstream systems.

---

# 4. AI Usage

Knowledge Factory uses AI selectively.

## Deterministic Stages

- Document Ingestion
- Document Processing
- Canonical Document Generation
- Validation

These stages should produce repeatable results.

---

## AI-Assisted Stages

- Knowledge Extraction
- Relationship Discovery
- Semantic Enrichment

These stages may use Large Language Models or other AI techniques to understand educational content.

---

# 5. Error Handling

If a stage fails:

- The failure is logged.
- Processing metadata is updated.
- The pipeline stops for that document.
- Partial Knowledge Packages are not published.

---

# 6. Extensibility

New educational sources or AI providers should be added by extending individual stages without changing the overall pipeline.

Examples:

- New OCR provider
- New LLM
- New curriculum
- New document format

---

# 7. Design Principles

The pipeline follows these principles:

- Single Responsibility per stage
- Provider Independence
- Canonical First
- Educational Semantics over Document Structure
- Modular Processing
- Backward Compatibility

---

# 8. Relationship to MathVerse

Knowledge Factory ends at the Knowledge Package.

MathVerse begins where the Knowledge Package is consumed.

Knowledge Factory never performs:

- Tutoring
- Student interaction
- Voice conversation
- Whiteboard rendering
- Mock testing
- Personalized learning

Those responsibilities belong exclusively to MathVerse.

---

# 9. Future Pipeline Extensions

The pipeline is designed to support future capabilities such as:

- Multi-language processing
- Multi-board curricula
- Diagram understanding
- Handwritten content
- Video transcript ingestion
- Interactive educational content

without redesigning the architecture.

---

# 10. Source of Truth

This document defines the logical processing pipeline of Knowledge Factory.

Implementation details are defined separately.

Related Documents

- VISION.md
- SYSTEM_ARCHITECTURE.md
- KNOWLEDGE_CONTRACT.md
- CANONICAL_SCHEMA.md
- DATA_MODEL.md
- IMPLEMENTATION_ROADMAP.md