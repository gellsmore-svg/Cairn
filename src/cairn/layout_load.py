"""Functional layout load analysis for UI geometry.

The analyzer is deliberately simple and dependency-free. It consumes a JSON-like
description of UI element rectangles and logical relationships, then estimates
layout traversal load from distances, grouping, and action sequence.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import hypot
from typing import Any


@dataclass(frozen=True)
class LayoutElement:
    id: str
    x: float
    y: float
    width: float
    height: float
    role: str = "element"
    label: str | None = None
    group: str | None = None

    @property
    def center(self) -> tuple[float, float]:
        return (self.x + self.width / 2, self.y + self.height / 2)


@dataclass(frozen=True)
class LayoutRelation:
    source: str
    target: str
    type: str = "related"


@dataclass(frozen=True)
class LayoutFinding:
    family: str
    factor: str
    reason: str
    mitigation: str
    severity: str = "medium"


@dataclass(frozen=True)
class FunctionalLayoutLoadReport:
    viewport: dict[str, float]
    metrics: dict[str, float | int | str]
    findings: list[LayoutFinding] = field(default_factory=list)
    suggested_blocks: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def analyze_functional_layout(payload: dict[str, Any]) -> FunctionalLayoutLoadReport:
    """Analyze UI geometry and return a functional layout load report."""
    viewport = _viewport(payload)
    elements = _elements(payload.get("elements", []))
    by_id = {element.id: element for element in elements}
    relations = _relations(payload.get("relations", []))
    sequence = [str(item) for item in payload.get("sequence", []) if str(item) in by_id]
    diagonal = max(hypot(viewport["width"], viewport["height"]), 1)

    relation_distances = [
        _distance(by_id[rel.source], by_id[rel.target])
        for rel in relations
        if rel.source in by_id and rel.target in by_id
    ]
    label_distances = [
        _distance(by_id[rel.source], by_id[rel.target])
        for rel in relations
        if rel.type == "label_for" and rel.source in by_id and rel.target in by_id
    ]
    evidence_action_distances = [
        _distance(by_id[rel.source], by_id[rel.target])
        for rel in relations
        if rel.type == "evidence_to_action" and rel.source in by_id and rel.target in by_id
    ]
    pointer_travel = _sequence_distance([by_id[item] for item in sequence])
    columns = _column_count([element for element in elements if element.role in {"field", "input", "select", "button"}])

    metrics: dict[str, float | int | str] = {
        "element_count": len(elements),
        "field_count": sum(1 for element in elements if element.role in {"field", "input", "select"}),
        "action_count": sum(1 for element in elements if element.role in {"button", "action"}),
        "column_count": columns,
        "avg_related_distance_px": round(_avg(relation_distances), 1),
        "max_related_distance_px": round(max(relation_distances, default=0), 1),
        "avg_label_field_distance_px": round(_avg(label_distances), 1),
        "max_evidence_action_distance_px": round(max(evidence_action_distances, default=0), 1),
        "cumulative_pointer_travel_px": round(pointer_travel, 1),
        "cumulative_pointer_travel_viewports": round(pointer_travel / diagonal, 2),
    }
    metrics["layout_load"] = _layout_level(metrics, diagonal)

    findings = _findings(metrics, diagonal)
    return FunctionalLayoutLoadReport(
        viewport=viewport,
        metrics=metrics,
        findings=findings,
        suggested_blocks=_suggested_blocks(metrics, findings),
    )


def format_functional_layout_report(
    report: FunctionalLayoutLoadReport,
    *,
    output_format: str = "markdown",
) -> str | dict[str, Any]:
    """Format a functional-layout-load report."""
    if output_format == "json":
        return report.to_dict()

    lines = ["# Functional Layout Load", ""]
    lines.append("## Metrics")
    for key, value in report.metrics.items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    if report.findings:
        lines.append("## Findings")
        for finding in report.findings:
            lines.append(f"- **{finding.family}: {finding.factor}** - {finding.reason}")
            lines.append(f"  Mitigation: {finding.mitigation}")
        lines.append("")

    if report.suggested_blocks:
        lines.append("## Suggested Cairn Blocks")
        for name, value in report.suggested_blocks.items():
            lines.append(f"### {name}")
            lines.append("```cairn")
            lines.append(value)
            lines.append("```")
            lines.append("")

    return "\n".join(lines).strip()


def _viewport(payload: dict[str, Any]) -> dict[str, float]:
    raw = payload.get("viewport") if isinstance(payload.get("viewport"), dict) else {}
    return {
        "width": float(raw.get("width", 1280) or 1280),
        "height": float(raw.get("height", 800) or 800),
    }


def _elements(raw_elements: Any) -> list[LayoutElement]:
    elements: list[LayoutElement] = []
    if not isinstance(raw_elements, list):
        return elements
    for raw in raw_elements:
        if not isinstance(raw, dict) or not raw.get("id"):
            continue
        try:
            elements.append(
                LayoutElement(
                    id=str(raw["id"]),
                    x=float(raw.get("x", 0)),
                    y=float(raw.get("y", 0)),
                    width=float(raw.get("width", 0)),
                    height=float(raw.get("height", 0)),
                    role=str(raw.get("role", "element")),
                    label=str(raw["label"]) if raw.get("label") is not None else None,
                    group=str(raw["group"]) if raw.get("group") is not None else None,
                )
            )
        except (TypeError, ValueError):
            continue
    return elements


def _relations(raw_relations: Any) -> list[LayoutRelation]:
    relations: list[LayoutRelation] = []
    if not isinstance(raw_relations, list):
        return relations
    for raw in raw_relations:
        if not isinstance(raw, dict):
            continue
        source = raw.get("from") or raw.get("source")
        target = raw.get("to") or raw.get("target")
        if source and target:
            relations.append(LayoutRelation(source=str(source), target=str(target), type=str(raw.get("type", "related"))))
    return relations


def _distance(a: LayoutElement, b: LayoutElement) -> float:
    ax, ay = a.center
    bx, by = b.center
    return hypot(ax - bx, ay - by)


def _sequence_distance(elements: list[LayoutElement]) -> float:
    return sum(_distance(a, b) for a, b in zip(elements, elements[1:]))


def _avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0


def _column_count(elements: list[LayoutElement]) -> int:
    if not elements:
        return 0
    centers = sorted(element.center[0] for element in elements)
    columns = 1
    last = centers[0]
    for center in centers[1:]:
        if center - last > 160:
            columns += 1
            last = center
    return columns


def _layout_level(metrics: dict[str, float | int | str], diagonal: float) -> str:
    score = 0
    if float(metrics["avg_related_distance_px"]) > diagonal * 0.25:
        score += 2
    elif float(metrics["avg_related_distance_px"]) > diagonal * 0.12:
        score += 1
    if float(metrics["avg_label_field_distance_px"]) > 120:
        score += 2
    elif float(metrics["avg_label_field_distance_px"]) > 60:
        score += 1
    if float(metrics["max_evidence_action_distance_px"]) > diagonal * 0.35:
        score += 2
    elif float(metrics["max_evidence_action_distance_px"]) > diagonal * 0.18:
        score += 1
    if float(metrics["cumulative_pointer_travel_viewports"]) > 1.5:
        score += 2
    elif float(metrics["cumulative_pointer_travel_viewports"]) > 0.8:
        score += 1
    if int(metrics["column_count"]) >= 3:
        score += 2
    elif int(metrics["column_count"]) == 2:
        score += 1
    if score >= 6:
        return "high"
    if score >= 3:
        return "medium"
    return "low"


def _findings(metrics: dict[str, float | int | str], diagonal: float) -> list[LayoutFinding]:
    findings: list[LayoutFinding] = []
    if float(metrics["avg_related_distance_px"]) > diagonal * 0.12:
        findings.append(
            LayoutFinding(
                family="functional_layout_load",
                factor="related element distance",
                reason="Related fields or evidence/action pairs are spatially separated enough to increase scan effort.",
                mitigation="Group related fields, evidence, warnings, and actions into the same decision region.",
                severity="high" if float(metrics["avg_related_distance_px"]) > diagonal * 0.25 else "medium",
            )
        )
    if float(metrics["avg_label_field_distance_px"]) > 60:
        findings.append(
            LayoutFinding(
                family="functional_layout_load",
                factor="label-field distance",
                reason="Labels are far enough from fields that users may need extra visual association work.",
                mitigation="Place labels close to their controls and preserve clear whitespace grouping.",
                severity="high" if float(metrics["avg_label_field_distance_px"]) > 120 else "medium",
            )
        )
    if int(metrics["column_count"]) >= 2:
        findings.append(
            LayoutFinding(
                family="functional_layout_load",
                factor="column complexity",
                reason="The form/action surface spans multiple columns, increasing the chance of skipped or misread fields.",
                mitigation="Prefer one main scan path; reserve columns for clearly independent groups.",
                severity="high" if int(metrics["column_count"]) >= 3 else "medium",
            )
        )
    if float(metrics["cumulative_pointer_travel_viewports"]) > 0.8:
        findings.append(
            LayoutFinding(
                family="functional_layout_load",
                factor="cumulative pointer travel",
                reason="The likely interaction sequence requires substantial movement across the viewport.",
                mitigation="Move frequent next actions closer to the evidence and fields that justify them.",
                severity="high" if float(metrics["cumulative_pointer_travel_viewports"]) > 1.5 else "medium",
            )
        )
    return findings


def _suggested_blocks(metrics: dict[str, float | int | str], findings: list[LayoutFinding]) -> dict[str, str]:
    blocks: dict[str, str] = {
        "FUNCTIONAL_LAYOUT_LOAD": "\n".join(f"{key}: {value}" for key, value in metrics.items()),
    }
    if findings:
        blocks["HUMAN_FACTORS"] = "\n".join(f"{f.family}: {f.factor} - {f.reason}" for f in findings)
        blocks["IMPROVEMENT"] = "\n".join(f.mitigation for f in findings)
    return blocks
