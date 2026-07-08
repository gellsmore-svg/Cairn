"""Validation helpers for Cairn UI simulation scenarios."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any


ALLOWED_ACTIONS = {
    "assertVisible",
    "assertCountAtLeast",
    "assertTextIncludes",
    "click",
    "fill",
    "finding",
    "measureLayout",
    "popup",
    "press",
    "screenshot",
    "select",
    "waitForNonEmptyText",
    "waitForCountAtLeast",
    "waitForSelector",
    "waitForText",
}

HUMAN_LOAD_PHASES = {
    "awareness",
    "orientation",
    "execution",
    "feedback",
    "notification",
    "inspection",
    "recovery",
    "handoff",
    "adaptation",
    "organisational_pressure",
}

_SELECTOR_ACTIONS = {
    "assertVisible",
    "assertCountAtLeast",
    "assertTextIncludes",
    "click",
    "fill",
    "popup",
    "press",
    "select",
    "waitForNonEmptyText",
    "waitForCountAtLeast",
    "waitForSelector",
}


@dataclass
class ScenarioValidationReport:
    path: str | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        return {"path": self.path, "ok": self.ok, "errors": self.errors, "warnings": self.warnings}


def load_ui_scenario(path: str | Path) -> dict[str, Any]:
    """Load a UI simulation scenario JSON file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_ui_scenario(scenario: dict[str, Any], *, path: str | None = None) -> ScenarioValidationReport:
    """Validate a Cairn UI simulation scenario without requiring Playwright."""
    report = ScenarioValidationReport(path=path)
    if not isinstance(scenario, dict):
        report.errors.append("scenario must be a JSON object")
        return report

    _validate_optional_str(report, scenario, "name")
    _validate_optional_str(report, scenario, "baseUrl")
    _validate_optional_str(report, scenario, "output")
    _validate_positive_int(report, scenario, "timeout", optional=True)
    _validate_viewport(report, scenario)

    steps = scenario.get("steps")
    if not isinstance(steps, list) or not steps:
        report.errors.append("steps must be a non-empty list")
        return report

    human_load_count = 0
    for index, step in enumerate(steps):
        human_load_count += _validate_step(report, step, index)

    if human_load_count == 0:
        report.warnings.append("scenario has no humanLoad annotations; evidence will be mostly mechanical")
    return report


def format_scenario_validation_report(report: ScenarioValidationReport, *, output_format: str = "text") -> str | dict[str, Any]:
    """Format a scenario validation report."""
    if output_format == "json":
        return report.to_dict()

    subject = report.path or "scenario"
    lines = [f"{subject}: {'ok' if report.ok else 'invalid'}"]
    for error in report.errors:
        lines.append(f"ERROR: {error}")
    for warning in report.warnings:
        lines.append(f"WARNING: {warning}")
    return "\n".join(lines)


def _validate_step(report: ScenarioValidationReport, step: Any, index: int) -> int:
    prefix = f"steps[{index}]"
    if not isinstance(step, dict):
        report.errors.append(f"{prefix} must be an object")
        return 0

    action = step.get("action")
    if not isinstance(action, str):
        report.errors.append(f"{prefix}.action must be a string")
        return _validate_human_load(report, step, prefix)
    if action not in ALLOWED_ACTIONS:
        report.errors.append(f"{prefix}.action has unknown action {action!r}")

    if action in _SELECTOR_ACTIONS:
        _validate_required_str(report, step, "selector", prefix)
    if action in {"fill", "select"}:
        _validate_required_str(report, step, "value", prefix)
    if action == "press":
        _validate_required_str(report, step, "key", prefix)
    if action in {"waitForText", "assertTextIncludes"}:
        _validate_required_str(report, step, "text", prefix)
    if action in {"assertCountAtLeast", "waitForCountAtLeast"}:
        _validate_non_negative_int(report, step, "count", prefix)
    if action == "finding" and not isinstance(step.get("value"), dict):
        report.errors.append(f"{prefix}.value must be an object for finding actions")
    if action == "measureLayout":
        _validate_measure_layout(report, step, prefix)

    _validate_optional_str(report, step, "label", prefix=prefix)
    _validate_positive_int(report, step, "timeout", optional=True, prefix=prefix)
    _validate_non_negative_int(report, step, "index", optional=True, prefix=prefix)
    if "contextSwitch" in step and not isinstance(step["contextSwitch"], bool):
        report.errors.append(f"{prefix}.contextSwitch must be a boolean")

    human_load_count = _validate_human_load(report, step, prefix)
    if step.get("contextSwitch") and not step.get("humanLoad"):
        report.warnings.append(f"{prefix} marks a context switch without explaining humanLoad")
    return human_load_count


