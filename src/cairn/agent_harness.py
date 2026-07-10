"""Tool-assisted agent harness planning for Cairn.

The planner does not execute commands. It turns the evidence available to an
interactive agent into a repeatable Cairn CLI/Python sequence.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
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
    inputs: dict[str, Any] = field(default_factory=dict)
    missing_inputs: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    agent_prompts: list[str] = field(default_factory=list)
    review_checks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_agent_harness_plan(
    *,
    process_path: str | None = None,
    ui_evidence_path: str | None = None,
    layout_path: str | None = None,
    repository_path: str | None = None,
    screenshot_paths: list[str] | None = None,
    output_dir: str = "cairn-agent-output",
    title: str = "Tool-assisted Cairn agent analysis",
    check_paths: bool = False,
) -> AgentHarnessPlan:
    """Return a deterministic command plan for an interactive agent harness."""
    inputs = _inputs(
        process_path=process_path,
        ui_evidence_path=ui_evidence_path,
        layout_path=layout_path,
        repository_path=repository_path,
        screenshot_paths=screenshot_paths or [],
    )
    missing_inputs = _missing_inputs(inputs) if check_paths else []
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
    for missing in missing_inputs:
        open_questions.append(f"Supplied input was not found: {missing}")

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

    if repository_path:
        steps.append(
            AgentHarnessStep(
                name="Inspect repository surfaces",
                purpose="Identify process files, UI code, agent entry points, tests, and logging surfaces relevant to the human-facing workflow.",
                command=None,
                produces=["repository evidence inventory", "candidate human-facing surfaces"],
            )
        )

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

    if screenshot_paths:
        steps.append(
            AgentHarnessStep(
                name="Review screenshots",
                purpose="Use screenshots as visual evidence for HCI touchpoints, layout grouping, affordance clarity, and cognitive aesthetic load.",
                command=None,
                produces=["screenshot observations", "candidate UI questions"],
            )
        )

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
            purpose="Review generated artifacts against the plan checklist before producing a plain-language synthesis.",
            command=None,
            produces=["plain-language synthesis", "open questions"],
        )
    )
    agent_prompts = _agent_prompts(
        has_process=bool(process_path),
        has_ui_evidence=bool(ui_evidence_path),
        has_layout=bool(layout_path),
        has_repository=bool(repository_path),
        has_screenshots=bool(screenshot_paths),
    )
    review_checks = _review_checks(
        has_process=bool(process_path),
        has_ui_evidence=bool(ui_evidence_path),
        has_layout=bool(layout_path),
        has_repository=bool(repository_path),
        has_screenshots=bool(screenshot_paths),
    )
    return AgentHarnessPlan(
        title=title,
        output_dir=output_dir,
        context_sources=context_sources,
        steps=steps,
        inputs=inputs,
        missing_inputs=missing_inputs,
        open_questions=open_questions,
        agent_prompts=agent_prompts,
        review_checks=review_checks,
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
    if plan.inputs:
        lines.append("## Inputs")
        for key, value in plan.inputs.items():
            if isinstance(value, list):
                rendered = ", ".join(f"`{item}`" for item in value) if value else "`[]`"
            else:
                rendered = f"`{value}`"
            lines.append(f"- {key}: {rendered}")
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
    if plan.agent_prompts:
        lines.append("")
        lines.append("## Consuming Agent Prompts")
        for prompt in plan.agent_prompts:
            lines.append(f"- {prompt}")
    if plan.review_checks:
        lines.append("")
        lines.append("## Agent Review Checklist")
        for check in plan.review_checks:
            lines.append(f"- {check}")
    if plan.missing_inputs:
        lines.append("")
        lines.append("## Missing Inputs")
        for missing in plan.missing_inputs:
            lines.append(f"- `{missing}`")
    return "\n".join(lines).strip()


def _format_shell(plan: AgentHarnessPlan) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        f"# {plan.title}",
        f"# Output directory: {plan.output_dir}",
        "",
    ]
    local_inputs = _local_input_paths(plan.inputs)
    if local_inputs:
        lines.extend(
            [
                "require_path() {",
                "  if [ ! -e \"$1\" ]; then",
                "    echo \"Missing required input: $1\" >&2",
                "    exit 2",
                "  fi",
                "}",
                "",
                "# Preflight supplied local inputs:",
            ]
        )
        for path in local_inputs:
            lines.append(f"require_path {_q(path)}")
        lines.append("")
    lines.append("# Context sources to load before interpretation:")
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
        lines.append("")
    if plan.agent_prompts:
        lines.append("# Consuming agent prompts:")
        for prompt in plan.agent_prompts:
            lines.append(f"# - {prompt}")
        lines.append("")
    if plan.review_checks:
        lines.append("# Agent review checklist:")
        for check in plan.review_checks:
            lines.append(f"# - {check}")
    return "\n".join(lines).rstrip() + "\n"


def _agent_prompts(
    *,
    has_process: bool,
    has_ui_evidence: bool,
    has_layout: bool,
    has_repository: bool,
    has_screenshots: bool,
) -> list[str]:
    prompts = [
        "Use Cairn's Python/CLI tools for repeatable evidence before free-form interpretation; do not replace deterministic outputs with general UX advice.",
        "For every human-facing process step, ask: what makes the user aware, how do they orient, what do they execute, how do they receive feedback or notification, and how do they recover or hand off?",
        "For every UI-mediated step, separate the business task from interface overhead: extra focus actions, cross-screen comparison, search, copying, re-keying, confirmation, and avoidable context switching.",
        "Evaluate cognitive aesthetic explicitly: whether visual hierarchy, grouping, labels, affordances, status, warnings, and evidence make the right judgement easy at the point of need.",
        "When scoring risk, state probability, impact, confidence, and evidence source separately so plausible human-system risks are not presented as measured facts.",
    ]
    if has_process:
        prompts.append("Anchor each human-risk or HCI finding to a concrete Cairn process step or requirement, then propose a Cairn annotation or support clause.")
    else:
        prompts.append("If no Cairn process file is supplied, draft candidate process steps first and mark them as inferred before assessing human load.")
    if has_ui_evidence:
        prompts.append("Use UI simulation evidence as the primary source for HCI touchpoints, non-happy-path states, feedback timing, and interaction recursion.")
    elif has_screenshots:
        prompts.append("Use screenshots for qualitative HCI and cognitive-aesthetic findings, but mark geometry, sequence, and interaction-cost claims as estimates.")
    else:
        prompts.append("If no UI evidence or screenshots exist, actively ask whether a UI is involved; do not let human-risk analysis stop at backend process behaviour.")
    if has_layout:
        prompts.append("Use functional layout metrics for related-field distance, evidence-to-action distance, scan path, pointer travel, and recovery distance before recommending form changes.")
    else:
        prompts.append("If layout geometry is unavailable, recommend layout JSON or Playwright extraction when field distance, eye movement, or pointer travel would affect the decision.")
    if has_repository:
        prompts.append("Inspect repository UI, logs, queue, and agent surfaces for hidden handoffs, ambiguous accountability, and places where the system silently transfers cognitive work to the user.")
    return prompts


def _review_checks(
    *,
    has_process: bool,
    has_ui_evidence: bool,
    has_layout: bool,
    has_repository: bool,
    has_screenshots: bool,
) -> list[str]:
    checks = [
        "Separate observed evidence from inference and mark confidence plainly.",
        "Identify human risks as process conditions, not traits of individual users.",
        "Check whether awareness, orientation, execution, feedback, notification, recovery, handoff, and adaptation touchpoints were considered for every UI-mediated step.",
        "Distinguish business work from interface overhead, including trivial focus actions, context switches, and avoidable explicit decisions.",
        "Confirm that AI recommendations include evidence, uncertainty, challenge, reject, defer, and override paths where the process depends on trust calibration.",
    ]
    if has_process:
        checks.append("Verify that suggested annotations map back to concrete Cairn process steps.")
    if has_ui_evidence:
        checks.append("Use UI simulation evidence to ground HCI phase findings, and flag any skipped non-happy-path states.")
    else:
        checks.append("Treat UI claims as inferential unless screenshots, traces, layout JSON, or repository UI code were inspected.")
    if has_layout:
        checks.append("Review functional layout load for related-field distance, evidence-to-action distance, scan path, pointer travel, and recovery distance.")
    elif has_screenshots:
        checks.append("Estimate layout load qualitatively from screenshots and recommend layout JSON if geometry is decision-relevant.")
    if has_repository:
        checks.append("Inspect repository UI, logging, queue, and agent surfaces for hidden human handoffs or accountability gaps.")
    return checks


def _inputs(
    *,
    process_path: str | None,
    ui_evidence_path: str | None,
    layout_path: str | None,
    repository_path: str | None,
    screenshot_paths: list[str],
) -> dict[str, Any]:
    inputs: dict[str, Any] = {}
    if process_path:
        inputs["process"] = process_path
    if ui_evidence_path:
        inputs["ui_evidence"] = ui_evidence_path
    if layout_path:
        inputs["layout"] = layout_path
    if repository_path:
        inputs["repository"] = repository_path
    if screenshot_paths:
        inputs["screenshots"] = list(screenshot_paths)
    return inputs


def _missing_inputs(inputs: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for path in _local_input_paths(inputs):
        if not Path(path).exists():
            missing.append(path)
    return missing


def _local_input_paths(inputs: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for value in inputs.values():
        values = value if isinstance(value, list) else [value]
        for item in values:
            text = str(item)
            if _is_remote(text):
                continue
            paths.append(text)
    return paths


def _is_remote(value: str) -> bool:
    return value.startswith(("http://", "https://", "git@", "ssh://"))


def _q(value: str) -> str:
    return shlex.quote(str(value))


__all__ = [
    "AgentHarnessPlan",
    "AgentHarnessStep",
    "build_agent_harness_plan",
    "format_agent_harness_plan",
]
