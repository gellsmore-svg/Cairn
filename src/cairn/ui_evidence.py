"""Human-load analysis for Cairn UI simulation reports."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from cairn.layout_load import analyze_functional_layout
from cairn.llm_adapters import LLMProvider, LLMRequest


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


@dataclass
class UiRoleplayInterpretation:
    provider: str
    text: str
    prompt: str
    evidence: UiHumanLoadReport
    personas: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "text": self.text,
            "prompt": self.prompt,
            "evidence": self.evidence.to_dict(),
            "personas": self.personas,
        }


def analyze_ui_simulation_report(report: dict[str, Any]) -> UiHumanLoadReport:
    """Summarise a `cairn-ui-sim` report as human-load evidence."""
    metrics = {key: int(value) for key, value in dict(report.get("metrics", {})).items()}
    observations = list(report.get("observations", []))
    phases = _phase_demands(observations)
    systems = sorted(_systems(observations))
    layout_reports = list(_layout_reports(report))
    findings = _findings(report, metrics, phases, systems, layout_reports)
    risk = _risk(findings, metrics, bool(report.get("errors")))
    return UiHumanLoadReport(
        scenario=str(report.get("scenario") or "UI simulation"),
        metrics=metrics,
        phases=phases,
        systems=systems,
        findings=findings,
        risk=risk,
        suggested_blocks=_suggested_blocks(metrics, phases, systems, findings, risk, layout_reports),
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


def format_cairn_annotation_snippet(
    report: UiHumanLoadReport,
    *,
    step_title: str | None = None,
    include_header: bool = True,
) -> str:
    """Return a Cairn annotation snippet from UI human-load evidence."""
    title = step_title or f"Review UI evidence for {report.scenario}"
    lines: list[str] = []
    if include_header:
        lines.extend(
            [
                f"## {title}",
                "",
                "PURPOSE:",
                f"  Record human-load evidence observed during UI simulation `{report.scenario}`.",
                "",
                "EVIDENCE:",
                f"  ui_simulation: {report.scenario}",
                f"  clicks: {report.metrics.get('clicks', 0)}",
                f"  fills: {report.metrics.get('fills', 0)}",
                f"  waits: {report.metrics.get('waits', 0)}",
                f"  context_switches: {report.metrics.get('contextSwitches', 0)}",
                f"  popups: {report.metrics.get('popups', 0)}",
                "",
            ]
        )

    for block in ("HUMAN_DEMAND", "HUMAN_LOAD", "HUMAN_FACTORS", "HUMAN_RISK"):
        value = report.suggested_blocks.get(block)
        if not value:
            continue
        lines.append(f"{block}:")
        lines.extend(f"  {line}" if line else "" for line in value.splitlines())
        lines.append("")

    lines.extend(
        [
            "REVIEW:",
            "  Treat this as design evidence, not measurement of a person.",
            "  Confirm the annotations with the process owner and representative users before adopting.",
        ]
    )
    return "\n".join(lines).rstrip()


def build_ui_roleplay_prompt(
    raw_report: dict[str, Any],
    evidence: UiHumanLoadReport,
    *,
    personas: list[str] | None = None,
    cairn_source: str | None = None,
) -> str:
    """Build an LLM prompt for simulated human-experience review of a UI run."""
    selected_personas = personas or _default_personas()
    persona_lines = "\n".join(f"- {persona}" for persona in selected_personas)
    source = cairn_source or "<no Cairn source supplied>"
    return (
        "You are simulating plausible human experience from UI evidence.\n"
        "This is not a real user study, clinical assessment, or performance score. "
        "Treat the browser report as grounded evidence and your role-play as hypothesis generation.\n\n"
        "Review the interface from these perspectives:\n"
        f"{persona_lines}\n\n"
        "For each perspective, reason about:\n"
        "- awareness: how the person notices what needs doing;\n"
        "- execution: what they must decide, remember, compare, type, or configure;\n"
        "- notification/closure: how they know the work is complete;\n"
        "- recovery: what happens if information is missing, wrong, delayed, or socially risky;\n"
        "- organisational pressure: incentives, queue pressure, audit, accountability, and trust.\n\n"
        "Return concise Markdown with these sections:\n"
        "1. Role-play snapshots\n"
        "2. Likely load amplifiers\n"
        "3. Failure or recursion loops\n"
        "4. Suggested Cairn annotations\n"
        "5. Questions for the developer or process owner\n\n"
        "Do not diagnose people. Do not claim statistical certainty. Distinguish observed evidence from inference.\n\n"
        "Optional Cairn source:\n"
        f"{source}\n\n"
        "Deterministic UI evidence JSON:\n"
        f"{evidence.to_dict()}\n\n"
        "Raw UI simulation report JSON:\n"
        f"{raw_report}\n"
    )


def interpret_ui_experience(
    raw_report: dict[str, Any],
    provider: LLMProvider,
    *,
    evidence: UiHumanLoadReport | None = None,
    personas: list[str] | None = None,
    cairn_source: str | None = None,
) -> UiRoleplayInterpretation:
    """Ask an LLM to role-play plausible user experience from UI evidence."""
    base_evidence = evidence or analyze_ui_simulation_report(raw_report)
    selected_personas = personas or _default_personas()
    prompt = build_ui_roleplay_prompt(
        raw_report,
        base_evidence,
        personas=selected_personas,
        cairn_source=cairn_source,
    )
    response = provider.complete(
        LLMRequest(
            task="cairn.ui_experience.roleplay",
            prompt=prompt,
            context={
                "ui_report": raw_report,
                "ui_evidence": base_evidence.to_dict(),
                "personas": selected_personas,
                "cairn_source": cairn_source,
            },
        )
    )
    return UiRoleplayInterpretation(
        provider=response.provider,
        text=response.text,
        prompt=prompt,
        evidence=base_evidence,
        personas=selected_personas,
    )


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


def _default_personas() -> list[str]:
    return [
        "novice user who wants to complete the task without understanding system internals",
        "experienced operator under queue pressure",
        "developer or analyst inspecting trust, trace, and failure behaviour",
    ]


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
    layout_reports: list[Any] | None = None,
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

    if "uncertainty management" in systems:
        findings.append(
            UiEvidenceFinding(
                family="cognitive_load",
                factor="uncertainty load",
                reason="The scenario declares uncertainty management as part of the user's task.",
                mitigation="Surface missing context, assumptions, and confidence before asking the user to trust or act on the answer.",
                probability="medium",
                impact="high",
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

    for layout_report in layout_reports or []:
        if layout_report.metrics.get("layout_load") in {"medium", "high"}:
            findings.append(
                UiEvidenceFinding(
                    family="functional_layout_load",
                    factor=f"{layout_report.metrics['layout_load']} layout traversal load",
                    reason=(
                        "Layout geometry suggests avoidable scan or pointer effort: "
                        f"avg related distance {layout_report.metrics['avg_related_distance_px']}px; "
                        f"pointer travel {layout_report.metrics['cumulative_pointer_travel_viewports']} viewport(s)."
                    ),
                    mitigation="Group related fields, evidence, warnings, and actions into one decision region where possible.",
                    probability="medium",
                    impact="medium" if layout_report.metrics["layout_load"] == "medium" else "high",
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


def _layout_reports(raw_report: dict[str, Any]):
    for snapshot in raw_report.get("layoutLoad", []):
        if isinstance(snapshot, dict):
            yield analyze_functional_layout(snapshot)


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
    layout_reports: list[Any] | None = None,
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
    if layout_reports:
        lines: list[str] = []
        for index, layout_report in enumerate(layout_reports, start=1):
            lines.append(f"snapshot_{index}:")
            lines.extend(f"  {key}: {value}" for key, value in layout_report.metrics.items())
        blocks["FUNCTIONAL_LAYOUT_LOAD"] = "\n".join(lines)
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
