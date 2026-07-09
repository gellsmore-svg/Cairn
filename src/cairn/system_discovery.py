"""Discover observation surfaces in a repo or local stack."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DiscoveredSurface:
    name: str
    kind: str
    path: str
    evidence: list[str] = field(default_factory=list)
    observer_actions: list[str] = field(default_factory=list)


@dataclass
class SystemDiscoveryReport:
    root: str
    surfaces: list[DiscoveredSurface]
    observation_plan: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def discover_system(root: str | Path) -> SystemDiscoveryReport:
    """Inspect a repository or stack root and propose observation surfaces."""
    base = Path(root).resolve()
    surfaces: list[DiscoveredSurface] = []
    candidates = [base] + [path for path in sorted(base.iterdir()) if path.is_dir() and not path.name.startswith(".")]
    for path in candidates:
        surfaces.extend(_discover_at(path))
    return SystemDiscoveryReport(
        root=str(base),
        surfaces=surfaces,
        observation_plan=_observation_plan(surfaces),
    )


def format_system_discovery_report(report: SystemDiscoveryReport, *, output_format: str = "markdown") -> str | dict[str, Any]:
    """Format a system discovery report."""
    if output_format == "json":
        return report.to_dict()

    lines = [f"# System Observation Discovery: {report.root}", ""]
    if report.surfaces:
        lines.append("## Surfaces")
        for surface in report.surfaces:
            lines.append(f"- **{surface.name}** ({surface.kind}) - `{surface.path}`")
            for item in surface.evidence:
                lines.append(f"  - evidence: {item}")
            for action in surface.observer_actions:
                lines.append(f"  - observe: {action}")
        lines.append("")
    if report.observation_plan:
        lines.append("## Proposed Observation Plan")
        for index, item in enumerate(report.observation_plan, start=1):
            lines.append(f"{index}. {item}")
    return "\n".join(lines).strip()


def _discover_at(path: Path) -> list[DiscoveredSurface]:
    surfaces: list[DiscoveredSurface] = []
    name = path.name
    files = {child.name for child in path.iterdir() if child.is_file()}
    dirs = {child.name for child in path.iterdir() if child.is_dir()}

    if {"versions.lock", "compose.yaml"} & files or (path / "health" / "healthcheck.sh").exists():
        surfaces.append(
            DiscoveredSurface(
                name=name,
                kind="runtime_host",
                path=str(path),
                evidence=[item for item in ("versions.lock", "compose.yaml", "health/healthcheck.sh") if (path / item).exists()],
                observer_actions=[
                    "Run health checks and convert failures/latency into live observation events.",
                    "Use Noa as the host for stack-wide observer agents, without embedding analysis logic in Noa.",
                ],
            )
        )

    pyproject = path / "pyproject.toml"
    pyproject_text = pyproject.read_text(encoding="utf-8", errors="ignore").lower() if pyproject.exists() else ""
    if "name = \"galeed\"" in pyproject_text or "src/galeed" in _path_markers(path):
        surfaces.append(
            DiscoveredSurface(
                name=name,
                kind="trace_log_spine",
                path=str(path),
                evidence=["Galeed package layout or package metadata"],
                observer_actions=[
                    "Consume trace_events and llm_calls as primary live observation sources.",
                    "Preserve request_id/session_id/trace_id/plan_id/job_id for cross-project joins.",
                ],
            )
        )

    if "package.json" in files or "e2e" in dirs:
        surfaces.append(
            DiscoveredSurface(
                name=name,
                kind="ui_surface",
                path=str(path),
                evidence=[item for item in ("package.json", "e2e") if item in files or item in dirs],
                observer_actions=[
                    "Run Playwright-backed Cairn UI scenarios for human-load evidence.",
                    "Capture context switches, repair loops, missing information, and closure clarity.",
                ],
            )
        )

    if name.lower() == "hoglah" or "name = \"hoglah\"" in pyproject_text:
        surfaces.append(
            DiscoveredSurface(
                name=name,
                kind="llm_queue",
                path=str(path),
                evidence=["Hoglah package/name detected"],
                observer_actions=[
                    "Observe queue depth, retries, failures, model latency, and stalled jobs.",
                    "Join job_id to Galeed traces and Cairn process steps.",
                ],
            )
        )
    elif "hoglah" in pyproject_text:
        surfaces.append(
            DiscoveredSurface(
                name=name,
                kind="uses_llm_queue",
                path=str(path),
                evidence=["Hoglah dependency/reference detected"],
                observer_actions=[
                    "Observe model-call submissions, job ids, retries, and queue latency where this product uses Hoglah.",
                    "Join product events to Hoglah/Galeed correlation ids.",
                ],
            )
        )

    if name.lower() == "cairn" or (path / "docs" / "scenarios").exists():
        surfaces.append(
            DiscoveredSurface(
                name=name,
                kind="process_language",
                path=str(path),
                evidence=["Cairn repo or UI scenario docs detected"],
                observer_actions=[
                    "Use Cairn as the shared language for observer evidence, role-play, and annotations.",
                    "Run cairn-ui-pipeline and cairn-live-observe to generate reviewable artifacts.",
                ],
            )
        )

    return surfaces


def _observation_plan(surfaces: list[DiscoveredSurface]) -> list[str]:
    kinds = {surface.kind for surface in surfaces}
    plan = ["Create a small observation JSONL stream with source, kind, tags, duration_ms, and human_systems."]
    if "trace_log_spine" in kinds:
        plan.append("Bind Galeed trace/log events and LLM call records into the observation stream.")
    if "ui_surface" in kinds:
        plan.append("Author or run Playwright/Cairn UI scenarios for key human workflows.")
    if "llm_queue" in kinds:
        plan.append("Add queue-health observations for LLM jobs, retries, failures, and latency.")
    if "uses_llm_queue" in kinds:
        plan.append("Join product-level agent steps to Hoglah queue events and Galeed trace ids.")
    if "runtime_host" in kinds:
        plan.append("Run the observer from the runtime host so cross-project health and correlation keys are visible.")
    if "process_language" in kinds:
        plan.append("Generate Cairn evidence, role-play critique, and annotation snippets for review.")
    plan.append("Cluster repeated findings into product issues or process-improvement proposals.")
    return plan


def _path_markers(path: Path) -> str:
    markers: list[str] = []
    for rel in ("src/galeed", "src/cairn", "docs/scenarios"):
        if (path / rel).exists():
            markers.append(rel)
    return " ".join(markers)
