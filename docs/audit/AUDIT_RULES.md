# Audit Rules

**Purpose**

This document defines how repository audits are performed.

These rules ensure every audit follows a consistent, evidence-based process.

---

# Audit Principles

## Inspect Before Recommend

Never recommend changes before reviewing the current implementation.

---

## No Assumptions

Recommendations must be based on repository evidence.

If information is missing, inspect the repository before making recommendations.

---

## Understand Existing Design

Determine why a component exists before suggesting changes.

Avoid redesigning without understanding the original intent.

---

## Architecture Alignment

Evaluate implementation against the approved architecture.

If differences exist:

- Record the finding.
- Discuss the impact.
- Recommend an approach.

---

## Classify Every Finding

Every finding must be classified as one of:

- KEEP
- MODIFY
- MOVE
- DELETE

Each recommendation must include justification.

---

## Record Before Implement

Significant findings must be documented before implementation begins.

---

## Incremental Reviews

Audit one logical component at a time.

Do not review multiple unrelated areas simultaneously.

---

## Evidence-Based Decisions

Recommendations should reference:

- Existing implementation
- Architecture documents
- ADRs
- Previous audit decisions

---

## Preserve Working Functionality

Avoid unnecessary refactoring.

Working code should only change when there is a clear benefit or defect.

---

## Close Findings

A finding is considered closed only when:

- The implementation is complete.
- Validation succeeds.
- The audit status is updated.

---

# Audit Workflow

Discover

↓

Inspect

↓

Understand

↓

Record Finding

↓

Discuss

↓

Approve

↓

Implement

↓

Validate

↓

Close

---

# Version History

| Version | Date | Description |
|----------|------------|------------------------------|
| 1.0.0 | 2026-07-30 | Initial audit rules |