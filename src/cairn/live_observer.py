"""Live observation evidence for product and agentic-system monitoring."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterable
from collections import Counter, defaultdict


@dataclass
class LiveObservationFinding:
    family: str
    factor: str
    reason: str
    mitigation: str
    probability: str = "medium"
    impact: str = "medium"


@dataclass
class LiveObservationRisk:
    probability: str
    impact: str
    confidence: str
    score: str
    rationale: str


@dataclass
class LiveObservationReport:
    title: str
    event_count: int
    sources: dict[str, int]
    kinds: dict[str, int]
    findings: list[LiveObservationFinding] = field(default_factory=list)
    risk: LiveObservationRisk | None = None
    suggested_blocks: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def analyze_live_observations(
    observations: Iterable[dict[str, Any]],
    *,
    title: str = "Live product observation",
) -> LiveObservationReport:
    """Summarise live product observations as Cairn-style evidence."""
    events = [dict(event) for event in observations]
    source_counts = Counter(str(event.get("source") or "unknown") for event in events)
    kind_counts = Counter(str(event.get("kind") or "unknown") for event in events)
    findings = _findings(events, source_counts, kind_counts)
    risk = _risk(findings, events)
    return LiveObservationReport(
        title=title,
        event_count=len(events),
        sources=dict(sorted(source_counts.items())),
        kinds=dict(sorted(kind_counts.items())),
        findings=findings,
        risk=risk,
        suggested_blocks=_suggested_blocks(events, findings, risk),
    )


def format_live_observation_report(report: LiveObservationReport, *, output_format: str = "markdown") -> str | dict[str, Any]:
    """Format live observation evidence as Markdown or JSON-compatible data."""
    if output_format == "json":
        return report.to_dict()

    lines = [f"# Live Observation Evidence: {report.title}", ""]
    lines.append(f"Events: {report.event_count}")
    if report.sources:
        lines.append("")
        lines.append("## Sources")
        for source, count in report.sources.items():
            lines.append(f"- {source}: {count}")
    if report.kinds:
        lines.append("")
        lines.append("## Kinds")
        for kind, count in report.kinds.items():
            lines.append(f"- {kind}: {count}")
    if report.findings:
        lines.append("")
        lines.append("## Findings")
        for finding in report.findings:
            lines.append(f"- **{finding.family}: {finding.factor}** - {finding.reason}")
            lines.append(f"  Mitigation: {finding.mitigation}")
    if report.risk:
        lines.append("")
        lines.append("## Risk")
        lines.append(
            f"{report.risk.score} "
            f"(probability: {report.risk.probability}; impact: {report.risk.impact}; "
            f"confidence: {report.risk.confidence})"
        )
        lines.append(report.risk.rationale)
    if report.suggested_blocks:
        lines.append("")
        lines.append("## Suggested Cairn Blocks")
        for name, value in report.suggested_blocks.items():
            lines.append(f"### {name}")
            lines.append("```cairn")
            lines.append(value)
            lines.append("```")
            lines.append("")
    return "\n".join(lines).strip()


def _findings(
    events: list[dict[str, Any]],
    source_counts: Counter[str],
    kind_counts: Counter[str],
) -> list[LiveObservationFinding]:
    findings: list[LiveObservationFinding] = []

    error_events = [event for event in events if _severity(event) in {"error", "critical"} or _has_tag(event, "error")]
    if error_events:
        findings.append(
            LiveObservationFinding(
                family="system_reliability",
                factor="runtime errors",
                reason=f"Observed {len(error_events)} error or critical event(s) during live monitoring.",
                mitigation="Correlate errors with user-visible state, agent steps, and recovery paths before treating the task as complete.",
                probability="high" if len(error_events) >= 3 else "medium",
                impact="high" if any(_severity(event) == "critical" for event in error_events) else "medium",
            )
        )

    slow_events = [event for event in events if _duration_ms(event) >= 3000]
    if slow_events:
        findings.append(
            LiveObservationFinding(
                family="human_load",
                factor="vigilance and waiting load",
                reason=f"Observed {len(slow_events)} event(s) at or above 3000 ms.",
                mitigation="Make waiting, stalled, retrying, and completed states explicit to reduce vigilance load.",
                probability="medium",
                impact="medium",
            )
        )

    queue_waiting_events = [
        event for event in events if event.get("kind") == "queue_event" and _has_tag(event, "waiting")
    ]
    if len(queue_waiting_events) >= 3:
        findings.append(
            LiveObservationFinding(
                family="human_load",
                factor="queue vigilance load",
                reason=f"Observed {len(queue_waiting_events)} queue event(s) that keep work in a waiting or in-progress state.",
                mitigation="Expose queue position, expected completion, stalled state, and completion handoff so users do not have to monitor the process manually.",
                probability="medium",
                impact="medium",
            )
        )

    if any(_has_tag(event, "context_switch") for event in events):
        findings.append(
            LiveObservationFinding(
                family="human_load",
                factor="context switching",
                reason="Live observations include context-switch tags across UI, logs, or process inspection.",
                mitigation="Keep trace, output, and recovery state correlated so users do not have to manually reconstruct the story.",
                probability="medium",
                impact="medium",
            )
        )

    if any(
        _has_tag(event, "unsupported_output")
        or _has_tag(event, "overconfident_output")
        or (_has_tag(event, "missing_evidence") and event.get("kind") == "agent_output")
        for event in events
    ):
        findings.append(
            LiveObservationFinding(
                family="agent_effectiveness",
                factor="unsupported or overconfident output",
                reason="Agent output was marked as unsupported, overconfident, or insufficiently grounded.",
                mitigation="Separate answer fluency from evidence sufficiency; require source, uncertainty, and authority checks before closure.",
                probability="medium",
                impact="high",
            )
        )

    human_systems = _human_system_counts(events)
    if "accountability" in human_systems or "uncertainty management" in human_systems:
        findings.append(
            LiveObservationFinding(
                family="human_systems",
                factor="accountability or uncertainty load",
                reason="Live observations involve accountability or uncertainty-management demands.",
                mitigation="Make authority, missing context, assumptions, and recovery options visible at the point of action.",
                probability="medium",
                impact="high",
            )
        )

    repeated_sources = [source for source, count in source_counts.items() if source != "unknown" and count >= 3]
    if repeated_sources:
        findings.append(
            LiveObservationFinding(
                family="operational_learning",
                factor="repeated observation cluster",
                reason=f"Repeated observations from: {', '.join(repeated_sources)}.",
                mitigation="Treat repeated clusters as candidates for durable product changes, not one-off incidents.",
                probability="medium",
                impact="medium",
            )
        )

    if kind_counts.get("agent_step", 0) and not kind_counts.get("agent_output_review", 0):
        findings.append(
            LiveObservationFinding(
                family="agent_effectiveness",
                factor="missing output review",
                reason="Agent steps were observed without any corresponding output-review event.",
                mitigation="Add lightweight review events that record grounding, uncertainty, usefulness, and closure quality.",
                probability="medium",
                impact="medium",
            )
        )

    return findings


def _risk(findings: list[LiveObservationFinding], events: list[dict[str, Any]]) -> LiveObservationRisk | None:
    if not findings:
        return None
    probability = "high" if len(findings) >= 4 or any(f.probability == "high" for f in findings) else "medium"
    impact = "high" if any(f.impact == "high" for f in findings) else "medium"
    if any(_severity(event) == "critical" for event in events):
        probability = "high"
        impact = "high"
    return LiveObservationRisk(
        probability=probability,
        impact=impact,
        confidence="medium",
        score=_score(probability, impact),
        rationale="Estimated from live observation counts, severities, tags, durations, and human-system cues; validate with operators and logs.",
    )


def _suggested_blocks(
    events: list[dict[str, Any]],
    findings: list[LiveObservationFinding],
    risk: LiveObservationRisk | None,
) -> dict[str, str]:
    blocks: dict[str, str] = {}
    blocks["OBSERVATION"] = "\n".join(
        [
            f"event_count: {len(events)}",
            f"sources: {', '.join(sorted({str(event.get('source') or 'unknown') for event in events}))}",
            f"kinds: {', '.join(sorted({str(event.get('kind') or 'unknown') for event in events}))}",
        ]
    )
    human_systems = _human_system_counts(events)
    if human_systems:
        blocks["HUMAN_LOAD"] = "\n".join(
            [
                f"human_systems: {', '.join(sorted(human_systems))}",
                f"uncertainty_loops: {'present' if 'uncertainty management' in human_systems else 'not_observed'}",
                f"accountability_load: {'present' if 'accountability' in human_systems else 'not_observed'}",
            ]
        )
    if findings:
        blocks["HUMAN_FACTORS"] = "\n".join(
            f"{finding.family}: {finding.factor} - {finding.reason}" for finding in findings
        )
        blocks["IMPROVEMENT"] = "\n".join(finding.mitigation for finding in findings)
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


def _human_system_counts(events: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for event in events:
        for system in event.get("human_systems", []):
            counts[str(system)] += 1
    return dict(counts)


def _has_tag(event: dict[str, Any], tag: str) -> bool:
    return tag in {str(item) for item in event.get("tags", [])}


def _severity(event: dict[str, Any]) -> str:
    return str(event.get("severity") or "info").lower()


def _duration_ms(event: dict[str, Any]) -> int:
    try:
        return int(event.get("duration_ms") or 0)
    except (TypeError, ValueError):
        return 0


def _score(probability: str, impact: str) -> str:
    if probability == "high" and impact == "high":
        return "critical"
    if probability == "high" or impact == "high":
        return "significant"
    if probability == "medium" or impact == "medium":
        return "moderate"
    return "watch"
