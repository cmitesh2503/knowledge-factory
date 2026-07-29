# Knowledge Factory Architecture

**Version:** 1.0  
**Status:** Active  
**Last Updated:** 2026-07-29

---

## Overview

This directory contains the official architecture documentation for the **Knowledge Factory** platform.

Knowledge Factory is a cloud-native data engineering platform that transforms educational documents into a technology-independent canonical knowledge model.

These documents define the architecture, design decisions, storage strategy, and data pipelines. They serve as the single source of truth for all infrastructure and application development.

---

## Documentation Index

| Document | Purpose |
|----------|---------|
| ARCHITECTURE.md | Overall system architecture and design principles |
| PIPELINE.md | End-to-end processing pipelines |
| ADR-001 | Canonical schema decision |
| ADR-002 | Ingestion pipeline design |
| ADR-003 | Storage strategy |
| ADR-004 | Firestore metadata catalog |

---

## Guiding Principles

- Documentation First Development (DFD)
- Infrastructure as Code (Terraform)
- Event-Driven Architecture
- Technology Independence
- Canonical Data Model
- Cloud-Native Design
- Modular Pipelines
- Reusable Components

---

## Architecture Version

Current Version: **Knowledge Factory v1.0**

---

## Repository Structure

```
docs/
└── architecture/
    README.md
    ARCHITECTURE.md
    PIPELINE.md
    ADR-001-canonical-schema.md
    ADR-002-ingestion-pipeline.md
    ADR-003-storage-strategy.md
    ADR-004-firestore-catalog.md
```

---

## Document Ownership

These documents are maintained together with the source code. Any architectural change must update the relevant documentation before implementation.