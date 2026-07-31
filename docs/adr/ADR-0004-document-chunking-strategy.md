# ADR-0004

## Title

Document Chunking Strategy

## Status

Accepted

## Context

Google Document AI Layout Parser has a page processing limit.
Knowledge Factory must support documents larger than this limit.

## Decision

Knowledge Factory processes PDFs using fixed 25-page chunks.

Rules:

- Maximum chunk size = 25 pages
- One chunk = One Document AI request
- Chunk results are merged
- One uploaded PDF produces one Canonical JSON

## Consequences

Advantages

- Predictable execution
- Simple retry model
- Technology independent
- Future OCR engines can be introduced without changing the canonical schema