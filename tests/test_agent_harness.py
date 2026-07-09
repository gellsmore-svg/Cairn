from __future__ import annotations

import json

import cairn
from cairn.agent_harness import build_agent_harness_plan, format_agent_harness_plan
from cairn.agent_harness_cli import main as harness_main


def test_agent_harness_plan_includes_available_deterministic_steps():
    plan = build_agent_harness_plan(
        process_path="process.cairn.md",
        ui_evidence_path="ui report.json",
        layout_path="layout.json",
        output_dir="out dir",
    )

    commands = [step.command for step in plan.steps if step.command]

    assert any(command == "cairn-validate process.cairn.md" for command in commands)
    assert any("cairn-human-factors process.cairn.md" in command for command in commands)
    assert any("cairn-ui-evidence 'ui report.json'" in command for command in commands)
    assert any("cairn-layout-load layout.json" in command for command in commands)
    assert any("cairn-generate-report" in command for command in commands)
    assert plan.inputs["process"] == "process.cairn.md"
    assert not plan.open_questions
    assert any("awareness, orientation, execution" in check for check in plan.review_checks)
    assert any("functional layout load" in check.lower() for check in plan.review_checks)
    assert cairn.build_agent_harness_plan is build_agent_harness_plan


def test_agent_harness_plan_marks_missing_evidence_as_questions():
    plan = build_agent_harness_plan(process_path="process.cairn.md")

    markdown = format_agent_harness_plan(plan)

    assert "Open Questions" in markdown
    assert "No UI simulation evidence was supplied" in markdown
    assert "Agent Review Checklist" in markdown
    assert "Treat UI claims as inferential" in markdown
    assert "cairn-human-factors process.cairn.md" in markdown


def test_agent_harness_plan_formats_shell_script():
    plan = build_agent_harness_plan(
        process_path="process.cairn.md",
        ui_evidence_path="ui.json",
        output_dir="out",
    )

    shell = format_agent_harness_plan(plan, output_format="shell")

    assert shell.startswith("#!/usr/bin/env bash\nset -euo pipefail")
    assert "require_path process.cairn.md" in shell
    assert "mkdir -p out" in shell
    assert "cairn-validate process.cairn.md" in shell
    assert "cairn-generate-report" in shell
    assert "# Manual/agent step" in shell
    assert "# Agent review checklist:" in shell
    assert "challenge, reject, defer, and override paths" in shell


def test_agent_harness_plan_tracks_repo_screenshots_and_missing_inputs(tmp_path):
    process = tmp_path / "process.cairn.md"
    screenshot = tmp_path / "screen.png"
    process.write_text("PROCESS — Demo.\n", encoding="utf-8")
    screenshot.write_text("png-ish", encoding="utf-8")

    plan = build_agent_harness_plan(
        process_path=str(process),
        repository_path="https://example.test/repo.git",
        screenshot_paths=[str(screenshot), str(tmp_path / "missing.png")],
        check_paths=True,
    )

    assert plan.inputs["repository"] == "https://example.test/repo.git"
    assert plan.inputs["screenshots"] == [str(screenshot), str(tmp_path / "missing.png")]
    assert plan.missing_inputs == [str(tmp_path / "missing.png")]
    markdown = format_agent_harness_plan(plan)
    assert "Inspect repository surfaces" in markdown
    assert "Review screenshots" in markdown
    assert "Missing Inputs" in markdown


def test_agent_harness_cli_writes_json(tmp_path):
    output = tmp_path / "plan.json"

    rc = harness_main(["--process", "p.cairn.md", "--ui-evidence", "ui.json", "-f", "json", "-o", str(output)])

    assert rc == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["steps"]
    assert any(step["name"] == "Generate review report" for step in payload["steps"])
    assert payload["inputs"]["process"] == "p.cairn.md"
    assert any("business work from interface overhead" in check for check in payload["review_checks"])


def test_agent_harness_cli_checks_files(tmp_path):
    output = tmp_path / "plan.json"

    rc = harness_main(["--process", str(tmp_path / "missing.cairn.md"), "--check-files", "-f", "json", "-o", str(output)])

    assert rc == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["missing_inputs"] == [str(tmp_path / "missing.cairn.md")]


def test_agent_harness_cli_can_fail_on_missing_after_writing_plan(tmp_path):
    output = tmp_path / "plan.json"

    rc = harness_main(
        [
            "--process",
            str(tmp_path / "missing.cairn.md"),
            "--check-files",
            "--fail-on-missing",
            "-f",
            "json",
            "-o",
            str(output),
        ]
    )

    assert rc == 2
    assert output.exists()


def test_agent_harness_fail_on_missing_implies_file_check(tmp_path):
    output = tmp_path / "plan.json"

    rc = harness_main(
        [
            "--process",
            str(tmp_path / "missing.cairn.md"),
            "--fail-on-missing",
            "-f",
            "json",
            "-o",
            str(output),
        ]
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert rc == 2
    assert payload["missing_inputs"] == [str(tmp_path / "missing.cairn.md")]


def test_agent_harness_cli_writes_shell(tmp_path):
    output = tmp_path / "plan.sh"

    rc = harness_main(["--process", "p.cairn.md", "--ui-evidence", "ui.json", "-f", "shell", "-o", str(output)])

    assert rc == 0
    assert output.read_text(encoding="utf-8").startswith("#!/usr/bin/env bash")