def _validate_measure_layout(report: ScenarioValidationReport, step: dict[str, Any], prefix: str) -> None:
    elements = step.get("elements")
    if not isinstance(elements, list) or not elements:
        report.errors.append(f"{prefix}.elements must be a non-empty list for measureLayout actions")
        return
    ids: set[str] = set()
    for idx, element in enumerate(elements):
        eprefix = f"{prefix}.elements[{idx}]"
        if not isinstance(element, dict):
            report.errors.append(f"{eprefix} must be an object")
            continue
        _validate_required_str(report, element, "id", eprefix)
        _validate_required_str(report, element, "selector", eprefix)
        if isinstance(element.get("id"), str):
            ids.add(element["id"])
        _validate_optional_str(report, element, "role", prefix=eprefix)
        _validate_optional_str(report, element, "label", prefix=eprefix)
        _validate_optional_str(report, element, "group", prefix=eprefix)
        _validate_non_negative_int(report, element, "index", optional=True, prefix=eprefix)

    relations = step.get("relations", [])
    if not isinstance(relations, list):
        report.errors.append(f"{prefix}.relations must be a list")
    else:
        for idx, relation in enumerate(relations):
            rprefix = f"{prefix}.relations[{idx}]"
            if not isinstance(relation, dict):
                report.errors.append(f"{rprefix} must be an object")
                continue
            source = relation.get("from") or relation.get("source")
            target = relation.get("to") or relation.get("target")
            if not isinstance(source, str) or not source:
                report.errors.append(f"{rprefix}.from/source must be a non-empty string")
            elif source not in ids:
                report.warnings.append(f"{rprefix} source {source!r} is not in elements")
            if not isinstance(target, str) or not target:
                report.errors.append(f"{rprefix}.to/target must be a non-empty string")
            elif target not in ids:
                report.warnings.append(f"{rprefix} target {target!r} is not in elements")
            _validate_optional_str(report, relation, "type", prefix=rprefix)

    sequence = step.get("sequence", [])
    if not isinstance(sequence, list) or not all(isinstance(item, str) for item in sequence):
        report.errors.append(f"{prefix}.sequence must be a list of element ids")
    else:
        for item in sequence:
            if item not in ids:
                report.warnings.append(f"{prefix}.sequence item {item!r} is not in elements")


def _validate_human_load(report: ScenarioValidationReport, step: dict[str, Any], prefix: str) -> int:
    if "humanLoad" not in step:
        return 0
    human_load = step["humanLoad"]
    if not isinstance(human_load, dict):
        report.errors.append(f"{prefix}.humanLoad must be an object")
        return 0

    phase = human_load.get("phase")
    if not isinstance(phase, str) or not phase:
        report.errors.append(f"{prefix}.humanLoad.phase must be a non-empty string")
    elif phase not in HUMAN_LOAD_PHASES:
        report.warnings.append(f"{prefix}.humanLoad.phase {phase!r} is not one of {sorted(HUMAN_LOAD_PHASES)}")

    demand = human_load.get("demand")
    if not isinstance(demand, str) or not demand.strip():
        report.errors.append(f"{prefix}.humanLoad.demand must be a non-empty string")

    systems = human_load.get("systems", [])
    if not isinstance(systems, list) or not all(isinstance(system, str) and system for system in systems):
        report.errors.append(f"{prefix}.humanLoad.systems must be a list of non-empty strings")
    return 1


def _validate_viewport(report: ScenarioValidationReport, scenario: dict[str, Any]) -> None:
    if "viewport" not in scenario:
        return
    viewport = scenario["viewport"]
    if not isinstance(viewport, dict):
        report.errors.append("viewport must be an object")
        return
    _validate_positive_int(report, viewport, "width", prefix="viewport")
    _validate_positive_int(report, viewport, "height", prefix="viewport")


def _validate_required_str(report: ScenarioValidationReport, data: dict[str, Any], key: str, prefix: str) -> None:
    if not isinstance(data.get(key), str) or not data[key]:
        report.errors.append(f"{prefix}.{key} must be a non-empty string")


def _validate_optional_str(
    report: ScenarioValidationReport,
    data: dict[str, Any],
    key: str,
    *,
    prefix: str | None = None,
) -> None:
    if key in data and not isinstance(data[key], str):
        report.errors.append(f"{prefix + '.' if prefix else ''}{key} must be a string")


def _validate_positive_int(
    report: ScenarioValidationReport,
    data: dict[str, Any],
    key: str,
    *,
    optional: bool = False,
    prefix: str | None = None,
) -> None:
    if optional and key not in data:
        return
    if not isinstance(data.get(key), int) or data[key] <= 0:
        report.errors.append(f"{prefix + '.' if prefix else ''}{key} must be a positive integer")


def _validate_non_negative_int(
    report: ScenarioValidationReport,
    data: dict[str, Any],
    key: str,
    prefix: str,
    *,
    optional: bool = False,
) -> None:
    if optional and key not in data:
        return
    if not isinstance(data.get(key), int) or data[key] < 0:
        report.errors.append(f"{prefix}.{key} must be a non-negative integer")
