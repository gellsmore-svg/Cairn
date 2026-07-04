"""Cairn — process meta-language: spec, grammar, and conformance surface.

The repo is primarily a specification (SPEC.md / GRAMMAR.md). This package exposes
the small machine-readable conformance surface so runtimes can validate the plans
they produce against the grammar instead of embedding a private dialect.
"""

from cairn.conformance import (
    CANONICAL_PLAN,
    CONFORMANCE_VERSION,
    PLAN_CONSTRUCTS,
    PLAN_STATUSES,
    REQUIRED_PLAN_FIELDS,
    REQUIRED_STEP_FIELDS,
    REVISION_DECISIONS,
    STEP_STATUSES,
    is_conformant,
    validate_plan,
)

__all__ = [
    "CANONICAL_PLAN",
    "CONFORMANCE_VERSION",
    "PLAN_CONSTRUCTS",
    "PLAN_STATUSES",
    "REQUIRED_PLAN_FIELDS",
    "REQUIRED_STEP_FIELDS",
    "REVISION_DECISIONS",
    "STEP_STATUSES",
    "is_conformant",
    "validate_plan",
]
