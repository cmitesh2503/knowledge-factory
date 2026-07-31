# Knowledge Factory Architecture

**Project:** Knowledge Factory  
**Document Version:** 1.0  
**Status:** Active  
**Type:** High-Level Architecture (Repository Root)

---

# Purpose

This document describes the high-level architecture of the Knowledge Factory platform.

It defines:

- What the platform is
- Why it exists
- The architectural principles
- Major system components
- Repository boundaries
- Relationship with downstream applications

Implementation details, infrastructure, schemas, and deployment procedures are documented separately under `docs/architecture/`.

---

# Vision

Knowledge Factory is a technology-independent document processing platform that transforms unstructured documents into a canonical knowledge representation that can be consumed by one or more downstream applications.

The platform is designed to isolate provider-specific implementations from business applications by introducing a canonical processing pipeline.

---

# Objectives

The platform aims to:

- Ingest documents from supported sources.
- Process documents using pluggable extraction providers.
- Convert provider output into a technology-independent canonical model.
- Validate and normalize extracted knowledge.
- Publish structured knowledge for downstream systems.
- Support multiple document providers without changing application logic.

---

# Design Principles

## Technology Independence

Provider-specific implementations must remain isolated from the canonical processing pipeline.

The canonical model must not depend on Google Document AI, Azure Document Intelligence, or any other vendor.

---

## Canonical First

The canonical representation is the primary artifact produced by the platform.

All downstream processing operates on the canonical model.

---

## Modular Processing

Each processing stage has a single responsibility.

Each stage can evolve independently without impacting the remaining pipeline.

---

## Infrastructure as Code

Cloud infrastructure is provisioned using Terraform.

Infrastructure changes must be version controlled.

---

## Extensibility

The platform must support additional providers, storage targets, and publishing mechanisms without redesigning the architecture.

---

# High-Level Architecture

```text
                Source Documents
                       │
                       ▼
                Document Ingestion
                       │
                       ▼
               Provider Adapter Layer
                       │
                       ▼
                Canonical Document
                       │
                       ▼
                 Normalization
                       │
                       ▼
                   Validation
                       │
                       ▼
                   Publishing
                       │
                       ▼
         Firestore / Storage / Consumers
```
                +----------------------+
                |   Cloud Storage      |
                |    Raw Bucket        |
                +----------+-----------+
                           |
                    Storage Event
                           |
                           ▼
                +----------------------+
                | Cloud Run Function   |
                |    (Gen2)            |
                +----------+-----------+
                           |
                           ▼
                +----------------------+
                | PDF Inspector        |
                | Count Pages          |
                +----------+-----------+
                           |
          +----------------+----------------+
          |                                 |
    Pages <= 25                      Pages > 25
          |                                 |
          ▼                                 ▼
 Document AI                    Split into 25-page chunks
                                         |
                                         ▼
                               Document AI per chunk
                                         |
                                         ▼
                               Merge Chunk Results
                                         |
                                         ▼
                               Canonical Mapper
                                         |
                                         ▼
                +-------------------------------+
                | Canonical JSON                |
                +---------------+---------------+
                                |
                +---------------+---------------+
                |                               |
                ▼                               ▼
        Processed Bucket             Firestore Metadata

---

# Core Components

## Ingestion

Receives documents from supported input sources.

---

## Provider Adapter

Converts provider-specific output into the internal canonical representation.

Examples include:

- Google Document AI
- Azure Document Intelligence
- Future OCR providers

---

## Canonical Model

Defines the technology-independent representation used throughout the platform.

This model is independent of any document extraction provider.

---

## Normalization

Standardizes extracted content into a consistent structure.

---

## Validation

Verifies completeness, consistency, and structural correctness before publication.

---

## Publishing

Publishes validated canonical knowledge to supported destinations.

Examples include:

- Firestore
- Cloud Storage
- Future knowledge repositories

---

# Repository Scope

This repository contains:

- Architecture
- Infrastructure as Code
- Canonical document design
- Processing pipeline design
- Storage architecture
- Deployment architecture
- Implementation documentation

---

# Out of Scope

This repository does **not** contain:

- AI tutoring
- Prompt engineering
- Student memory
- Chat APIs
- Business-specific application logic
- User interfaces

Those belong to consuming applications such as MathVerse.

---

# Relationship with MathVerse

```text
           Educational Documents
                    │
                    ▼
           Knowledge Factory
                    │
           Canonical Knowledge
                    │
                    ▼
               MathVerse
                    │
         AI Tutor / Student APIs
```

Knowledge Factory is responsible for producing structured knowledge.

MathVerse is responsible for consuming that knowledge.

---

# Documentation Structure

| Document | Purpose |
|----------|---------|
| README.md | Repository entry point |
| REPOSITORY_INDEX.md | Repository navigation |
| docs/architecture/ARCHITECTURE.md | Detailed architecture |
| docs/architecture/PIPELINE.md | Processing pipeline |
| docs/architecture/Canonical Schema.md | Canonical model |
| docs/architecture/Storage Strategy.md | Storage architecture |
| docs/architecture/Firestore Metadata.md | Firestore design |
| docs/architecture/Infrastructure.md | Infrastructure and Terraform |

---

# Architectural Principles

- Single responsibility for each processing stage.
- Canonical model independent of implementation technology.
- Provider adapters isolate external dependencies.
- Infrastructure managed as code.
- Documentation reflects implementation.
- Architecture describes the approved design.
- Repository evolves incrementally while preserving architectural consistency.

## Document Processing Strategy

Knowledge Factory treats every uploaded PDF as one logical ingestion job.

Google Document AI Layout Parser has a maximum page processing limit.
To support larger documents, the ingestion pipeline automatically
splits PDFs into fixed-size chunks before invoking Document AI.

### Processing Rules

- One uploaded PDF = One ingestion job
- Maximum Document AI chunk size = 25 pages
- One chunk = One Document AI request
- Chunking is an internal implementation detail
- One uploaded PDF always produces one Canonical JSON document

---

# Current Implementation Status

| Area | Status |
|------|--------|
| Repository Structure | Complete |
| Architecture Documentation | In Progress |
| Terraform Foundation | Complete |
| Storage Infrastructure | Complete |
| IAM | Complete |
| Firestore | Complete |
| Document AI | Complete |
| Cloud Run Infrastructure | In Progress |
| Processing Services | Planned |
| Integration Testing | Planned |

---

# References

- `README.md`
- `REPOSITORY_INDEX.md`
- `docs/architecture/`
- `infrastructure/terraform/`
