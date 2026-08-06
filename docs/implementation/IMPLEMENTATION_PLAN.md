# IMPLEMENTATION_PLAN.md

# Knowledge Factory Implementation Plan

**Version:** 2.0  
**Status:** Active  
**Owner:** Aastha Global IT Solutions

---

# Purpose

This document tracks the implementation of Knowledge Factory.

Unlike the Roadmap, this document is updated continuously during development.

Each task includes:

- Objective
- Files
- Acceptance Criteria
- Status

---

# Current Sprint

## Goal

Build the complete Knowledge Factory pipeline from PDF ingestion to a reusable Knowledge Package.

---

# Sprint 1 — Foundation

Status

✅ Completed

## Objectives

- Repository created
- Terraform infrastructure
- Cloud Storage
- Firestore
- Cloud Run
- CI/CD
- Logging
- Monitoring

---

# Sprint 2 — Canonical Document

Status

🟡 In Progress

---

## Task 2.1

### Provider-independent Document Processing

Status

✅ Completed

Files

- document_processor.py

Acceptance Criteria

- Provider-specific logic isolated
- Canonical block model produced
- Provider metadata separated

---

## Task 2.2

### Canonical Document Builder

Status

✅ Completed

Files

- canonical_document_builder.py

Acceptance Criteria

- Provider-independent document
- Stable IDs
- Canonical metadata

---

## Task 2.3

### Block Type Normalization

Status

✅ Completed

Acceptance Criteria

- Heading normalization
- Paragraph normalization
- Table normalization
- List normalization
- Image normalization

---

## Task 2.4

### Geometry Extraction

Status

🟡 Deferred

Reason

Current Layout Parser does not expose usable geometry for canonical blocks.

Decision

Continue without geometry.

Geometry will be revisited during Figure Extraction.

---

## Task 2.5

### Provider Metadata Separation

Status

✅ Completed

Acceptance Criteria

- Canonical JSON contains no provider-specific metadata.
- Provider metadata stored separately.

---

# Sprint 3 — Knowledge Extraction

Status

🔲 Planned

Objective

Transform Canonical Documents into educational knowledge.

---

## Task 3.1

Curriculum Extractor

Status

⬜ Not Started

Output

Curriculum entity

---

## Task 3.2

Chapter Extractor

Status

⬜ Not Started

Output

Chapter entities

---

## Task 3.3

Section Extractor

Status

⬜ Not Started

Output

Section entities

---

## Task 3.4

Concept Extractor

Status

⬜ Not Started

Output

Concept entities

---

## Task 3.5

Definition Extractor

Status

⬜ Not Started

Output

Definition entities

---

## Task 3.6

Formula Extractor

Status

⬜ Not Started

Output

Formula entities

---

## Task 3.7

Theorem Extractor

Status

⬜ Not Started

Output

Theorem entities

---

## Task 3.8

Proof Extractor

Status

⬜ Not Started

---

## Task 3.9

Derivation Extractor

Status

⬜ Not Started

---

## Task 3.10

Example Extractor

Status

⬜ Not Started

---

## Task 3.11

Exercise Extractor

Status

⬜ Not Started

---

## Task 3.12

Figure Extractor

Status

⬜ Not Started

Notes

This sprint revisits geometry extraction.

Expected outputs:

- Figure metadata
- Figure relationships
- Diagram references

---

## Task 3.13

Table Extractor

Status

⬜ Not Started

---

# Sprint 4 — Knowledge Validation

Status

⬜ Planned

Tasks

- Schema validation
- Duplicate detection
- Relationship validation
- Missing entity detection
- Quality scoring

---

# Sprint 5 — Knowledge Graph

Status

⬜ Planned

Tasks

- Concept graph
- Formula graph
- Example graph
- Exercise graph
- Figure graph

---

# Sprint 6 — Semantic Chunking

Status

⬜ Planned

Chunk Types

- Concept
- Formula
- Example
- Exercise
- Figure
- Teacher Explanation

---

# Sprint 7 — Embeddings

Status

⬜ Planned

Tasks

- Embedding generation
- Embedding versioning
- Metadata

---

# Sprint 8 — Knowledge Storage

Status

⬜ Planned

Tasks

- Firestore
- Cloud Storage
- Vector Database

---

# Sprint 9 — Knowledge APIs

Status

⬜ Planned

Tasks

- Curriculum API
- Chapter API
- Concept API
- Formula API
- Exercise API

---

# Sprint 10 — AI Enrichment

Status

⬜ Planned

Tasks

- Learning objectives
- Common mistakes
- Teaching explanations
- Prerequisites
- Difficulty estimation
- Exam tips

---

# Current Decisions

## Decision 001

Knowledge Factory is independent of MathVerse.

Status

Approved

---

## Decision 002

Canonical Document is provider-independent.

Status

Approved

---

## Decision 003

Knowledge Package is the only public output.

Status

Approved

---

## Decision 004

Semantic chunks replace page-based chunks.

Status

Approved

---

## Decision 005

Geometry extraction is deferred until Figure Extraction.

Status

Approved

---

# Next Task

The next implementation task is:

Sprint 3

Task 3.1

Curriculum Extractor

This marks the beginning of transforming documents into educational knowledge rather than document content.

---

# Related Documents

- VISION.md
- SYSTEM_ARCHITECTURE.md
- KNOWLEDGE_CONTRACT.md
- PIPELINE.md
- DATA_MODEL.md
- ROADMAP.md