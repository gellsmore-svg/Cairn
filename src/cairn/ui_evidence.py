"""Human-load analysis for Cairn UI simulation reports."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class UiEvidenceFinding:
    family: str
    factor: str
    reason: str
    mitigation: str
    probability: str = "medium"
    impact: str = "medium"


@dataclass
class UiEvidenceRisk:
    probability: str
    impact: str
    confidence: str
    score: str
    rationale: str


@dataclass
class UiHumanLoadReport:
    scenario: str
    metrics: dict[str, int]
    phases: dict[str, list[str]]
    systems: list[str]
    findings: list[UiEvidenceFinding] = field(default_factory=list)
    risk: UiEvidenceRisk | None = None
    suggested_blocks: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def analyze_ui_simulation_report(report: dict[str, Any]) -> UiHumanLoadReport:
    """Summarise a `cairn-ui-sim` report as human-load evidence."""
    metrics = {key: int(value) for key, value in dict(report.get("metrics", {})).items()}
    observations = list(report.get("observations", []))
    phases = _phase_demands(observations)
    systems = sorted(_systems(observations))
    findings = _findings(report, metrics, phases, systems)
    risk = _risk(findings, metrics, bool(report.get("errors")))
    return UiHumanLoadReport(
        scenario=str(report.get("scenario") or "UI simulation"),
        metrics=metrics,
        phases=phases,
        systems=systems,
        findings=findings,
        risk=risk,
        suggested_blocks=_suggested_blocks(metrics, phases, systems, findings, risk),
    )


def format_ui_human_load_report(report: UiHumanLoadReport, *, output_format: str = "markdown") -> str | dict[str, Any]:
    """Format a UI human-load report as Markdown or a JSON-compatible dict."""
    if output_format == "json":
        return report.to_dict()

    lines = [f"# UI Human-Load Evidence: {report.scenario}", ""]
    if report.metrics:
        lines.append("## Metrics")
        for key, value in sorted(report.metrics.items()):
            lines.append(f"- {key}: {value}")
        lines.append("")

    if report.phases:
        lines.append("## Phases")
        for phase, demands in report.phases.items():
            lines.append(f"- **{phase}**")
            for demand in demands:
                lines.append(f"  - {demand}")
        lines.append("")

    if report.systems:
        lines.append("## Human Systems")
        lines.append(", ".join(report.systems))
        lines.append("")

    if report.findings:
        lines.append("## Findings")
        for finding in report.findings:
            lines.append(f"- **{finding.family}: {finding.factor}** - {finding.reason}")
            lines.append(f"  Mitigation: {finding.mitigation}")
        lines.append("")

    if report.risk:
        lines.append("## Risk")
        lines.append(
            f"{report.risk.score} "
            f"(probability: {report.risk.probability}; impact: {report.risk.impact}; "
            f"confidence: {report.risk.confidence})"
        )
        lines.append(report.risk.rationale)
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


def _phase_demands(observations: list[dict[str, Any]]) -> dict[str, list[str]]:
    phases: dict[str, list[str]] = {}
    for observation in observations:
        if observation.get("type") != "human_load":
            continue
        phase = str(observation.get("phase") or "unspecified")
        demand = str(observation.get("demand") or "").strip()
        if demand:
            phases.setdefault(phase, []).append(demand)
    return phases


def _systems(observations: list[dict[str, Any]]) -> set[str]:
    systems: set[str] = set()
    for observation in observations:
        if observation.get("type") != "human_load":
            continue
        for system in observation.get("systems", []):
            systems.add(str(system))
    return systems


def _findings(
    raw_report: dict[str, Any],
    metrics: dict[str, int],
    phases: dict[str, list[str]],
    systems: list[str],
) -> list[UiEvidenceFinding]:
    findings: list[UiEvidenceFinding] = []

    context_switches = metrics.get("contextSwitches", 0)
    if context_switches:
        findings.append(
            UiEvidenceFinding(
                family="cognitive_load",
                factor="context switching",
                reason=f"The simulation observed {context_switches} explicit context switch(es).",
                mitigation="Keep the primary task resumable and make cross-surface state correlation visible.",
                probability="high" if context_switches >= 3 else "medium",
                impact="medium",
            )
        )

    if metrics.get("popups", 0):
        findings.append(
            UiEvidenceFinding(
                family="interface_friction",
                factor="mode switching",
                reason="The simulation opened a separate popup/window during task inspection.",
                mitigation="Use popups for deliberate expert inspection; keep normal user closure in the main flow.",
                probability="medium",
                impact="medium",
            )
        )

    if "configuration" in systems or metrics.get("fills", 0) > 1:
        findings.append(
            UiEvidenceFinding(
                family="interface_friction",
                factor="system-use overhead",
                reason="The task included controls or inputs that support the system rather than the business question itself.",
                mitigation="Separate expert configuration from ordinary execution, or preserve safe defaults.",
                probability="medium",
                impact="medium",
            )
        )

    if "feedback" in phases:
        findings.append(
            UiEvidenceFinding(
                family="organisational_change",
                factor="feedback capture burden",
                reason="The user is asked to translate an experience into feedback after completing the main task.",
                mitigation="Offer low-friction structured prompts and attach feedback to the relevant trace automatically.",
                probability="medium",
                impact="medium",
            )
        )

    if raw_report.get("errors"):
        findings.append(
            UiEvidenceFinding(
                family="emotional_agency",
                factor="recoverability and control",
                reason="The simulation encountered errors before completing the scenario.",
                mitigation="Make failure states explicit and provide a clear retry, repair, or escalation path.",
                probability="high",
                impact="high",
            )
        )

    for item in raw_report.get("findings", []):
        findings.append(
            UiEvidenceFinding(
                family="scenario_finding",
                factor=str(item.get("label") or "human-load finding"),
                reason=str(item.get("risk") or item.get("reason") or "Scenario supplied a human-load finding."),
                mitigation=str(item.get("mitigation") or "Review with the process owner."),
                probability=str(item.get("probability") or "medium"),
                impact=str(item.get("impact") or "medium"),
            )
        )

    return findings


def _risk(findings: list[UiEvidenceFinding], metrics: dict[str, int], has_errors: bool) -> UiEvidenceRisk | None:
    if not findings:
        return None
    probability = "high" if has_errors or metrics.get("contextSwitches", 0) >= 3 else "medium"
    impact = "high" if has_errors or any(f.impact == "high" for f in findings) else "medium"
    evidence_basis = "observed UI actions, context switches, and scenario annotations"
    if has_errors:
        evidence_basis += ", including scenario errors"
    return UiEvidenceRisk(
        probability=probability,
        impact=impact,
        confidence="medium",
        score=_score(probability, impact),
        rationale=f"Estimated from {evidence_basis}; validate with real users.",
    )


def _score(probability: str, impact: str) -> str:
    if probability == "high" and impact == "high":
        return "critical"
    if probability == "high" or impact == "high":
        return "significant"
    if probability == "medium" or impact == "medium":
        return "moderate"
    return "watch"


def _suggested_blocks(
    metrics: dict[str, int],
    phases: dict[str, list[str]],
    systems: list[str],
    findings: list[UiEvidenceFinding],
    risk: UiEvidenceRisk | None,
) -> dict[str, str]:
    blocks: dict[str, str] = {}
    if phases:
        blocks["HUMAN_DEMAND"] = "\n".join(
            f"{phase.upper()}: {' '.join(demands)}" for phase, demands in phases.items()
        )
    blocks["HUMAN_LOAD"] = "\n".join(
        [
            f"focus_actions: {metrics.get('clicks', 0) + metrics.get('fills', 0) + metrics.get('waits', 0)}",
            f"trivial_actions: {metrics.get('clicks', 0)}",
            f"context_switches: {metrics.get('contextSwitches', 0)}",
            f"input_burden: {metrics.get('fills', 0)} fill action(s)",
            f"closure_clarity: {'uncertain' if findings else 'observed'}",
            f"human_systems: {', '.join(systems) if systems else 'none declared'}",
        ]
    )
    if findings:
        blocks["HUMAN_FACTORS"] = "\n".join(
            f"{finding.family}: {finding.factor} - {finding.reason}" for finding in findings
        )
    if risk:
        blocks["HUMAN_RISK"] = "\n".join(
            [
                f"probability: {risk.probability}",
                f"impact: {risk.impact}",
                f"confidence: {risk.confidence}",
                f"score: {risk.score}",
                f"rationale: {risk.rationale}",
            ]
        )
    return blocks
