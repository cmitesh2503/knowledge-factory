# Knowledge Factory Project Rules

**Project:** Knowledge Factory  
**Version:** 1.0.0  
**Status:** Active

---

# Purpose

This document defines the engineering principles and governance rules for the Knowledge Factory repository.

These rules apply to all contributors, reviews, implementations, and architectural decisions.

When uncertainty exists, this document takes precedence over personal preference.

---

# Core Principles

## Documentation Before Implementation

Architecture and design decisions must be documented before implementation begins.

---

## Inspect Before Modify

Never modify, rename, move, or delete existing files without first understanding their purpose.

Assumptions are not acceptable.

---

## Architecture Is the Source of Truth

Implementation must align with the approved architecture.

If implementation and architecture differ:

1. Identify the difference.
2. Discuss the reason.
3. Update architecture if approved.
4. Implement the change.

---

## Canonical First

The Knowledge Factory Canonical Schema is the first persisted structured artifact.

Vendor-specific formats are never exposed outside the ingestion pipeline.

---

## Incremental Development

Changes should be:

- Small
- Testable
- Reviewable
- Reversible

Avoid large refactoring without justification.

---

## Audit Before Implementation

Every major feature or infrastructure change should be reviewed before implementation.

The audit process exists to reduce risk, not slow development.

---

## Architecture Decisions

Significant architectural changes require an ADR before implementation.

Examples include:

- Changing cloud services
- Introducing new storage technologies
- Modifying the canonical schema
- Changing processing pipelines

---

## Repository as the Source of Truth

Repository documentation is authoritative.

Conversation history is not.

When there is uncertainty, review the repository first.

---

## Validation Before Completion

No task is considered complete until:

- Implementation is finished.
- Validation succeeds.
- Documentation is updated where required.

---

# Project Objectives

Knowledge Factory aims to be:

- Technology independent
- Modular
- Event driven
- Cloud native
- Infrastructure as Code
- Production ready
- Extensible

---

# Rule Changes

Changes to these rules require discussion and approval before implementation.

---

# Version History

| Version | Date | Description |
|----------|------------|------------------------------|
| 1.0.0 | 2026-07-30 | Initial project governance |