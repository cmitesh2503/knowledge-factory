"""
Knowledge Factory

Base Extractor

Defines the common extraction lifecycle for all deterministic
Knowledge Factory extractors.

All extractors follow the same pipeline:

Canonical Document
        │
        ▼
Find Candidates
        │
        ▼
Validate Candidates
        │
        ▼
Build Domain Models
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")
C = TypeVar("C")


class BaseExtractor(ABC, Generic[C, T]):
    """
    Base class for all Knowledge Factory extractors.

    C = Candidate model
    T = Domain model
    """

    def extract(self, canonical_document: dict) -> list[T]:
        """
        Standard deterministic extraction pipeline.
        """

        candidates = self.find_candidates(canonical_document)

        candidates = self.validate_candidates(candidates)

        return self.build(candidates)

    @abstractmethod
    def find_candidates(self, canonical_document: dict) -> list[C]:
        """
        Locate extraction candidates from the Canonical Document.
        """
        raise NotImplementedError

    def validate_candidates(self, candidates: list[C]) -> list[C]:
        """
        Optional validation hook.

        Child extractors may override this method.
        """
        return candidates

    @abstractmethod
    def build(self, candidates: list[C]) -> list[T]:
        """
        Convert validated candidates into domain models.
        """
        raise NotImplementedError