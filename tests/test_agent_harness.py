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
    assert not plan.open_questions
    assert cairn.build_agent_harness_plan is build_agent_harness_plan


def test_agent_harness_plan_marks_missing_evidence_as_questions():
    plan = build_agent_harness_plan(process_path="process.cairn.md")

    markdown = format_agent_harness_plan(plan)

    assert "Open Questions" in markdown
    assert "No UI simulation evidence was supplied" in markdown
    assert "cairn-human-factors process.cairn.md" in markdown


def test_agent_harness_plan_formats_shell_script():
    plan = build_agent_harness_plan(
        process_path="process.cairn.md",
        ui_evidence_path="ui.json",
        output_dir="out",
    )

    shell = format_agent_harness_plan(plan, output_format="shell")

    assert shell.startswith("#!/usr/bin/env bash\nset -euo pipefail")
    assert "mkdir -p out" in shell
    assert "cairn-validate process.cairn.md" in shell
    assert "cairn-generate-report" in shell
    assert "# Manual/agent step" in shell


def test_agent_harness_cli_writes_json(tmp_path):
    output = tmp_path / "plan.json"

    rc = harness_main(["--process", "p.cairn.md", "--ui-evidence", "ui.json", "-f", "json", "-o", str(output)])

    assert rc == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["steps"]
    assert any(step["name"] == "Generate review report" for step in payload["steps"])


def test_agent_harness_cli_writes_shell(tmp_path):
    output = tmp_path / "plan.sh"

    rc = harness_main(["--process", "p.cairn.md", "--ui-evidence", "ui.json", "-f", "shell", "-o", str(output)])

    assert rc == 0
    assert output.read_text(encoding="utf-8").startswith("#!/usr/bin/env bash")
