from __future__ import annotations

import json
from pathlib import Path

import sys

from cairn.llm_adapters import LLMRequest, LLMResponse
from cairn.ui_evidence import (
    analyze_ui_simulation_report,
    build_ui_roleplay_prompt,
    format_ui_human_load_report,
    interpret_ui_experience,
)
from cairn.ui_evidence_cli import main as ui_evidence_main
from cairn.ui_roleplay_cli import main as ui_roleplay_main


ROOT = Path(__file__).resolve().parents[1]


def test_ui_simulation_report_becomes_human_load_evidence():
    raw = json.loads((ROOT / "docs" / "analysis" / "mahlah-ui-sim-report.json").read_text(encoding="utf-8"))
    report = analyze_ui_simulation_report(raw)

    assert report.scenario == "mahlah-human-load"
    assert report.metrics["contextSwitches"] == 3
    factors = {(finding.family, finding.factor) for finding in report.findings}
    assert ("cognitive_load", "context switching") in factors
    assert ("organisational_change", "feedback capture burden") in factors
    assert report.risk is not None
    assert report.risk.score == "significant"
    assert "HUMAN_DEMAND" in report.suggested_blocks
    assert "HUMAN_LOAD" in report.suggested_blocks
    assert "context_switches: 3" in report.suggested_blocks["HUMAN_LOAD"]


def test_format_ui_human_load_report_markdown_and_json():
    raw = json.loads((ROOT / "docs" / "analysis" / "mahlah-ui-sim-report.json").read_text(encoding="utf-8"))
    report = analyze_ui_simulation_report(raw)

    markdown = format_ui_human_load_report(report)
    assert "UI Human-Load Evidence" in markdown
    assert "context switching" in markdown

    payload = format_ui_human_load_report(report, output_format="json")
    assert isinstance(payload, dict)
    assert payload["suggested_blocks"]["HUMAN_LOAD"]


def test_ui_evidence_cli_writes_markdown(tmp_path):
    source = ROOT / "docs" / "analysis" / "mahlah-ui-sim-report.json"
    output = tmp_path / "ui-evidence.md"
    rc = ui_evidence_main([str(source), "-o", str(output)])

    assert rc == 0
    text = output.read_text(encoding="utf-8")
    assert "Suggested Cairn Blocks" in text
    assert "HUMAN_RISK" in text


class FakeRoleplayProvider:
    name = "fake-roleplay"

    def complete(self, request: LLMRequest) -> LLMResponse:
        assert request.task == "cairn.ui_experience.roleplay"
        assert "ui_evidence" in request.context
        assert "novice" in request.prompt
        return LLMResponse(
            text="## Role-play snapshots\n\nThe novice user loses context at the dev log.",
            provider=self.name,
        )


def test_interpret_ui_experience_uses_provider():
    raw = json.loads((ROOT / "docs" / "analysis" / "mahlah-ui-sim-report.json").read_text(encoding="utf-8"))
    evidence = analyze_ui_simulation_report(raw)
    prompt = build_ui_roleplay_prompt(raw, evidence, personas=["novice reviewer"])
    assert "not a real user study" in prompt
    assert "novice reviewer" in prompt

    interpretation = interpret_ui_experience(raw, FakeRoleplayProvider(), evidence=evidence)
    assert interpretation.provider == "fake-roleplay"
    assert "novice user" in interpretation.personas[0]
    assert "dev log" in interpretation.text


def test_ui_roleplay_cli_command_provider(tmp_path):
    script = tmp_path / "fake_roleplay.py"
    script.write_text(
        "import json, sys\n"
        "payload = json.load(sys.stdin)\n"
        "assert payload['task'] == 'cairn.ui_experience.roleplay'\n"
        "assert 'ui_evidence' in payload['context']\n"
        "print(json.dumps({'text': 'Roleplay OK: ' + payload['context']['ui_evidence']['scenario']}))\n",
        encoding="utf-8",
    )
    source = ROOT / "docs" / "analysis" / "mahlah-ui-sim-report.json"
    output = tmp_path / "roleplay.md"
    rc = ui_roleplay_main([str(source), "--llm-command", f"{sys.executable} {script}", "-o", str(output)])

    assert rc == 0
    assert output.read_text(encoding="utf-8") == "Roleplay OK: mahlah-human-load"
