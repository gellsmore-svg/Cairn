"""Cairn's Keturah manifest — its LLM-consumable interfaces.

Built from cairn.conformance so the advertised grammar matches the enforced one.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version as _pkg_version

from keturah import Manifest, capability, manifest

from cairn.conformance import PLAN_CONSTRUCTS, PLAN_STATUSES, REQUIRED_PLAN_FIELDS


def _version() -> str:
    try:
        return _pkg_version("cairn")
    except PackageNotFoundError:
        return "0.0.0+source"


def build_manifest() -> Manifest:
    return manifest(
        "cairn",
        version=_version(),
        description="Process meta-language: plan/template grammar and a machine-readable conformance surface.",
        capabilities=[
            capability(
                "validate_plan",
                "Validate a Cairn PLAN against the grammar; returns a list of conformance errors "
                "(empty = conformant). Allowed step constructs: " + ", ".join(sorted(PLAN_CONSTRUCTS)) + ".",
                input_schema={"type": "object", "properties": {"plan": {"type": "object"}}, "required": ["plan"]},
                output_schema={
                    "type": "object",
                    "properties": {"errors": {"type": "array", "items": {"type": "string"}}},
                },
                tags=["validation", "plan"],
            ),
            capability(
                "render_plan",
                "Render a Cairn process description or PLAN dict into a simplified human-readable "
                "view (narrative_steps, simple_prose, operator, executive).",
                input_schema={
                    "type": "object",
                    "properties": {
                        "input_cairn": {"description": "Markdown text or PLAN object"},
                        "profile": {
                            "type": "string",
                            "enum": ["narrative_steps", "simple_prose", "operator", "executive", "narrative"],
                        },
                        "language": {"type": "string"},
                        "output_format": {"type": "string", "enum": ["markdown", "text", "json", "mermaid"]},
                        "options": {"type": "object"},
                    },
                    "required": ["input_cairn"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "body": {"type": "string"},
                        "profile": {"type": "string"},
                        "language": {"type": "string"},
                    },
                },
                tags=["render", "plan"],
            ),
            capability(
                "plan_schema",
                "The Cairn plan contract: required fields ("
                + ", ".join(REQUIRED_PLAN_FIELDS)
                + "), allowed constructs, and statuses ("
                + ", ".join(sorted(PLAN_STATUSES))
                + ").",
                kind="resource",
                tags=["schema"],
            ),
        ],
    )
