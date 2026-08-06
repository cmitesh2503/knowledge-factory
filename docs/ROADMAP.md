# ROADMAP.md

# Knowledge Factory Roadmap

**Version:** 2.0  
**Status:** Draft  
**Owner:** Aastha Global IT Solutions

---

# Purpose

This roadmap defines the implementation strategy for Knowledge Factory.

Knowledge Factory is developed independently from MathVerse.

Its responsibility ends when a validated Knowledge Package is produced.

---

# Current Status

## Completed

- Repository separation from MathVerse
- GCP foundation
- Terraform infrastructure
- Cloud Storage architecture
- Cloud Run deployment
- Firestore integration
- Document AI integration
- PDF ingestion pipeline
- Canonical document generation
- Provider-independent document processing
- Provider metadata separation
- Block normalization

---

# Phase 1 — Foundation

Status

Completed

Deliverables

- Repository structure
- Infrastructure
- CI/CD
- Storage
- Firestore
- Cloud Run
- Logging
- Monitoring

---

# Phase 2 — Canonical Document

Status

In Progress

Objective

Create a provider-independent canonical document.

Deliverables

- Canonical document model
- Page normalization
- Block normalization
- Metadata normalization
- Provider isolation
- Validation

Exit Criteria

Every supported provider produces the same Canonical Document.

---

# Phase 3 — Knowledge Extraction

Status

Planned

Objective

Convert Canonical Documents into educational knowledge.

Deliverables

- Curriculum extractor
- Chapter extractor
- Section extractor
- Concept extractor
- Definition extractor
- Formula extractor
- Theorem extractor
- Proof extractor
- Derivation extractor
- Example extractor
- Exercise extractor
- Figure extractor
- Table extractor

Exit Criteria

A complete educational knowledge model is produced.

---

# Phase 4 — Knowledge Validation

Status

Planned

Objective

Ensure extracted knowledge is complete and internally consistent.

Deliverables

- Schema validation
- Relationship validation
- Duplicate detection
- Missing entity detection
- Quality scoring

Exit Criteria

Only validated knowledge progresses further.

---

# Phase 5 — Knowledge Graph

Status

Planned

Objective

Build relationships between educational entities.

Deliverables

- Concept graph
- Formula graph
- Example graph
- Exercise graph
- Figure graph
- Cross-reference graph

Exit Criteria

Every entity is connected through semantic relationships.

---

# Phase 6 — Semantic Chunking

Status

Planned

Objective

Create educational retrieval units.

Chunk Types

- Concept
- Definition
- Formula
- Theorem
- Proof
- Example
- Exercise
- Figure
- Teacher Explanation

Exit Criteria

Chunks represent educational meaning instead of document pages.

---

# Phase 7 — Embedding Generation

Status

Planned

Objective

Generate vector embeddings for semantic retrieval.

Deliverables

- Chunk embeddings
- Version management
- Embedding metadata

Exit Criteria

Every semantic chunk has an embedding.

---

# Phase 8 — Knowledge Storage

Status

Planned

Objective

Persist reusable educational knowledge.

Deliverables

- Canonical documents
- Knowledge graph
- Semantic chunks
- Embeddings
- Metadata

Exit Criteria

Knowledge Package is completely stored.

---

# Phase 9 — Knowledge APIs

Status

Planned

Objective

Expose Knowledge Packages through stable APIs.

Capabilities

- Curriculum search
- Chapter search
- Concept lookup
- Formula lookup
- Exercise lookup
- Figure lookup

Exit Criteria

Knowledge can be consumed without accessing internal storage.

---

# Phase 10 — AI Enrichment

Status

Future

Objective

Improve educational quality using AI.

Capabilities

- Relationship discovery
- Learning objective generation
- Common mistake detection
- Exam tip generation
- Teaching explanation generation
- Difficulty estimation
- Prerequisite identification

Exit Criteria

Knowledge becomes teacher-ready.

---

# Phase 11 — Multi-Source Support

Status

Future

Supported Sources

- NCERT
- CBSE
- ICSE
- State Boards
- JEE Main
- JEE Advanced
- NEET
- Teacher Notes
- Coaching Material
- Previous Year Papers
- Sample Papers
- Revision Notes

---

# Phase 12 — Multi-Subject Support

Status

Future

Subjects

- Mathematics
- Physics
- Chemistry
- Biology
- Computer Science

---

# Phase 13 — Enterprise Features

Status

Future

Capabilities

- Multi-language support
- Versioned curriculum
- Incremental updates
- Knowledge quality dashboard
- Content review workflow
- Publisher integrations

---

# Out of Scope

The following belong to MathVerse.

- Student Chat
- Voice Tutor
- Whiteboard Teaching
- Image Question Solving
- Mock Tests
- Student Memory
- Adaptive Learning
- Learning Analytics
- Personalized Tutoring

---

# Success Criteria

Knowledge Factory is complete when:

✓ Educational content can be ingested.

✓ Canonical documents are generated.

✓ Educational knowledge is extracted.

✓ Knowledge graph is created.

✓ Semantic chunks are generated.

✓ Embeddings are generated.

✓ Knowledge Packages are published.

At this point, MathVerse becomes the consumer of Knowledge Factory.

---

# Related Documents

- VISION.md
- SYSTEM_ARCHITECTURE.md
- KNOWLEDGE_CONTRACT.md
- PIPELINE.md
- DATA_MODEL.md
- CANONICAL_SCHEMA.md