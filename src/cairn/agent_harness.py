"""Tool-assisted agent harness planning for Cairn.

The planner does not execute commands. It turns the evidence available to an
interactive agent into a repeatable Cairn CLI/Python sequence.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import shlex
from typing import Any


@dataclass(frozen=True)
class AgentHarnessStep:
    name: str
    purpose: str
    command: str | None = None
    produces: list[str] = field(default_factory=list)
    required: bool = True


@dataclass(frozen=True)
class AgentHarnessPlan:
    title: str
    output_dir: str
    context_sources: list[str]
    steps: list[AgentHarnessStep]
    open_questions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_agent_harness_plan(
    *,
    process_path: str | None = None,
    ui_evidence_path: str | None = None,
    layout_path: str | None = None,
    output_dir: str = "cairn-agent-output",
    title: str = "Tool-assisted Cairn agent analysis",
) -> AgentHarnessPlan:
    """Return a deterministic command plan for an interactive agent harness."""
    context_sources = [
        "SPEC.md",
        "docs/usage-modes.md",
        "docs/orchestration/manual-agent-analysis.cairn.md",
        "docs/orchestration/agent-harness-playbook.md",
        "okf/concepts/index.md",
        "docs/HCI-TOUCHPOINTS.md",
        "docs/FUNCTIONAL-LAYOUT-LOAD.md",
    ]
    steps: list[AgentHarnessStep] = [
        AgentHarnessStep(
            name="Read target evidence",
            purpose="Record the repository, process, UI evidence, screenshots, or layout artifacts actually inspected.",
            command=None,
            produces=["evidence inventory"],
        ),
        AgentHarnessStep(
            name="Load Cairn semantic context",
            purpose="Ground the analysis in Cairn's specification, orchestration pattern, and OKF lenses.",
            command=None,
            produces=["active Cairn/OKF lenses"],
        ),
        AgentHarnessStep(
            name="Create output directory",
            purpose="Ensure subsequent deterministic Cairn tools can write their artifacts.",
            command=f"mkdir -p {_q(output_dir)}",
            produces=[output_dir],
        ),
    ]
    open_questions: list[str] = []

    if process_path:
        process_q = _q(process_path)
        steps.extend(
            [
                AgentHarnessStep(
                    name="Validate process structure",
                    purpose="Check the Cairn process skeleton before interpreting human or UI implications.",
                    command=f"cairn-validate {process_q}",
                    produces=["validation result"],
                ),
                AgentHarnessStep(
                    name="Analyze human factors",
                    purpose="Generate deterministic cognitive, psychological, social, organisational, and incentive-factor evidence.",
                    command=(
                        f"cairn-human-factors {process_q} --format json "
                        f"--output {_q(output_dir + '/human-factors.json')}"
                    ),
                    produces=[output_dir + "/human-factors.json"],
                ),
            ]
        )
    else:
        open_questions.append("No Cairn process file was supplied; process validation and deterministic human-factors analysis are unavailable.")

    if ui_evidence_path:
        ui_q = _q(ui_evidence_path)
        steps.extend(
            [
                AgentHarnessStep(
                    name="Summarise UI evidence",
                    purpose="Convert UI simulation evidence into HCI phases, human-load findings, risk, and suggested Cairn blocks.",
                    command=(
                        f"cairn-ui-evidence {ui_q} --format json "
                        f"--output {_q(output_dir + '/ui-evidence.json')}"
                    ),
                    produces=[output_dir + "/ui-evidence.json"],
                ),
                AgentHarnessStep(
                    name="Generate interface recommendations",
                    purpose="Produce concrete interface changes with mandatory OKF concept traceability.",
                    command=(
                        f"cairn-recommend-interface-changes {ui_q} "
                        f"--output {_q(output_dir + '/interface-recommendations.md')} "
                        f"--future-svg-output {_q(output_dir + '/future-state.svg')}"
                    ),
                    produces=[
                        output_dir + "/interface-recommendations.md",
                        output_dir + "/future-state.svg",
                    ],
                ),
            ]
        )
    else:
        open_questions.append("No UI simulation evidence was supplied; HCI touchpoint and interface recommendations may remain inferential.")

    if layout_path:
        layout_q = _q(layout_path)
        steps.append(
            AgentHarnessStep(
                name="Analyze functional layout load",
                purpose="Measure form/layout traversal load from rectangles, relationships, and task sequence.",
                command=(
                    f"cairn-layout-load {layout_q} --format json "
                    f"--output {_q(output_dir + '/layout-load.json')} "
                    f"--svg-output {_q(output_dir + '/layout-overlay.svg')}"
                ),
                produces=[output_dir + "/layout-load.json", output_dir + "/layout-overlay.svg"],
            )
        )

    if process_path or ui_evidence_path:
        args = ["cairn-generate-report", "--title", title, "--format", "markdown", "--output", output_dir + "/cairn-analysis-report.md"]
        if process_path:
            args.extend(["--input", process_path])
        if ui_evidence_path:
            args.extend(["--interface-evidence", ui_evidence_path])
        steps.append(
            AgentHarnessStep(
                name="Generate review report",
                purpose="Assemble a human-reviewable report from available process and UI evidence.",
                command=" ".join(_q(item) for item in args),
                produces=[output_dir + "/cairn-analysis-report.md"],
            )
        )

    steps.append(
        AgentHarnessStep(
            name="Agent review and explanation",
            purpose="Review generated artifacts for missing evidence, unsupported certainty, uncited recommendations, and skipped UI touchpoints.",
            command=None,
            produces=["plain-language synthesis", "open questions"],
        )
    )
    return AgentHarnessPlan(
        title=title,
        output_dir=output_dir,
        context_sources=context_sources,
        steps=steps,
        open_questions=open_questions,
    )


def format_agent_harness_plan(plan: AgentHarnessPlan, *, output_format: str = "markdown") -> str | dict[str, Any]:
    """Format an agent harness plan as Markdown, shell script, or JSON-compatible data."""
    if output_format == "json":
        return plan.to_dict()
    if output_format == "shell":
        return _format_shell(plan)

    lines = [f"# {plan.title}", ""]
    lines.append(f"Output directory: `{plan.output_dir}`")
    lines.append("")
    lines.append("## Context Sources")
    for source in plan.context_sources:
        lines.append(f"- `{source}`")
    lines.append("")
    lines.append("## Deterministic Sequence")
    for index, step in enumerate(plan.steps, start=1):
        lines.append(f"### {index}. {step.name}")
        lines.append(step.purpose)
        if step.command:
            lines.append("")
            lines.append("```bash")
            lines.append(step.command)
            lines.append("```")
        if step.produces:
            lines.append("")
            lines.append("Produces: " + ", ".join(f"`{item}`" for item in step.produces))
        lines.append("")
    if plan.open_questions:
        lines.append("## Open Questions")
        for question in plan.open_questions:
            lines.append(f"- {question}")
    return "\n".join(lines).strip()


def _format_shell(plan: AgentHarnessPlan) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        f"# {plan.title}",
        f"# Output directory: {plan.output_dir}",
        "",
        "# Context sources to load before interpretation:",
    ]
    for source in plan.context_sources:
        lines.append(f"# - {source}")
    lines.append("")

    for index, step in enumerate(plan.steps, start=1):
        lines.append(f"# {index}. {step.name}")
        lines.append(f"# {step.purpose}")
        if step.command:
            lines.append(step.command)
        else:
            lines.append(f"# Manual/agent step; produces: {', '.join(step.produces) if step.produces else 'review output'}")
        lines.append("")

    if plan.open_questions:
        lines.append("# Open questions:")
        for question in plan.open_questions:
            lines.append(f"# - {question}")
    return "\n".join(lines).rstrip() + "\n"


def _q(value: str) -> str:
    return shlex.quote(str(value))


__all__ = [
    "AgentHarnessPlan",
    "AgentHarnessStep",
    "build_agent_harness_plan",
    "format_agent_harness_plan",
]
