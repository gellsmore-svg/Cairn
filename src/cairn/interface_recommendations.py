"""Traceable interface change recommendations for Cairn UI evidence."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from typing import Any

from cairn.layout_load import LayoutFinding, analyze_functional_layout
from cairn.ui_evidence import analyze_ui_simulation_report, UiEvidenceFinding


@dataclass
class RecommendationTrace:
    okf_file: str
    concept: str
    research: str | None = None


@dataclass
class InterfaceRecommendation:
    change: str
    rationale: str
    priority: str
    effort: str
    current_state: str
    future_state: str
    traceability: list[RecommendationTrace]
    future_svg: str | None = None


@dataclass
class InterfaceRecommendationReport:
    title: str
    recommendations: list[InterfaceRecommendation] = field(default_factory=list)
    references: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def recommend_interface_changes(evidence: dict[str, Any]) -> InterfaceRecommendationReport:
    """Generate deterministic, OKF-traceable UI change recommendations."""
    title = str(evidence.get("scenario") or evidence.get("label") or "Interface recommendations")
    recommendations: list[InterfaceRecommendation] = []

    for snapshot in evidence.get("layoutLoad", []):
        if isinstance(snapshot, dict):
            layout_report = analyze_functional_layout(snapshot)
            for finding in layout_report.findings:
                recommendations.append(_from_layout_finding(finding, snapshot))

    if not recommendations and {"viewport", "elements"}.issubset(evidence):
        layout_report = analyze_functional_layout(evidence)
        for finding in layout_report.findings:
            recommendations.append(_from_layout_finding(finding, evidence))

    if "metrics" in evidence or "observations" in evidence:
        ui_report = analyze_ui_simulation_report(evidence)
        for finding in ui_report.findings:
            recommendations.append(_from_ui_finding(finding))

    recommendations = _dedupe(recommendations)
    return InterfaceRecommendationReport(
        title=title,
        recommendations=recommendations,
        references=[
            "okf/concepts/hci-touchpoints.md",
            "okf/concepts/functional-layout-load.md",
            "okf/concepts/human-factors.md",
            "okf/concepts/augmentation-process.md",
        ],
    )


def format_interface_recommendations(
    report: InterfaceRecommendationReport,
    *,
    output_format: str = "markdown",
) -> str | dict[str, Any]:
    if output_format == "json":
        return report.to_dict()
    lines = [f"# Interface Change Recommendations: {report.title}", ""]
    if not report.recommendations:
        lines.append("No deterministic recommendations were generated from the supplied evidence.")
        return "\n".join(lines).strip()

    for index, rec in enumerate(report.recommendations, start=1):
        lines.append(f"## {index}. {rec.change}")
        lines.append(f"- Priority: {rec.priority}")
        lines.append(f"- Effort: {rec.effort}")
        lines.append(f"- Current state: {rec.current_state}")
        lines.append(f"- Future state: {rec.future_state}")
        lines.append(f"- Rationale: {rec.rationale}")
        lines.append("- Traceability:")
        for trace in rec.traceability:
            suffix = f"; research: {trace.research}" if trace.research else ""
            lines.append(f"  - `{trace.okf_file}` - {trace.concept}{suffix}")
        lines.append("")
    return "\n".join(lines).strip()


def future_state_svg(report: InterfaceRecommendationReport) -> str:
    """Render a simple SVG summary of the proposed future interface state."""
    width = 960
    row_h = 96
    height = max(220, 90 + row_h * max(1, len(report.recommendations)))
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="#ffffff" />',
        '<text x="32" y="42" font-family="Arial, sans-serif" font-size="24" font-weight="700" fill="#111827">Future Interface State</text>',
    ]
    if not report.recommendations:
        lines.append(_text(32, 92, "No recommendations generated.", 16, "#374151"))
    for index, rec in enumerate(report.recommendations, start=1):
        y = 72 + (index - 1) * row_h
        color = "#dc2626" if rec.priority == "high" else "#d97706" if rec.priority == "medium" else "#2563eb"
        lines.append(f'<rect x="32" y="{y}" width="896" height="76" rx="6" fill="#f8fafc" stroke="{color}" stroke-width="2" />')
        lines.append(_text(52, y + 28, f"{index}. {rec.change}", 15, "#111827"))
        lines.append(_text(52, y + 52, rec.future_state[:135], 13, "#374151"))
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def _from_layout_finding(finding: LayoutFinding, snapshot: dict[str, Any]) -> InterfaceRecommendation:
    if finding.factor == "label-field distance":
        change = "Move labels next to their associated controls."
        trace = "Functional layout load - label_field_distance"
    elif finding.factor == "evidence-action distance":
        change = "Group evidence, warnings, and the action they justify into one decision region."
        trace = "Functional layout load - evidence_action_distance"
    elif finding.factor == "column complexity":
        change = "Reduce cross-column scanning or make independent columns visually explicit."
        trace = "Functional layout load - column_complexity"
    elif finding.factor == "cumulative pointer travel":
        change = "Shorten the task path so the primary scan and pointer route follow the work sequence."
        trace = "Functional layout load - cumulative_pointer_travel"
    else:
        change = "Reduce avoidable layout traversal load."
        trace = f"Functional layout load - {finding.factor}"
    label = str(snapshot.get("label") or "measured layout")
    return InterfaceRecommendation(
        change=change,
        rationale=finding.reason + " " + finding.mitigation,
        priority="high" if finding.severity == "high" else "medium",
        effort="medium",
        current_state=f"{label}: {finding.reason}",
        future_state=finding.mitigation,
        traceability=[
            RecommendationTrace(
                okf_file="okf/concepts/functional-layout-load.md",
                concept=trace,
                research="Fitts's Law, Gestalt proximity/grouping, NN/g form grouping, Baymard form research",
            ),
            RecommendationTrace(
                okf_file="okf/concepts/hci-touchpoints.md",
                concept="perceptual_grouping / recognition_over_recall",
            ),
        ],
    )


def _from_ui_finding(finding: UiEvidenceFinding) -> InterfaceRecommendation:
    if finding.family == "functional_layout_load":
        traces = [
            RecommendationTrace("okf/concepts/functional-layout-load.md", "functional layout load"),
            RecommendationTrace("okf/concepts/hci-touchpoints.md", "cognitive aesthetic / perceptual grouping"),
        ]
    elif finding.family == "trust_automation" or "automation" in finding.factor:
        traces = [
            RecommendationTrace("okf/concepts/human-factors.md", "Trust And Automation"),
            RecommendationTrace("okf/concepts/augmentation-process.md", "HAI Bias And Trust Calibration", "Automation bias / trust calibration research"),
        ]
    elif finding.family == "augmentation_process":
        traces = [RecommendationTrace("okf/concepts/augmentation-process.md", finding.factor)]
    else:
        traces = [RecommendationTrace("okf/concepts/human-factors.md", f"{finding.family}: {finding.factor}")]
    return InterfaceRecommendation(
        change=finding.mitigation.rstrip(".") + ".",
        rationale=finding.reason,
        priority="high" if finding.impact == "high" else "medium",
        effort="medium",
        current_state=finding.reason,
        future_state=finding.mitigation,
        traceability=traces,
    )


def _dedupe(items: list[InterfaceRecommendation]) -> list[InterfaceRecommendation]:
    out: list[InterfaceRecommendation] = []
    seen: set[str] = set()
    for item in items:
        key = item.change.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def _text(x: int, y: int, value: str, size: int, fill: str) -> str:
    escaped = (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    return f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size}" fill="{fill}">{escaped}</text>'


def recommendations_json(report: InterfaceRecommendationReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


__all__ = [
    "InterfaceRecommendation",
    "InterfaceRecommendationReport",
    "RecommendationTrace",
    "format_interface_recommendations",
    "future_state_svg",
    "recommend_interface_changes",
    "recommendations_json",
]
