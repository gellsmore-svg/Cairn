"""General report assembly for Cairn analysis artifacts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from cairn.human_factors import HumanFactorsReport, analyze_human_factors, format_human_factors_report
from cairn.interface_recommendations import (
    InterfaceRecommendationReport,
    format_interface_recommendations,
    future_state_svg,
    recommend_interface_changes,
)
from cairn.render import export_view
from cairn.render.model import RenderResult
from cairn.ui_evidence import UiHumanLoadReport, analyze_ui_simulation_report, format_ui_human_load_report


@dataclass
class CairnAnalysisReport:
    title: str
    executive_summary: str
    human_factors: HumanFactorsReport | None = None
    ui_evidence: UiHumanLoadReport | None = None
    recommendations: InterfaceRecommendationReport | None = None
    references: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "executive_summary": self.executive_summary,
            "human_factors": self.human_factors.to_dict() if self.human_factors else None,
            "ui_evidence": self.ui_evidence.to_dict() if self.ui_evidence else None,
            "recommendations": self.recommendations.to_dict() if self.recommendations else None,
            "references": self.references,
        }


def build_analysis_report(
    *,
    title: str = "Cairn Analysis Report",
    process_text: str | None = None,
    interface_evidence: dict[str, Any] | None = None,
) -> CairnAnalysisReport:
    human = analyze_human_factors(process_text) if process_text else None
    ui = analyze_ui_simulation_report(interface_evidence) if interface_evidence and ("metrics" in interface_evidence or "observations" in interface_evidence) else None
    recs = recommend_interface_changes(interface_evidence) if interface_evidence else None
    risk_count = sum(1 for step in human.steps if step.risk) if human else 0
    rec_count = len(recs.recommendations) if recs else 0
    summary = (
        f"Generated from Cairn semantic analysis. "
        f"Human-factor risk steps: {risk_count}. "
        f"Traceable interface recommendations: {rec_count}."
    )
    return CairnAnalysisReport(
        title=title,
        executive_summary=summary,
        human_factors=human,
        ui_evidence=ui,
        recommendations=recs,
        references=[
            "okf/concepts/human-factors.md",
            "okf/concepts/hci-touchpoints.md",
            "okf/concepts/functional-layout-load.md",
            "okf/concepts/augmentation-process.md",
        ],
    )


def format_analysis_report(report: CairnAnalysisReport, *, output_format: str = "markdown") -> str | dict[str, Any] | bytes:
    if output_format == "json":
        return report.to_dict()
    body = _markdown(report)
    if output_format == "markdown":
        return body
    result = RenderResult(profile="analysis_report", language="en", format="markdown", body=body)
    if output_format in {"html", "pdf"}:
        return export_view(result, output_format, {"title": report.title})
    raise ValueError(f"unsupported report format: {output_format}")


def _markdown(report: CairnAnalysisReport) -> str:
    lines = [f"# {report.title}", "", "## Executive Summary", "", report.executive_summary, ""]
    if report.ui_evidence:
        lines.append("## Current State UI Evidence")
        lines.append("")
        lines.append(str(format_ui_human_load_report(report.ui_evidence)))
        lines.append("")
    if report.human_factors:
        lines.append("## Human Factors And Augmentation")
        lines.append("")
        lines.append(str(format_human_factors_report(report.human_factors)))
        lines.append("")
    if report.recommendations:
        lines.append("## Traceable Interface Recommendations")
        lines.append("")
        lines.append(str(format_interface_recommendations(report.recommendations)))
        lines.append("")
        lines.append("## Future State Visual")
        lines.append("")
        lines.append("```svg")
        lines.append(future_state_svg(report.recommendations).strip())
        lines.append("```")
        lines.append("")
    if report.references:
        lines.append("## References")
        for ref in report.references:
            lines.append(f"- `{ref}`")
    return "\n".join(lines).strip()


__all__ = ["CairnAnalysisReport", "build_analysis_report", "format_analysis_report"]
