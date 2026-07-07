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
from cairn.human_factors import (
    analyze_human_factors,
    build_human_factors_prompt,
    format_human_factors_report,
    interpret_human_factors,
)
from cairn.llm_adapters import CommandLLMProvider, HoglahLLMProvider, LLMRequest, LLMResponse
from cairn.live_observer import analyze_live_observations, format_live_observation_report
from cairn.render import export_view, register_exporter, registered_exporters, registered_profiles, render_plan
from cairn.ui_evidence import (
    analyze_ui_simulation_report,
    build_ui_roleplay_prompt,
    format_cairn_annotation_snippet,
    format_ui_human_load_report,
    interpret_ui_experience,
)
from cairn.ui_scenarios import format_scenario_validation_report, validate_ui_scenario

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
    "analyze_human_factors",
    "analyze_live_observations",
    "analyze_ui_simulation_report",
    "build_ui_roleplay_prompt",
    "build_human_factors_prompt",
    "CommandLLMProvider",
    "HoglahLLMProvider",
    "format_cairn_annotation_snippet",
    "format_human_factors_report",
    "format_live_observation_report",
    "format_scenario_validation_report",
    "format_ui_human_load_report",
    "interpret_human_factors",
    "interpret_ui_experience",
    "LLMRequest",
    "LLMResponse",
    "is_conformant",
    "parse_document",
    "export_view",
    "register_exporter",
    "registered_exporters",
    "registered_profiles",
    "render_plan",
    "validate_document",
    "validate_plan",
    "validate_ui_scenario",
]
