"""One-command pipeline for Cairn UI simulation evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cairn.llm_adapters import CommandLLMProvider, HoglahLLMProvider
from cairn.ui_evidence import (
    analyze_ui_simulation_report,
    format_cairn_annotation_snippet,
    format_ui_human_load_report,
    interpret_ui_experience,
)
from cairn.ui_scenarios import load_ui_scenario
from cairn.ui_sim_cli import main as ui_sim_main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cairn-ui-pipeline",
        description="Run the UI simulation pipeline: validate, simulate, evidence, annotations, optional role-play.",
    )
    parser.add_argument("scenario", help="Path to a JSON UI simulation scenario")
    parser.add_argument("--project-root", default=".", help="Project root whose node_modules include Playwright")
    parser.add_argument("--base-url", help="Override scenario baseUrl")
    parser.add_argument("--from-report", help="Use an existing cairn-ui-sim report instead of running Playwright")
    parser.add_argument("--report-output", help="Write or read the UI simulation report at this path")
    parser.add_argument("--evidence-output", help="Write Markdown evidence summary to this path")
    parser.add_argument("--annotations-output", help="Write Cairn annotation snippet to this path")
    parser.add_argument("--roleplay-output", help="Write optional LLM role-play Markdown to this path")
    parser.add_argument("--step-title", help="Heading to use for the generated Cairn annotation snippet")
    parser.add_argument("--persona", action="append", default=[], help="Persona/perspective to simulate; repeatable")
    parser.add_argument("--cairn-source", help="Optional Cairn source file to include as role-play context")
    parser.add_argument("--llm-command", help="Optional command LLM provider for role-play")
    parser.add_argument("--hoglah-model", help="Optional Hoglah-backed provider model name for role-play")
    parser.add_argument("--hoglah-real", action="store_true", help="Use Hoglah's real adapter instead of its safe stub")
    parser.add_argument("--llm-timeout", type=int, default=120, help="Timeout in seconds for the LLM provider")
    parser.add_argument("--headed", action="store_true", help="Run browser headed instead of headless")
    parser.add_argument("--timeout", type=int, default=30000, help="Default browser action timeout in ms")
    args = parser.parse_args(argv)

    if args.llm_command and args.hoglah_model:
        parser.error("choose either --llm-command or --hoglah-model, not both")

    scenario_path = Path(args.scenario).resolve()
    scenario = load_ui_scenario(scenario_path)
    report_path = Path(args.from_report).resolve() if args.from_report else _resolve_report_path(args, scenario_path, scenario)

    if not args.from_report:
        sim_args = [
            str(scenario_path),
            "--project-root",
            args.project_root,
            "--output",
            str(report_path),
            "--timeout",
            str(args.timeout),
        ]
        if args.base_url:
            sim_args.extend(["--base-url", args.base_url])
        if args.headed:
            sim_args.append("--headed")
        rc = ui_sim_main(sim_args)
        if rc != 0:
            return rc

    raw_report = json.loads(report_path.read_text(encoding="utf-8"))
    evidence = analyze_ui_simulation_report(raw_report)
    outputs = _default_outputs(report_path)
    evidence_path = Path(args.evidence_output).resolve() if args.evidence_output else outputs["evidence"]
    annotations_path = Path(args.annotations_output).resolve() if args.annotations_output else outputs["annotations"]

    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(format_ui_human_load_report(evidence), encoding="utf-8")

    annotations_path.parent.mkdir(parents=True, exist_ok=True)
    annotations_path.write_text(
        format_cairn_annotation_snippet(evidence, step_title=args.step_title),
        encoding="utf-8",
    )

    roleplay_path = None
    if args.llm_command or args.hoglah_model:
        roleplay_path = Path(args.roleplay_output).resolve() if args.roleplay_output else outputs["roleplay"]
        cairn_source = Path(args.cairn_source).read_text(encoding="utf-8") if args.cairn_source else None
        if args.llm_command:
            provider = CommandLLMProvider(args.llm_command, timeout=args.llm_timeout)
        else:
            provider = HoglahLLMProvider(model=args.hoglah_model, use_real=args.hoglah_real, timeout=args.llm_timeout)
        interpretation = interpret_ui_experience(
            raw_report,
            provider,
            evidence=evidence,
            personas=args.persona or None,
            cairn_source=cairn_source,
        )
        roleplay_path.parent.mkdir(parents=True, exist_ok=True)
        roleplay_path.write_text(interpretation.text, encoding="utf-8")

    print(f"report: {report_path}")
    print(f"evidence: {evidence_path}")
    print(f"annotations: {annotations_path}")
    if roleplay_path:
        print(f"roleplay: {roleplay_path}")
    return 0


def _resolve_report_path(args: argparse.Namespace, scenario_path: Path, scenario: dict) -> Path:
    if args.report_output:
        return Path(args.report_output).resolve()
    output = scenario.get("output") or "../analysis/ui-sim-report.json"
    output_path = Path(output)
    return output_path if output_path.is_absolute() else (scenario_path.parent / output_path).resolve()


def _default_outputs(report_path: Path) -> dict[str, Path]:
    name = report_path.name
    suffix = "-ui-sim-report.json"
    base = name[: -len(suffix)] if name.endswith(suffix) else report_path.stem
    return {
        "evidence": report_path.with_name(f"{base}-ui-evidence.md"),
        "annotations": report_path.with_name(f"{base}-ui-annotations.cairn.md"),
        "roleplay": report_path.with_name(f"{base}-ui-roleplay.md"),
    }


if __name__ == "__main__":
    raise SystemExit(main())
