# Canonical Document Schema

**Project:** Knowledge Factory  
**Document Version:** 1.0  
**Status:** Active  
**Type:** Canonical Data Model

---

# Purpose

This document defines the technology-independent canonical document model used throughout the Knowledge Factory platform.

All provider-specific outputs (Google Document AI today, additional providers in the future) must be transformed into this canonical representation before any downstream processing occurs.

The canonical model is the primary data contract within the platform.

---

# Design Principles

The canonical schema is designed to be:

- Technology independent
- Provider agnostic
- Versioned
- Extensible
- Human readable
- Machine processable
- Stable across provider changes

---

# Processing Flow

```text
Source Document
        │
        ▼
Document Processing Provider
        │
        ▼
Provider-specific Output
        │
        ▼
Provider Adapter
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
```

---

# Canonical Document Structure

```text
Document
│
├── Metadata
├── Source Information
├── Pages
├── Sections
├── Elements
├── Tables
├── Images
├── Relationships
└── Processing Metadata
```

---

# Metadata

Document-level information describing the processed document.

Examples include:

- Document ID
- Document Version
- Processing Timestamp
- Schema Version
- Language
- Page Count
- Processing Status

---

# Source Information

Captures information about the original document.

Examples include:

- Original filename
- Source location
- Provider
- MIME type
- File size
- Checksum

---

# Pages

Represents the physical pages within the source document.

Each page may contain:

- Text
- Images
- Tables
- Layout information
- Bounding regions

---

# Sections

Represents the logical organization of the document.

Examples:

- Chapter
- Heading
- Section
- Subsection

Sections are independent of page boundaries.

---

# Elements

Represents atomic content extracted from the document.

Examples:

- Paragraph
- Heading
- List
- Formula
- Caption
- Footnote
- Code block

---

# Tables

Represents structured tabular data.

Each table should preserve:

- Rows
- Columns
- Cell values
- Header information
- Cell relationships

---

# Images

Represents non-text visual content.

Examples include:

- Figures
- Diagrams
- Charts
- Illustrations

Associated metadata should be retained.

---

# Relationships

Defines logical relationships between document components.

Examples include:

- Parent-child hierarchy
- Cross references
- Page associations
- Table ownership
- Image ownership

---

# Processing Metadata

Captures information generated during processing.

Examples include:

- Processing provider
- Processing duration
- Validation status
- Confidence scores
- Processing warnings
- Processing errors

---

# Versioning

The canonical schema must include a schema version.

Schema evolution must:

- Preserve backward compatibility where possible.
- Avoid breaking downstream consumers.
- Document all schema changes.

---

# Validation Requirements

Every canonical document should satisfy the following:

- Valid schema version
- Required metadata present
- At least one page
- Consistent section hierarchy
- Valid element relationships
- No orphaned objects
- Successful structural validation

Documents failing validation must not be published.

---

# Extensibility

The canonical schema is designed to support future enhancements without redesign.

Potential extensions include:

- OCR confidence metadata
- AI-generated annotations
- Semantic tagging
- Domain-specific entities
- Knowledge graph relationships
- Additional document element types

---

# Relationship to Other Documents

| Document | Purpose |
|----------|---------|
| ARCHITECTURE.md | Overall platform architecture |
| PIPELINE.md | Processing pipeline |
| Storage Strategy.md | Storage architecture |
| Firestore Metadata.md | Metadata persistence |
| Infrastructure.md | Infrastructure architecture |

---

# Future Considerations

The canonical schema should remain independent of:

- Google Document AI
- Azure Document Intelligence
- Firestore
- Cloud Storage
- Any downstream application

Changes to providers or storage technologies must not require changes to the canonical document model.