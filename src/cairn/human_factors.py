"""Offline human-factors analysis for Cairn documents.

This module is intentionally dependency-free. It gives Cairn a portable semantic
analysis surface that can run from PyPI without any model service. LLM providers
can later consume the same report as context and add judgement, examples, or
dialogue.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
import re

from cairn.llm_adapters import LLMProvider, LLMRequest, LLMResponse
from cairn.render.parse import normalize_input
from cairn.render.model import ProcessDocument, StepNode


@dataclass
class FactorFinding:
    family: str
    factor: str
    reason: str
    mitigation: str


@dataclass
class HumanRiskEstimate:
    probability: str
    impact: str
    confidence: str
    score: str
    rationale: str


@dataclass
class StepHumanFactorsReport:
    step: str
    text: str
    purpose: str | None = None
    factors: list[FactorFinding] = field(default_factory=list)
    risk: HumanRiskEstimate | None = None
    conversation_starters: list[str] = field(default_factory=list)
    suggested_blocks: dict[str, str] = field(default_factory=dict)


@dataclass
class HumanFactorsReport:
    title: str
    steps: list[StepHumanFactorsReport]
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HumanFactorsInterpretation:
    provider: str
    text: str
    prompt: str
    report: HumanFactorsReport

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "text": self.text,
            "prompt": self.prompt,
            "report": self.report.to_dict(),
        }


_FACTOR_RULES = (
    {
        "family": "cognitive_load",
        "factor": "context switching",
        "tokens": ("context_switches", "navigation_actions", "co-locate", "one pane"),
        "mitigation": "co-locate evidence and reduce navigation before the decision point.",
    },
    {
        "family": "cognitive_load",
        "factor": "uncertainty load",
        "tokens": ("uncertainty_loops", "hidden uncertainty", "source disagreement", "ambiguous", "missing context", "missing evidence", "missing information", "not obviously grounded"),
        "mitigation": "show what is known, unknown, and disputed before asking for judgement.",
    },
    {
        "family": "cognitive_load",
        "factor": "mode switching",
        "tokens": ("mode switch", "second-window", "second window", "dev log", "split attention"),
        "mitigation": "make cross-surface correlation visible and keep the main task resumable.",
    },
    {
        "family": "cognitive_load",
        "factor": "vigilance load",
        "tokens": ("vigilance_load", "waiting for live events", "appears stalled"),
        "mitigation": "make running, stalled, completed, and failed states explicit.",
    },
    {
        "family": "interface_friction",
        "factor": "input burden",
        "tokens": ("input_burden", "free-form", "reason templates", "blank"),
        "mitigation": "provide structured inputs and editable templates for high-value feedback.",
    },
    {
        "family": "interface_friction",
        "factor": "closure ambiguity",
        "tokens": ("closure_clarity", "unclear closure", "final status", "completed or failed", "loop close"),
        "mitigation": "show explicit completion, failure, and next-action state.",
    },
    {
        "family": "interface_friction",
        "factor": "provenance burden",
        "tokens": ("provenance", "source evidence", "used nodes", "process trace", "trace/session", "review_history"),
        "mitigation": "keep source, trace, reviewer, timestamp, and decision context inspectable together.",
    },
    {
        "family": "trust_automation",
        "factor": "automation bias",
        "tokens": ("assisted-by: llm", "ai summary", "ai recommendation", "authoritative", "automation bias", "fluent answers", "fluent generated"),
        "mitigation": "expose evidence, uncertainty, and disagreement separately from the AI suggestion.",
    },
    {
        "family": "trust_automation",
        "factor": "rubber-stamp risk",
        "tokens": ("rubber stamp", "rubber-stamp", "one-click accept", "one-click endorsement", "lowest-effort path"),
        "mitigation": "make reject, defer, and inspect-more-context paths as easy and legitimate as approval.",
    },
    {
        "family": "emotional_agency",
        "factor": "recoverability and control",
        "tokens": ("emotional_agency", "retry path", "repair the interaction", "without losing", "calm recovery"),
        "mitigation": "provide calm recovery paths and visible confirmation that the user's action was received.",
    },
    {
        "family": "social_role",
        "factor": "accountability without control",
        "tokens": ("accountability", "accountable", "audit", "human-owned", "full control"),
        "mitigation": "align accountability with inspectable evidence, authority, and recovery paths.",
    },
    {
        "family": "behavioural_economics",
        "factor": "effort avoidance",
        "tokens": ("trivial_actions", "effort", "easiest", "one-click", "default"),
        "mitigation": "make the right action easier than the risky shortcut.",
    },
    {
        "family": "incentives_game_theory",
        "factor": "queue-pressure incentives",
        "tokens": ("close the queue", "sla", "pressure", "metrics"),
        "mitigation": "measure quality and escalation appropriateness, not only throughput.",
    },
    {
        "family": "organisational_change",
        "factor": "role shift",
        "tokens": ("role_shift", "new_skill", "deskilling", "upskilling", "adoption_support"),
        "mitigation": "name the new skill, train it, and make support visible during rollout.",
    },
    {
        "family": "organisational_change",
        "factor": "feedback suppression",
        "tokens": ("feedback", "feedback prompts", "text box is blank", "high input burden suppresses useful signal"),
        "mitigation": "offer low-friction, structured feedback prompts tied to the trace or decision.",
    },
)


def analyze_human_factors(input_cairn: str | dict[str, Any]) -> HumanFactorsReport:
    """Return an offline human-factors analysis report for a Cairn document."""
    doc = normalize_input(input_cairn)
    reports: list[StepHumanFactorsReport] = []
    for node in _walk(doc.steps):
        report = _analyze_step(node)
        if report.factors or report.risk or _is_human_touch(node):
            reports.append(report)
    return HumanFactorsReport(title=doc.title, steps=reports, warnings=doc.warnings)


def interpret_human_factors(
    input_cairn: str | dict[str, Any],
    provider: LLMProvider,
    *,
    report: HumanFactorsReport | None = None,
) -> HumanFactorsInterpretation:
    """Ask an LLM provider to interpret an offline human-factors report.

    The offline report remains the portable baseline. The provider is asked to
    produce proposed annotations and questions for a human designer to review.
    """
    base_report = report or analyze_human_factors(input_cairn)
    prompt = build_human_factors_prompt(input_cairn, base_report)
    response = provider.complete(
        LLMRequest(
            task="cairn.human_factors.interpret",
            prompt=prompt,
            context={"offline_report": base_report.to_dict(), "input_cairn": input_cairn},
        )
    )
    return HumanFactorsInterpretation(
        provider=response.provider,
        text=response.text,
        prompt=prompt,
        report=base_report,
    )


def build_human_factors_prompt(input_cairn: str | dict[str, Any], report: HumanFactorsReport) -> str:
    source_note = input_cairn if isinstance(input_cairn, str) else "<PLAN dict supplied in context>"
    return (
        "You are interpreting a Cairn human-factors analysis.\n"
        "Use the offline report as a starting point, not as unquestionable truth.\n"
        "Do not make clinical claims. Identify plausible human-system forces, "
        "risk combinations, missing context, and redesign questions.\n\n"
        "If the process step touches a UI, screen, queue, portal, dashboard, "
        "form, or agentic interface, explicitly map the HCI touchpoints. Do not "
        "treat the UI as a cosmetic wrapper. For each relevant UI step, ask how "
        "the human becomes aware of the work, orients to state/risk/evidence, "
        "executes the action, receives feedback, recovers from errors or missing "
        "information, and sees handoff/closure. Assess cognitive aesthetic load: "
        "visual hierarchy, information scent, recognition over recall, state "
        "visibility, affordance clarity, perceptual grouping, error prevention, "
        "recovery, accessibility/focus, confidence cues, and density fit. "
        "Separate observed evidence from inference.\n\n"
        "Return concise Markdown with these sections:\n"
        "1. Highest-risk steps\n"
        "2. Proposed HUMAN_FACTORS / HUMAN_RISK annotations\n"
        "3. HCI touchpoint and cognitive-aesthetic findings\n"
        "4. Questions for the developer or process owner\n"
        "5. Redesign suggestions\n\n"
        "Cairn source:\n"
        f"{source_note}\n\n"
        "Offline report JSON:\n"
        f"{report.to_dict()}\n"
    )


def _walk(nodes: list[StepNode]) -> list[StepNode]:
    out: list[StepNode] = []
    for node in nodes:
        out.append(node)
        out.extend(_walk(node.children))
    return out


def _is_human_touch(node: StepNode) -> bool:
    blob = " ".join(node.tags).upper()
    return "HUMAN" in blob or "ASSISTED-BY" in blob or any(
        key in node.sub_blocks
        for key in ("HUMAN_DEMAND", "HUMAN_LOAD", "HUMAN_FACTORS", "HUMAN_RISK", "TRUST", "CHANGE_IMPACT")
    )


def _analyze_step(node: StepNode) -> StepHumanFactorsReport:
    evidence = _evidence_blob(node)
    findings: list[FactorFinding] = []
    seen: set[tuple[str, str]] = set()
    for rule in _FACTOR_RULES:
        if any(_token_matches(evidence, token) for token in rule["tokens"]):
            key = (rule["family"], rule["factor"])
            if key in seen:
                continue
            seen.add(key)
            findings.append(
                FactorFinding(
                    family=rule["family"],
                    factor=rule["factor"],
                    reason=f"Matched cues in step {node.number}: {', '.join(t for t in rule['tokens'] if _token_matches(evidence, t))}.",
                    mitigation=rule["mitigation"],
                )
            )

    risk = _risk_from_blocks_or_findings(node, findings, evidence)
    suggested = _suggested_blocks(findings, risk)
    return StepHumanFactorsReport(
        step=node.number,
        text=node.text,
        purpose=node.sub_blocks.get("PURPOSE"),
        factors=findings,
        risk=risk,
        conversation_starters=_conversation_starters(findings, risk),
        suggested_blocks=suggested,
    )


def _evidence_blob(node: StepNode) -> str:
    pieces = [node.text, " ".join(node.tags)]
    pieces.extend(f"{key}: {value}" for key, value in node.sub_blocks.items())
    return "\n".join(pieces).lower()


def _token_matches(evidence: str, token: str) -> bool:
    if token in {
        "context_switches",
        "navigation_actions",
        "trivial_actions",
        "input_burden",
        "uncertainty_loops",
        "closure_clarity",
        "vigilance_load",
    }:
        match = re.search(rf"\b{re.escape(token)}\s*:\s*([^\n]+)", evidence)
        if not match:
            return False
        value = match.group(1).strip()
        if token == "closure_clarity":
            if value.startswith("0") or value in {"none", "high", "n/a"}:
                return False
            return True
        if token != "closure_clarity" and (value.startswith("0") or value in {"none", "low", "n/a"}):
            return False
        return True
    return token in evidence


def _risk_from_blocks_or_findings(
    node: StepNode,
    findings: list[FactorFinding],
    evidence: str,
) -> HumanRiskEstimate | None:
    existing = node.sub_blocks.get("HUMAN_RISK")
    if existing:
        parsed = _parse_key_values(existing)
        return HumanRiskEstimate(
            probability=parsed.get("probability", "medium"),
            impact=parsed.get("impact", "medium"),
            confidence=parsed.get("confidence", "medium"),
            score=parsed.get("score", _score(parsed.get("probability", "medium"), parsed.get("impact", "medium"))),
            rationale=parsed.get("rationale", existing.replace("\n", " ")),
        )

    if not findings:
        return None
    probability = "high" if len(findings) >= 4 or "uncertainty_loops" in evidence else "medium"
    impact = "high" if any(token in evidence for token in ("approval", "financial", "audit", "accountability")) else "medium"
    confidence = "medium"
    return HumanRiskEstimate(
        probability=probability,
        impact=impact,
        confidence=confidence,
        score=_score(probability, impact),
        rationale="Estimated from offline human-factor cues; confirm with domain users before treating as authoritative.",
    )


def _parse_key_values(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        out[key.strip().lower()] = value.strip()
    return out


def _score(probability: str, impact: str) -> str:
    if probability == "high" and impact == "high":
        return "critical"
    if probability == "high" or impact == "high":
        return "significant"
    if probability == "medium" or impact == "medium":
        return "moderate"
    return "watch"


def _suggested_blocks(findings: list[FactorFinding], risk: HumanRiskEstimate | None) -> dict[str, str]:
    blocks: dict[str, str] = {}
    if findings:
        lines = [f"{f.family}: {f.factor} - {f.reason}" for f in findings]
        blocks["HUMAN_FACTORS"] = "\n".join(lines)
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
    if findings:
        blocks["IMPROVEMENT"] = "\n".join(f.mitigation for f in findings)
    return blocks


def _conversation_starters(findings: list[FactorFinding], risk: HumanRiskEstimate | None) -> list[str]:
    starters = ["What human-system forces are plausibly present in this step?"]
    if risk and risk.score in {"significant", "critical"}:
        starters.append("Is the human accountable for a decision they can inspect, control, and recover from?")
    if any(f.family == "trust_automation" for f in findings):
        starters.append("Does the process calibrate trust before asking the human to approve or rely on AI output?")
    if any(f.family == "cognitive_load" for f in findings):
        starters.append("Which context switches or memory burdens can be removed before the business decision?")
    return starters


def format_human_factors_report(report: HumanFactorsReport, *, output_format: str = "markdown") -> str | dict[str, Any]:
    """Format a human-factors report as markdown or json-compatible dict."""
    if output_format == "json":
        return report.to_dict()

    lines: list[str] = [f"# Human Factors Analysis: {report.title or 'Cairn document'}", ""]
    for step in report.steps:
        lines.append(f"## {step.step}. {step.text}")
        if step.purpose:
            lines.append(f"**Purpose:** {step.purpose}")
        for finding in step.factors:
            lines.append(f"- **{finding.family}: {finding.factor}** - {finding.reason}")
            lines.append(f"  Mitigation: {finding.mitigation}")
        if step.risk:
            lines.append(
                f"**Risk:** {step.risk.score} "
                f"(probability: {step.risk.probability}; impact: {step.risk.impact}; "
                f"confidence: {step.risk.confidence})"
            )
            lines.append(f"Rationale: {step.risk.rationale}")
        if step.conversation_starters:
            lines.append("**Conversation starters:**")
            for starter in step.conversation_starters:
                lines.append(f"- {starter}")
        lines.append("")
    return "\n".join(lines).strip()
