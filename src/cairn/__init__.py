"""Cairn — process meta-language: spec, grammar, and conformance surface.

The repo is primarily a specification (SPEC.md / GRAMMAR.md). This package exposes
the machine-readable conformance surface and simplified view generation for plans
and process descriptions.
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
from cairn.grammar import (
    CairnDocument,
    document_to_dict,
    document_to_plan,
    extract_cairn_source,
    parse_document,
    validate_document,
)
from cairn.render import export_view, register_exporter, registered_exporters, registered_profiles, render_plan

__all__ = [
    "CANONICAL_PLAN",
    "CairnDocument",
    "CONFORMANCE_VERSION",
    "PLAN_CONSTRUCTS",
    "PLAN_STATUSES",
    "REQUIRED_PLAN_FIELDS",
    "REQUIRED_STEP_FIELDS",
    "REVISION_DECISIONS",
    "STEP_STATUSES",
    "document_to_dict",
    "document_to_plan",
    "extract_cairn_source",
    "is_conformant",
    "parse_document",
    "export_view",
    "register_exporter",
    "registered_exporters",
    "registered_profiles",
    "render_plan",
    "validate_document",
    "validate_plan",
]